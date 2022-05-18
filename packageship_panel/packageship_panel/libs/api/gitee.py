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
"""
Call gitee api to parse the spec to get the source package name and version,
and get all the packages under src-openeuler
"""
import os
import base64
import json
from packageship.libs.conf import configuration
from packageship.application.common.remote import AsyncRequest
from packageship.libs.log import LOGGER
from pyrpm.spec import Spec, replace_macros


class GiteeApi:
    """
    Call gitee api to parse the spec to get the source package name and version,
    and get all the packages under src-openeuler
    """

    def __init__(self, token=None) -> None:
        """
        Initialize the properties of the class
        Args:
            token: gitee token
        """
        self.token = token or configuration.GIT_TOKEN or os.getenv("GIT_TOKEN")
        if not self.token:
            raise RuntimeError("The gitee token has not been obtained, "
                               "please check the environment variable settings")
        self.all_src_url = "https://gitee.com/api/v5/enterprises/open_euler/repos"
        self.content_tree_url = None

    @staticmethod
    def base_decrypt(content):
        """
        base64 decrypt spec content
        Args:
            content: spec content

        Returns:
            name: src package name
            version: src version version
        """
        # base 64 decrypt the contents of the spec
        name, version = None, None
        content = base64.b64decode(content).decode("utf-8")
        try:
            spec = Spec.from_string(content)
        except AttributeError as error:
            LOGGER.error(f"error parsing spec content {error}")
            return name, version
        name = replace_macros(spec.name, spec)
        version = replace_macros(spec.version, spec)
        return name, version

    async def all_src_repo(self, page, per_page=100):
        """
        Get all repositories under the src-openeuler organization
        Args:
            page : page number
            per_page : page size

        Returns:
            all_packages: All repo names on the current page
            total_page: total pages
        """
        all_packages = []
        params = {
            "access_token": self.token,
            "type": "public",
            "page": page,
            "per_page": per_page,
        }
        response = await AsyncRequest.get(url=self.all_src_url, params=params)
        if not all([response.success, response.json]):
            LOGGER.error(f"getting the repo name failed because {response.json}")
            return all_packages, 1
        for content in response.json:
            if content.get("namespace").get("path") == "src-openeuler":
                all_packages.append(content.get("path"))
        return all_packages, int(response.headers.get("total_page", 1))

    async def get_sepc_content(self, spec_url):
        """
        get the contents of the spec
        Args:
            spec_url: spec url

        Returns:
            name: src package name
            vers: src package version
        """
        name, vers = (None, None)
        params = {"access_token": self.token}
        response = await AsyncRequest.get(url=spec_url, params=params)
        if not all([response.success, response.json]):
            LOGGER.error(f"failed to get contents of spec because {response.json}")
            return name, vers
        return self.base_decrypt(response.json.get("content"))

    async def src_repo_spec(self, repo, owner="src-openeuler", sha="master"):
        """
        src repo spec url
        Args:
            repo:  repo name
            owner: organize defaults to src-openeuler
            sha: sha

        Returns:
            name: src name
            vers: package vers
        """
        name, vers = (None, None)
        self.content_tree_url = (
            f"https://gitee.com/api/v5/repos/{owner}/{repo}/git/trees/{sha}"
        )
        params = {"access_token": self.token}

        response = await AsyncRequest.get(url=self.content_tree_url, params=params)
        if not all([response.success, response.json]):
            LOGGER.error(f"failed src repo spec url because {response.json}")
            return name, vers
        spec = [content for content in response.json.get("tree") if content.get("path").endswith(".spec")]
        if spec:
            name, vers = await self.get_sepc_content(spec[0].get("url"))
        return name, vers

    async def get_sig_info(self, community="openeuler", sigs=None):
        """
        Call the om interface to get the sig group information
        Args:
            community: community defaults to openeuler
            sigs: Get the specified sig information, the default is none, get all sig information
        Returns:
            sig_infos: a list of sig infos
        """
        url = "https://omapi.osinfra.cn/query/sigDetails"
        response = await AsyncRequest.post(url=url, data=json.dumps(dict(sigs=sigs, community=community)))
        sig_infos = response.json
        if not all([response.success, response.json]) or sig_infos["code"] != 200:
            LOGGER.error("failed to get sig infos,")
            return []
        return sig_infos["data"]
