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

    @property
    def depend_dict(self):
        """[get depend dict]

        Returns:
            binary_dict [dict]: [bianry package dict data]
            source_dict [dict]: [source package dict data]
        """
        return self.binary_dict, self.source_dict

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

    def _check_com_value(self, req: dict, search_dict: dict, self_build=False):
        """
        Description:parse the req dict, refresh the search dict for next search loop
        and update the com_not_found_pro set if need
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
        """
        for value in search_dict.values():
            if value:
                return True
        return False

    def _search_dep_before(self, key, search_type):
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
    def job(func, search_set, db_name):
        """
        Description: process the query database job
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
                resp.extend(self.job(func, pkg_set_tmp, db_name))
                self._search_set.update(pkg_set)
                pkg_set.clear()
        return resp
