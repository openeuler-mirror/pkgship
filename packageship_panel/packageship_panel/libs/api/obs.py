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
Call obs api to analyze the compilation status of the main project and the software packages under the project
"""
import os
import json
import aiohttp
from lxml import etree
from lxml.etree import ParseError
from requests import RequestException
from requests.auth import HTTPBasicAuth
import requests
from packageship.libs.log import LOGGER
from packageship.libs.conf import configuration
from packageship.application.common.remote import AsyncRequest


class ObsApi:
    """
    Class initialization and assigning properties
    """
    def __init__(self, account=None, password=None) -> None:
        """
        Class initialization and assigning properties
        Args:
            account: account
            password: password
        """
        self.host = configuration.OBS_HOST
        self._account = account or configuration.OBS_ACCOUNT or os.getenv(
            "OBS_ACCOUNT")
        self._password = password or configuration.OBS_PASSWORD or os.getenv(
            "OBS_PASSWORD")
        self.architectures = {
            "standard_aarch64": "aarch64",
            "standard_x86_64": "x86_64",
        }
        self.obs_states = list()
        if not all([self.host, self._account, self._password]):
            raise RuntimeError(
                "Please check whether the path, account and password of obs are fully configured"
            )

    @property
    def _auth(self):
        """
        User Authentication
        Returns:
           BasicAuth of aiohttp
        """
        return aiohttp.BasicAuth(login=self._account,
                                 password=self._password,
                                 encoding="utf-8")

    @property
    def _auth_basic(self):
        obs_auth = HTTPBasicAuth(self._account, self._password)
        return obs_auth

    @staticmethod
    def _xpath(xpath, node, choice=False):
        """
        Parse xml node
        Args:
            xpath: label element
            node: node object
            choice: True or False

        Returns:
            If choice is true, return all elements located, otherwise return the first one
        """
        element_result = node.xpath(xpath)
        if element_result:
            return element_result if choice else element_result[0]
        return element_result

    @staticmethod
    def _parse_arch_state(state):
        """
        Parse the compilation status of the project
        Args:
            state:  project state

        Returns:
            arch_state: arch_state
        """

        arch_state = "published"
        for repository_state in list(set(state)):
            if repository_state != "published":
                return repository_state
        return arch_state

    @staticmethod
    def _etree_obj(xml_result):
        """
        The object that instantiates the etree
        Args:
            xml_result: xml result

        Returns:
            etree_element: etree object
        """
        etree_element = None
        try:
            etree_element = etree.HTML(xml_result)
        except (ParseError, ValueError):
            LOGGER.error("Error parsing lxml node")
            return etree_element
        return etree_element

    async def get_project_status(self, project):
        """
        Call the obs api to get the compilation status of the project
        Args:
            project: project name

        Returns:
            obs_information: obs package build state
        """
        url = self._url(url="build/{project}/_result", project=project)
        response = await AsyncRequest.get(url, auth=self._auth)
        if not all([response.success, response.text]):
            LOGGER.error("failed to get project compilation status")
            return []
        obs_information = self._parse_all_projects(response.text, project)
        return obs_information

    async def main_project(self):
        """
        Get obs main project
        Returns:
            main projects
        """
        url = self._url(url="/project")
        response = await AsyncRequest.get(url, auth=self._auth)
        if not all([response.success, response.text]):
            LOGGER.error("failed to get main project")
            return []

        return self._parse_main_project(response.text)

    def get_project_state(self, project):
        url = self._url(url="build/{project}/_result?view=summary",
                        project=project)
        project_state = "building"
        try:
            response = requests.get(url=url, auth=self._auth_basic)
            if response.status_code != 200 or not response.text:
                LOGGER.error("failed to get project compilation status")
                return project_state
            project_state = self._parse_project_state(response.text)
            return project_state
        except (RequestException, AttributeError) as e:
            LOGGER.error(f"failed to get project compilation status,{e}")
            return project_state

    async def get_complete_packages(self,
                                    project,
                                    limit=5,
                                    community="openeuler"):
        """
        get the information of the successfully compiled package
        Args:
            project: project
            limit: limit
            community: community

        Returns:
            package build info
        """
        url = f"https://omapi.osinfra.cn/query/obsDetails?community={community}&branch={project}&limit={limit}"
        response = await AsyncRequest.get(url)
        build_complete_packages = response.json
        if (not all([response.success, response.json])
                or build_complete_packages["code"] != 200):
            LOGGER.error("failed to get complete packages")
            return dict()
        return {
            pkg["repo_name"] + "_standard_" + pkg["architecture"]: pkg
            for pkg in build_complete_packages["data"]
        }

    async def get_iso_infos(self,
                            branchs=None,
                            limit=1,
                            community="openeuler"):
        """
        get iso  construct info
        Args:
            branchs: branch name
            limit: limit
            community: community

        Returns:
            iso_infos: build iso result
        """
        url = f"https://omapi.osinfra.cn/query/isoBuildTimes"
        response = await AsyncRequest.post(
            url,
            data=json.dumps(
                dict(community=community, limit=limit, branchs=branchs)),
        )
        iso_infos = response.json
        if not all([response.success, response.json
                    ]) or iso_infos["code"] != 200:
            LOGGER.error("failed to get iso infos")
            return []
        return iso_infos["data"]

    def _url(self, url, **kwargs):
        """
        Splicing of obs routing
        Args:
            url: url
            **kwargs: kwargs

        Returns:
            spliced obs route
        """
        return self.host + url.format(**kwargs)

    def _parse_all_projects(self, xml_result, project_name):
        """
        Parse the compilation status of all packages under the project
        Args:
            xml_result: xml result
            project_name: project name

        Returns:
            obs_info: build results of all packages under a project
        """
        obs_info = list()
        etree_element = self._etree_obj(xml_result)
        if etree_element is None:
            return obs_info
        state = self._xpath(xpath="//@state", node=etree_element, choice=True)
        self.obs_states.append(
            [project_name, self._parse_arch_state(state[1:])])
        for _result in self._xpath(xpath="//result",
                                   node=etree_element,
                                   choice=True):
            for status in self._xpath(xpath="./status",
                                      node=_result,
                                      choice=True):
                build_requires = list()
                if self._xpath(xpath="./@code", node=status) == "unresolvable":
                    build_unresolvable = self._xpath(xpath="./details/text()",
                                                     node=status)
                    if build_unresolvable:
                        for provides in build_unresolvable.split(","):
                            build_requires.append(
                                provides.replace("nothing provides",
                                                 "").strip())
                pkgs = dict(
                    architecture=self._xpath(xpath="./@repository",
                                             node=_result),
                    repo_name=self._xpath(xpath="./@package", node=status),
                    build_status=self._xpath(xpath="./@code", node=status),
                    obs_branch=project_name,
                    build_requires=build_requires,
                )
                obs_info.append(pkgs)
        return obs_info

    def _parse_main_project(self, main_project_xml):
        """
        parse main project
        Args:
            main_project_xml: main project xml

        Returns:
            projects: all main project
        """
        projects = list()
        etree_element = self._etree_obj(main_project_xml)
        if etree_element is None:
            return projects
        projects = [
            self._xpath(xpath="./td[1]/a/text()", node=tr) for tr in
            self._xpath(xpath='//div[@class="table-responsive"]//tbody/tr',
                        node=etree_element,
                        choice=True)
        ]
        return projects

    def _parse_project_state(self, xml_result):
        project_state = "building"
        try:
            etree_element = self._etree_obj(xml_result)
            if etree_element is None:
                return project_state
            state = self._xpath(xpath="//@state",
                                node=etree_element,
                                choice=True)
            project_state = self._parse_arch_state(state[1:])
        except IndexError as error:
            LOGGER.error(error)
        return project_state
