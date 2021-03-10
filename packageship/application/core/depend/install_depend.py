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
Install depend
"""
import copy
from packageship.libs.log import LOGGER
from packageship.application.query.depend import InstallRequires
from packageship.application.database.cache import buffer_cache
from .basedepend import BaseDepend
class InstallDepend(BaseDepend):

    """
    Description: query install depend of package

    Attributes:
        db_list: database priority list
        search_install_dict: stored bianry name for next install search loop
        binary_dict: stored the result for depend binary info
        source_dict: stored the resulth for depend source info
        depend_history: Query other dependent class
        com_not_found_pro: stored the comopent name which cannot find the provided pkg
        _search_set: stored the bianry name for this search loop
        __level: count the depend level
        __query_installreq: query databases for getting install requires
    """

    def __init__(self, db_list, depend=None):
        """
        Args:
            db_list: database priority list
            depend: the type of BaseDepend class
        """
        if not db_list:
            raise ValueError("the input of db_list is none")

        super(InstallDepend, self).__init__()

        self._init_search_dict(self.search_install_dict, db_list)
        self.__level = 0
        self.__query_installreq = InstallRequires(db_list)

        
        # for build and self depend, get the previous result from the input cls
        if isinstance(depend, BaseDepend):
            self.depend_history = depend
            self.binary_dict = depend.binary_dict
            self.source_dict = depend.source_dict
            self.com_not_found_pro = depend.com_not_found_pro
            self.search_install_dict = depend.search_install_dict
            # if the depend type is build,
            # there would be a build depend result in the source dict
            self.depend_type = "build" if self.source_dict else "self"

    def install_depend(self, bin_name, level=0):
        """
        Description: get binary rpm package(s) install depend relation
        Args:
            bin_name: the list of package names needed to be searched
            level: The number of levels of dependency querying,
                    the default value of level is 0, which means search all dependency
        Exception:
            AttributeError: the input value is invalid
       """
        if not isinstance(bin_name, list):
            raise AttributeError("the input is invalid")
        for binary in bin_name:
            if binary:
                self.search_install_dict.get("non_db").add(binary)

        while self._check_search(self.search_install_dict):
            self.__level += 1
            self.__query_one_level_dep(level)
            # Stop the query when the __level in the query reaches the input of level
            if self.__level == level:
                break

    def __query_one_level_dep(self, level):
        """
        Description: query the one level install dep in database
        Args:
            level: The number of levels of dependency querying,
                    the default value of level is 0, which means search all dependency
        Returns:
            resp: the response for one level depend result
       """
        resp = self._query_in_db(
            search_dict=self.search_install_dict,
            func=self.__query_installreq.get_install_req)

        if self.__level == 1:
            searched_pkg = copy.deepcopy(self._search_set)

        for pkg_info in resp:
            if not pkg_info:
                LOGGER.warning("There is a None type in resp")
                continue
            bin_name = pkg_info.get("binary_name")
            src_name = pkg_info.get("src_name")

            if not bin_name:
                continue
            # check the input packages searched result
            if self.__level == 1:
                searched_pkg.discard(bin_name)

            if not self._has_searched_dep(bin_name, "install"):
                # binary pkg which has not query the installdep yet,
                # put it into search dict based on the database which found it
                depend_set = set()
                #for non install depend, the list would be empty
                install_list = []
                for req in pkg_info.get("requires"):
                    com_bin_name = req.get("com_bin_name")
                    # insert req info in last level loop
                    if self.__level == level:
                        self._insert_com_info(req)

                    if self._checka_and_add_com_value(req, self.search_install_dict):
                        depend_set.add(com_bin_name)
                install_list = list(depend_set)

                # put the package binary info into binary result dict
                self._insert_into_binary_dict(
                    name=bin_name,
                    version=pkg_info.get("bin_version", "NOT FOUND"),
                    source_name=pkg_info.get("src_name", "NOT FOUND"),
                    database=pkg_info.get("database", "NOT FOUND"),
                    install=install_list
                )

            # put the package source info into source result dict
            if src_name and src_name not in self.source_dict:
                self._insert_into_source_dict(
                    name=src_name,
                    version=pkg_info.get("src_version", "NOT FOUND"),
                    database=pkg_info.get("database", "NOT FOUND")
                )

            if self.depend_history and self.depend_type == "self":
                self.depend_history.add_search_dict(
                    "install",
                    pkg_info.get("database"),
                    com_src_name=src_name)

        self._search_set.clear()
        if self.__level == 1 and searched_pkg and not self.depend_history:
            self.log_msg = f"Can not find the packages:{str(searched_pkg)}in all databases"
            LOGGER.warning(self.log_msg)
            
    def __call__(self, **kwargs):
        self.__dict__.update(
            dict(packagename=kwargs["packagename"], dependency_type="installdep"))

        @buffer_cache(depend=self)
        def _depend(**kwargs):
            self.install_depend(bin_name=kwargs["packagename"],
                                level=kwargs["parameter"]["level"])
        _depend(**kwargs)
