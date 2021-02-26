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
            bedep_dict[bin_name] = copy.deepcopy(values)
            bedep_dict[bin_name].setdefault("build", [])
            bedep_dict[bin_name].setdefault("install", [])
            _update_install_lst(bin_name, values)

        _update_build_lst()
        return bedep_dict

    def filter_dict(self, root: str, level: int, direction: str = "bothward"):
        """get filter dict data

        Args:
            root (str): The name of the root node binary package
            level (int): The level of dependency that needs to be acquired
            direction (str, optional): [description]. Defaults to 'bothward'.

        Raises:
            ValueError: [level must gte 1]
            ValueError: [root not in this depend relations]
            ValueError: [Error direction,excepted in ["bothward","upward","downward"]]

        Returns:
            [dict]: [result dict data]
        """

        if level < 1:
            raise ValueError("level must gte 1")
        if root not in self.binary_dict:
            raise ValueError(f"{root} not in this depend relations")

        if direction not in ["bothward", "upward", "downward"]:
            raise ValueError(
                f'Error direction,excepted in ["bothward","upward","downward"],but given {direction}'
            )

        filter_data = dict()

        def _update_direction(pkg, level, layer, req_type, local_direction):
            """update direction data

            Args:
                pkg (str): the root node 
                level (int): filter level
                layer (int): current depend layer
                req_type (str): requires or be_requires
                local_direction (str): upward or downward
            """
            if level < 1:
                return
            level -= 1

            other_req = "requires" if req_type == "be_requires" else "be_requires"
            curr_layer = []
            try:
                for root_node in filter_data[pkg][req_type]:
                    curr_layer.append(root_node)
                    update_data_func(root_node, layer, local_direction)
                    
                    if root_node not in filter_data:
                        continue
                    
                    if other_req not in filter_data[root_node]:
                        continue

                    root_info = filter_data[root_node]
                    root_info["direction"] = (
                        "both" if root_info["direction"] != "root" else "root"
                    )
                   
            except KeyError:
                return
            for nlayer in curr_layer:
                _update_direction(nlayer, level, layer + 1, req_type, local_direction)

        def _update_be_reqs(pkg):
            """update data's be_requires value

            Args:
                pkg (str): root node
            """
            filter_data[pkg].setdefault("be_requires", [])
            for key, values in self.binary_dict.items():
                if (
                    pkg in values.get("install",[])
                    and key not in filter_data[pkg]["be_requires"]
                ):
                    filter_data[pkg]["be_requires"].append(key)

        def update_data_func(pkg, layer, local_direction):
            """update data miain function

            Args:
                pkg (str): root node
                layer (str): current depend layer
                local_direction (str): to search direction
            """
            try:
                pkg_info = self.binary_dict[pkg]
            except KeyError:
                return
            else:
                if pkg not in filter_data:
                    filter_data[pkg] = {
                        "name": pkg,
                        "source_name": pkg_info.get("source_name"),
                        "version": pkg_info.get("version"),
                        "level": layer,
                        "database": pkg_info.get("database"),
                        "direction": local_direction,
                    }

                if local_direction == "upward":
                    _update_be_reqs(pkg)
                elif local_direction == "downward":
                    filter_data[pkg]["requires"] = copy.deepcopy(
                        pkg_info.get("install", [])
                    )
                else:
                    filter_data[pkg]["requires"] = copy.deepcopy(
                        pkg_info.get("install", [])
                    )
                    _update_be_reqs(pkg)

        # start layer is 1
        update_data_func(root, 1, "root")
        # next level is level-1 and next layer is 2
        if direction == "bothward":
            _update_direction(root, level - 1, 2, "be_requires", "upward")
            _update_direction(root, level - 1, 2, "requires", "downward")
        elif direction == "upward":
            _update_direction(root, level - 1, 2, "be_requires", "upward")
        else:
            _update_direction(root, level - 1, 2, "requires", "downward")
        return filter_data

    def download_depend_files(self):
        """
        get the depend relationship with downloadable files
        """
        down_load = Download(depend=self)
        return down_load.run()

    def depend_info_graph(self, source, package_type):
        """get the depend relationship with graph format"""
        graph_info = GraphInfo(depend=self)

        return graph_info.generate_graph(root_node=source, package_type=package_type)
