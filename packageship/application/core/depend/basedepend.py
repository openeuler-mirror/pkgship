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
Depend Base Class
"""

import copy
from .graph import GraphInfo
from packageship.libs.log import LOGGER
from packageship.application.core.depend.down_load import Download

class BaseDepend:
    """
    Description: Depend base class

    Attributes:
        search_install_dict: stored bianry name for next install search loop
        search_build_dict: stored source name for next build search loop
        search_subpack_dict: stored source name for next subpack search loop
        binary_dict: stored the result for depend binary info
        source_dict: stored the resulth for depend source info
        depend_history: Query other dependent class
        com_not_found_pro: stored the comopent name which cannot find the provided pkg
        _search_set: stored the bianry name for this search loop
    """

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
            binary_dict [dict]: [bianry package dict data]
            source_dict [dict]: [source package dict data]
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
                        "bothward" if root_info["direction"] != "root" else "root"
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

    def _insert_into_binary_dict(self, name, **kwargs):
        """
        Description: insert binary info into binary dict
        """
        self.binary_dict[name] = {
            "name": name,
            "version": kwargs.get("version"),
            "source_name": kwargs.get("source_name"),
            "database": kwargs.get("database"),
        }
        # pacakges searched installdep wounld had "install" key
        if isinstance(kwargs.get("install"), list):
            self.binary_dict[name]["install"] = kwargs.get("install")

    def _insert_into_source_dict(self, name, **kwargs):
        """
        Description: insert source info into binary dict
        """
        self.source_dict[name] = {
            "name": name,
            "version": kwargs.get("version"),
            "database": kwargs.get("database"),
        }
        # pacakges searched builddep wounld had "build" key
        if isinstance(kwargs.get("build"), list):
            self.source_dict[name]["build"] = kwargs.get("build")

    def _checka_and_add_com_value(self, req: dict, search_dict: dict, self_build=False):
        """
        Description:parse the req dict, refresh the search dict for next search loop
        and update the com_not_found_pro set if need
        Attributes:
            req: requires dictionary contains install (or build) depend relation
            search_dict: install_search_dict or build_search_dict, com_bin_name may
                         insert into those dict for next search loop
            self_build: for self_build is True, would check the source name instand
                        of binary name
        """
        com_bin_name = req.get("com_bin_name")
        com_db = req.get("com_database")
        com_src_name = req.get("com_src_name")

        com_name = com_bin_name
        pkg_dict = self.binary_dict

        if self_build:
            com_name = com_src_name
            pkg_dict = self.source_dict

        if com_db and com_name and \
                (com_name not in self._search_set) and (com_name not in pkg_dict):
            # pkg which has not query the installdep yet,
            # put it into search dict based on the database which found it
            search_dict[com_db].add(com_name)

        if com_bin_name:
            return True
        # for the component which cannot find the bin name, add into com_not_found set
        self.com_not_found_pro.add(req.get("component"))
        return False

    def _insert_com_info(self, req):
        """
        Description:insert component info into dictionary
        Attributes:
            req: requires dictionary contains install (or build) depend relation
        """
        com_bin_name = req.get("com_bin_name")
        com_src_name = req.get("com_src_name")
        if com_bin_name and com_bin_name not in self.binary_dict:
            self._insert_into_binary_dict(
                name=com_bin_name,
                version=req.get("com_bin_version", "NOT FOUND"),
                source_name=req.get("com_src_name", "NOT FOUND"),
                database=req.get("com_database", "NOT FOUND")
            )
        if com_src_name and com_src_name not in self.source_dict:
            self._insert_into_source_dict(
                name=com_src_name,
                version=req.get("com_src_version", "NOT FOUND"),
                database=req.get("com_database", "NOT FOUND")
            )

    @staticmethod
    def _check_search(search_dict: dict):
        """
        Description:check the search dictionary value for next loop
        Attributes:
            search_dict: install, build, subpack dict, when the values is None,
                         means no packages search this loop
        """
        for value in search_dict.values():
            if value:
                return True
        return False

    def _has_searched_dep(self, key, search_type):
        """
        Description:check the package was searched before
        """
        # for search_type = "build"
        search_dict = self.source_dict
        if search_type == "install":
            search_dict = self.binary_dict

        if key not in search_dict:
            return False
        try:
            search_dict[key][search_type]
        except KeyError:
            return False
        return True

    @staticmethod
    def _init_search_dict(search_dict: dict, db_list: list):
        """
        Description: search_dict demo:
        {
            "openEuler-20.03": ["ant", "Judy", "glibc"],
            "openEuler-20.09": ["tomcat", "firefox", "CUnit"],
            "other-OS": ["python3", "redis", "flask"],
            "non_db": ["elasticsearch"]
        }
        """
        for db_name in db_list:
            search_dict[db_name] = set()
        search_dict["non_db"] = set()

    @staticmethod
    def __job(func, search_set, db_name):
        """
        Description: process the query database job
        Attributes:
            func: get_install_req, get_build_req or get_bin_name
            search_set: a set of package would searched as input
            db_name: specifed the db_name while searching, None means use db_list
        """
        _depend = []
        _depend = func(list(search_set), db_name)
        return _depend

    def _query_in_db(self, search_dict, func):
        """
        Description: execute the query database job based on search dict
        """
        resp = []

        for db_name, pkg_set in search_dict.items():
            if db_name == "non_db":
                db_name = None
            if pkg_set:
                pkg_set_tmp = copy.deepcopy(pkg_set)
                resp.extend(self.__job(func, pkg_set_tmp, db_name))
                self._search_set.update(pkg_set)
                pkg_set.clear()
        return resp
