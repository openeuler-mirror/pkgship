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
import copy
from .graph import GraphInfo
from packageship.libs.log import LOGGER
from packageship.application.common.export import Download


class BaseDepend:
    def __init__(self):
        """
        Initialization class
        """
        self.binary_dict = dict()
        self.source_dict = dict()
        # set used as the query function input
        # dict used for storging the query list and query database
        self._search_set = set()
        self.search_install_dict = dict()
        self.search_build_dict = dict()
        self.search_subpack_dict = dict()
        self.depend_history = None

        # stored the comopent name which cannot find the provided pkg
        self.com_not_found_pro = set()

    def depend_list(self):
        """
        get the depend relationship with list format
        """
        binary_list = []
        source_list = []

        statistics_info = {}
        for bin_name, binary_info in self.binary_dict.items():
            curr_bin_database = binary_info["database"]
            binary_list.append(
                {
                    "binary_name": bin_name,
                    "source_name": binary_info.get("source_name"),
                    "version": binary_info.get("version"),
                    "database": curr_bin_database,
                }
            )
            if curr_bin_database not in statistics_info:
                statistics_info[curr_bin_database] = {
                    "database": curr_bin_database,
                    "binary_sum": 1,
                    "source_sum": 0,
                }
            else:
                statistics_info[curr_bin_database]["binary_sum"] += 1

        for src_name, source_info in self.source_dict.items():
            curr_src_database = source_info["database"]
            source_list.append(
                {
                    "source_name": src_name,
                    "version": source_info.get("version"),
                    "database": source_info.get("database"),
                }
            )
            if curr_src_database not in statistics_info:
                statistics_info[curr_src_database] = {
                    "database": curr_src_database,
                    "binary_sum": 0,
                    "source_sum": 1,
                }
            else:
                statistics_info[curr_src_database]["source_sum"] += 1

        statistics = [val for _, val in statistics_info.items()]

        return {
            "binary_list": binary_list,
            "source_list": source_list,
            "statistics": statistics,
        }

    @property
    def depend_dict(self):
        """[get depend dict]

        Returns:
            binary_dict [dict]: [description]
            source_dict [dict]: [description]
        """
        return self.binary_dict, self.source_dict

    @property
    def bedepend_dict(self):
        bedep_dict = dict()

        def _update_install_lst(local_bin_name, local_values):
            for binary_name in local_values.get("install", []):
                try:
                    install_infos = self.binary_dict[binary_name]
                except KeyError:
                    continue
                bedep_dict.setdefault(
                    binary_name,
                    {
                        "name": binary_name,
                        "source_name": install_infos.get("source_name", None),
                        "version": install_infos.get("version", None),
                        "database": install_infos.get("database", None),
                        "install": [local_bin_name],
                        "build": [],
                    },
                )["install"].append(local_bin_name)

        def _update_build_lst():
            for src_name, src_value in self.source_dict.items():
                for build_bin_name in src_value.get("build", []):
                    try:
                        build_info = bedep_dict[build_bin_name]
                        build_info["build"].append(src_name)
                    except KeyError:
                        continue

        for bin_name, values in self.binary_dict.items():
            if bin_name not in bedep_dict:
                bedep_dict[bin_name] = copy.deepcopy(values)
                bedep_dict[bin_name].update({"build": []})
            _update_install_lst(bin_name, values)
        _update_build_lst()
        return bedep_dict