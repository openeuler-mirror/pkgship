# !/usr/bin/python3
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
Obs data information
"""
import math
import os

from packageship.application.common.constant import BUILD_TIME_LEVEL
from packageship.application.common.constant import DEFAULT_GIT_BRANCH
from packageship.application.common.constant import DEFAULT_PAGE_SIZE
from packageship.application.common.constant import EXPORT_ISO_ROW
from packageship.application.common.constant import EXPORT_ISO_COLUMN
from packageship.application.common.constant import EXPORT_BUILD_STATE_COLUMN
from packageship.application.common.constant import EXPORT_BUILD_TIME_COLUMN
from packageship.application.common.constant import OBS_PACKAGE_INFO_COLUMN
from packageship.application.common.constant import OBS_A_ARCHITECTURE
from packageship_panel.application.core import ExportBase
from packageship_panel.application.query.panel import PanelInfo

from packageship.application.common.constant import BUILD_STATES
from packageship.libs.log import LOGGER


class ObsInfo(ExportBase):
    """Obs data information"""

    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.gitee_branch = kwargs.get("gitee_branch") or DEFAULT_GIT_BRANCH
        self.architecture = kwargs.get("architecture") or OBS_A_ARCHITECTURE
        self.pkg_name = kwargs.get("pkg_name")
        self.build_state = kwargs.get("build_state")
        self.sig_name = kwargs.get("sig_name")
        self.maintainers = kwargs.get("maintainers")
        self.orders = kwargs.get("orders")
        self.page_index = kwargs.get("page_index") or -1
        self.page_size = kwargs.get("page_size") or DEFAULT_PAGE_SIZE
        self._panel_info = PanelInfo()

    @staticmethod
    def _seconds_to_min(build_time):
        """
        Convert seconds to minute
        Args:
            build_time: build time is seconds
        Returns:
            converted time
        """
        if isinstance(build_time, list):
            return (
                [round(int(number) / 60, 2) for number in build_time]
                if build_time
                else build_time
            )
        return round(int(build_time) / 60, 2) if build_time else build_time

    @staticmethod
    def _csv_build_data(obs_build_infos, obs_build_constants):
        """
        Package compilation time statistics
        Args:
            obs_build_infos: obs build infos
            obs_build_constants: obs build constant
        Returns:
            pkg_builds_time: pkg builds time list
        """
        return [
            obs_build_infos.get(obs_build_constant)
            for obs_build_constant in obs_build_constants
        ]

    @staticmethod
    def _iso_success_rate(iso_info_count):
        """
        Calculate the success rate of iso
        Args:
            iso_info_count: iso_info_count

        Returns:
            iso_success_rate: iso_success_rate
        """

        iso_success_rate = "{:.2f}%".format(iso_info_count / 30 * 100)
        return iso_success_rate

    def export_obs_info_csv(self):
        """
        Export OBS information in CSV format
        """
        # Create a temporary folder
        self.create_folder_path()
        obs_file_path = os.path.join(self.folder_path, "obs.csv")
        self.copy_file(self._template_csv_path("obs_info_template.csv"), obs_file_path)
        # Read csv data from template file
        self.cve_content_list(obs_file_path)
        # Query obs information
        obs_infos = self.get_obs_infos()
        # process obs information to csv_list
        self._process_obs_data(obs_infos)
        self.list_save_csv(obs_file_path)
        return self.folder_path

    def suggest_branch(self, query=None):
        """
        Query the OBS build page gitee branch suggestion list
        :param query: Fuzzy search  gitee branch
        :return: gitee branch list
        """
        body = {"gitee_branch": query}
        query_all = False if query else True
        branchs = self._panel_info.query_suggest_info(
            index="branch_info", body=body, query_all=query_all
        )
        return [branch_info["gitee_branch"] for branch_info in branchs]

    def suggest_pkg(self, query):
        """
        Query the recommended software package list on the OBS build page
        Args:
            query: Fuzzy search package name
        Returns:
            List of matched source packages
        """
        body = {"repo_name": query}
        query_all = False if query else True
        packages = self._panel_info.query_suggest_info(
            index="obs_info", body=body, query_all=query_all
        )
        return [package["repo_name"] for package in packages]

    def suggest_sig(self, query=None):
        """
        Query the OBS build page sig info suggestion list
        Args:
            query: Fuzzy search  sig info
        Returns:
            sig info  list
        """
        body = {"name": query}
        query_all = False if query else True
        sigs = self._panel_info.query_suggest_info(
            index="sig_info", body=body, query_all=query_all
        )
        return [sig["name"] for sig in sigs]

    def get_obs_infos(self):
        """
        Get OBS information
        Args:

        Returns:
            all obs info
        """
        # Query obs information
        update_obs_infos = self._obs_infos(
            page_size=self.page_size, page=self.page_index
        )
        total_count, total_page = self._total_page()
        # obs compile state data
        build_states = self._panel_info.query_build_states(
            branch=self.gitee_branch, architecture=self.architecture
        )
        # obs compile time data
        build_times = self._panel_info.query_build_times(
            branch=self.gitee_branch, architecture=self.architecture
        )
        # query iso compilation time data
        iso_info_ten, iso_success_rate = self._iso_build_data()
        return dict(
            pkg_infos=update_obs_infos,
            pkg_build_states=build_states,
            pkg_build_times=build_times,
            iso_info=iso_info_ten,
            total_count=total_count,
            total_page=total_page,
            iso_success_rate=iso_success_rate,
        )

    def _obs_infos(self, page_size=DEFAULT_PAGE_SIZE, page=-1):
        """
        Assemble query conditions to query obs information
        Args:
            page_size: amount displayed per page
            page: page number

        Returns:
            obs_infos: obs informations queried from the database
        """
        body = {
            "gitee_branch": self.gitee_branch,
            "architecture": self.architecture,
        }
        if self.pkg_name:
            body.setdefault("repo_name", self.pkg_name)
        if self.build_state:
            body.setdefault("build_status", self.build_state)
        if self.sig_name:
            body.setdefault("name", self.sig_name)
        if self.maintainers:
            body.setdefault("maintainer.id", self.maintainers)
        if self.orders:
            body.setdefault("orders", self.orders)
        obs_infos = self._panel_info.query_obs_info(
            body=body, page_index=page, page_size=page_size
        )
        update_obs_infos = list()
        for obs_info in obs_infos:
            # If the repositories field exists, it will be removed
            obs_info_fields = list(obs_info.keys())
            if "repositories" in obs_info_fields:
                del obs_info["repositories"]
            # field rename
            if "name" in obs_info_fields:
                obs_info["sig_name"] = obs_info.pop("name")
            if "build_status" in obs_info_fields:
                obs_info["build_state"] = obs_info.pop("build_status")
            # Convert seconds to minutes
            obs_info["build_time"] = self._seconds_to_min(obs_info["build_time"])
            obs_info["history_build_times"] = self._seconds_to_min(
                obs_info["history_build_times"]
            )
            update_obs_infos.append(obs_info)
        return update_obs_infos

    def _total_page(self):
        """
        Count the number and pages of obs information
        """
        total_count = len(self._obs_infos(page_size=-1, page=self.page_index))

        try:
            total_page = math.ceil(total_count / int(self.page_size))
        except ZeroDivisionError as error:
            LOGGER.error(f"total_page calculation error,{error}")
            total_page = 0
        return total_count, total_page

    def _iso_build_data(self, recent_days=10):
        """
        iso build time
        Args:
            recent_days: How many days last
        Returns:

        """
        branch = self.gitee_branch[0]
        obs_branch = (
            "openEuler:Mainline" if branch == "master" else branch.replace("-", ":")
        )
        iso_info_ten = self._panel_info.query_iso_info(
            branch=obs_branch, recent_days=recent_days
        )
        for iso_info in iso_info_ten:
            iso_info["build_time"] = self._seconds_to_min(iso_info["build_time"])
            iso_info["iso_time"] = self._seconds_to_min(iso_info["iso_time"])
        # iso compilation data for the last 30 days
        iso_info_thirty = len(self._panel_info.query_iso_info(branch=obs_branch))
        iso_success_rate = self._iso_success_rate(iso_info_thirty)
        return iso_info_ten, iso_success_rate

    def _traverse_content(self, pkg_builds, column):
        """
        Traverse the information of obs and add data to cvs_list
        Args:
            pkg_builds: pkg build state
            column: csv column

        Returns:
            None
        """
        for index, pkg_build in enumerate(pkg_builds, start=2):
            self.modify_content_list(index, column, pkg_build)

    def _package_info(self, obs_info):
        """
        Package Field Information
        Args:
            obs_info: obs information dict

        Returns:
            detailed_infos: obs information list
        """

        detailed_infos = [
            self.ternary_comparison(obs_info.get("repo_name")),
            self.ternary_comparison(obs_info.get("obs_branch")),
            self.ternary_comparison(obs_info.get("build_state")),
            self.ternary_comparison(obs_info.get("build_detail_link")),
            self.ternary_comparison(obs_info.get("build_time")),
            self.ternary_comparison(obs_info.get("sig_name")),
            self.parse_owners_maintainers(obs_info.get("maintainer", [])),
            self.parse_owners_maintainers(obs_info.get("contributors", [])),
            self.ternary_comparison(obs_info.get("source_name")),
            self.ternary_comparison(obs_info.get("gitee_version")),
        ]
        return detailed_infos

    def _process_obs_data(self, obs_infos):
        """
        Process obs information to csv_list
        Args:
            obs_infos: obs information

        Returns:
            None
        """
        # iso rate
        self.modify_content_list(
            EXPORT_ISO_ROW, EXPORT_ISO_COLUMN, obs_infos.get("iso_success_rate")
        )
        # obs state
        pkg_build_states = self._csv_build_data(
            obs_infos.get("pkg_build_states"), BUILD_STATES
        )
        # obs build time
        pkg_build_times = self._csv_build_data(
            obs_infos.get("pkg_build_times"), BUILD_TIME_LEVEL
        )
        self._traverse_content(pkg_build_states, EXPORT_BUILD_STATE_COLUMN)
        self._traverse_content(pkg_build_times, EXPORT_BUILD_TIME_COLUMN)
        # obs package info
        for number, obs_info in enumerate(
            obs_infos.get("pkg_infos"), start=OBS_PACKAGE_INFO_COLUMN
        ):
            self.insert_row(number)
            for index, detailed_info in enumerate(
                self._package_info(obs_info), start=1
            ):
                self.insert_col(number, index, detailed_info)

    def suggest_maintainers(self, query=None):
        """
        Query maintainers by sig group
        Args:
            query: Fuzzy search maintainer
        Returns:
            maintainer  list
        """
        body = {"maintainer": query}
        query_all = False if query else True
        sigs = self._panel_info.query_suggest_info(
            index="sig_info", body=body, query_all=query_all
        )
        maintainers = set()
        for sig in sigs:
            for maintainer in sig["maintainer"]:
                maintainers.add(maintainer["id"])
        maintainers = sorted(maintainers)
        return maintainers
