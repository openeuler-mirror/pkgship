#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2020-2020. All rights reserved.
# licensed under the Mulan PSL v2.
# You can use this software according to the terms and conditions of the Mulan PSL v2.
# You may obtain a copy of Mulan PSL v2 at:
#     http://license.coscl.org.cn/MulanPSL2
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR
# PURPOSE.
# See the Mulan PSL v2 for more details.
# ******************************************************************************/
import json
import os
import stat

import requests
import retrying
import yaml
from lxml import etree
from packageship.application.common.constant import MAX_RETRY
from packageship.application.common.remote import RemoteService
from packageship.application.initialize.integration import InitializeService
from packageship.libs.conf import configuration
from packageship.libs.log import LOGGER
from retrying import retry

OPENEULER_REPO = "https://repo.openeuler.org"
RELEASE_MANAGE = (
    "https://gitee.com/openeuler/release-management/raw/master/release-management.yaml"
)


@retry(retry_on_result=lambda result: result is None, stop_max_attempt_number=MAX_RETRY)
def read_release_management_yaml():
    """
    Read the release version
    """
    request = RemoteService()
    request.request(RELEASE_MANAGE, "get")
    if request.status_code != requests.codes["ok"]:
        return None
    try:
        release_management = yaml.safe_load(request.text)
        return release_management
    except yaml.YAMLError:
        raise ValueError(
            "The file format is incorrect. It is not the correct YAML file."
        )


def src_db_path(branch):
    return f"{OPENEULER_REPO}/{branch}/source".strip()


def bin_db_path(branch):
    return f"{OPENEULER_REPO}/{branch}/everything/aarch64".strip()


def _write_conf_repo(conf_yaml, repos):
    try:
        flags = os.O_RDWR | os.O_CREAT
        modes = stat.S_IWUSR | stat.S_IRUSR
        with os.fdopen(os.open(conf_yaml, flags, modes), "w", encoding="utf-8") as file:
            yaml.dump(data=repos, stream=file)
    except yaml.YAMLError:
        LOGGER.error(
            "There was an error writing dynamically to the YAML configuration file."
        )


@retry(retry_on_result=lambda result: result is None, stop_max_attempt_number=MAX_RETRY)
def _release_repo():
    request = RemoteService()
    request.request(url=OPENEULER_REPO, method="get")
    if request.status_code != requests.codes["ok"]:
        return None
    try:
        html = etree.HTML(request.text)
        release_repos = [
            repo for repo in html.xpath("//*[@id='list']/tbody/tr/td[1]/a/@title")
        ]
        return release_repos
    except AttributeError:
        LOGGER.warning(
            f"The requested page content is incorrect: {OPENEULER_REPO}.")
        return None


def _get_multi_version_repo(branch):
    """
    Judge whether there is multi in the current branch_ Version, and add it to the repo list if it exists.
    """
    open_stack_repo_url = f"https://repo.openeuler.org/{branch}/EPOL/multi_version/OpenStack"
    request = RemoteService()
    request.request(url=open_stack_repo_url, method="get")
    if request.status_code != requests.codes["OK"]:
        return []

    open_stack_repo_name = "https://repo.openeuler.org/{branch}/EPOL/multi_version/OpenStack/{version}"
    open_stack_versions = ["Train", "Wallaby"]
    open_stack_repo_list = []
    for version in open_stack_versions:
        open_stack_repo_list.append(
            {
                "dbname": "-".join([branch, "OpenStack", version]).lower(),
                "src_db_file": open_stack_repo_name.format(branch=branch, version=version) + "/source",
                "bin_db_file": open_stack_repo_name.format(branch=branch, version=version) + "/aarch64"
            }
        )
    return open_stack_repo_list


def _get_additional_repo():
    """
    Obtain the repo that needs to be added additionally
    The repo configuration file is trigger_timer_additional_repo.json
    """
    current_path = os.path.dirname(os.path.realpath(__file__))
    additional_repo_file = os.path.join(
        current_path, "trigger_timer_additional_repo.json")
    additional_repo_list = []
    with open(additional_repo_file, "r") as repo_file:
        try:
            additional_repo_list = json.load(repo_file)
        except json.JSONDecodeError as error:
            LOGGER.error(
                f"Failed to parse file trigger_timer_additional_repo.json, message: {error}")
            return []

    return additional_repo_list


def _add_repo_priority(repo_list):
    """
    Add priority to the generated repo configuration
    """
    for index, repo in enumerate(repo_list):
        repo["priority"] = index + 1


def create_conf_yaml(conf_yaml):
    try:
        release_management = read_release_management_yaml()
        release_repos = _release_repo()
    except (retrying.RetryError, ValueError) as error:
        LOGGER.error(f"Failed to dynamically update data,errors: {error}")
        return
    repos = list()
    right_release_repo = list(
        set(release_repos).intersection(
            set(
                [
                    release.get("branch")
                    for release in release_management.get("release", list())
                ]
            )
        )
    )
    for release_branch in sorted(right_release_repo, reverse=True):
        repos.append(
            {
                "dbname": release_branch.lower(),
                "src_db_file": src_db_path(release_branch),
                "bin_db_file": bin_db_path(release_branch)
            }
        )
        repos.extend(_get_multi_version_repo(branch=release_branch))

    repos.extend(_get_additional_repo())
    _add_repo_priority(repos)
    _write_conf_repo(conf_yaml, repos)


def initizlize_release_repo():
    """
    Initialize the source of the release
    """
    conf_yaml = os.path.join(
        configuration.TEMPORARY_DIRECTORY, "release-management.yaml"
    )
    os.makedirs(configuration.TEMPORARY_DIRECTORY, exist_ok=True)
    create_conf_yaml(conf_yaml)
    if not os.path.exists(conf_yaml):
        LOGGER.error("Failed to create the repo configuration file.")
        return
    initialize = InitializeService()
    initialize.import_depend(path=conf_yaml)
    if initialize.success:
        LOGGER.info(
            "The published repo has been dynamically updated successfully.")
    else:
        LOGGER.error("The published repo update failed.")
    if initialize.remove_error:
        for _, message in initialize.remove_error.items():
            LOGGER.warning(message)
    if initialize.reindex_error:
        for reindex_error in initialize.reindex_error:
            LOGGER.warning(reindex_error["message"])
            LOGGER.warning("Reindex failed: %s" % reindex_error["reindex"])
            LOGGER.warning(
                "Please manually delete the following databases: %s"
                % " ".join(reindex_error["del_index"])
            )


if __name__ == "__main__":
    initizlize_release_repo()
