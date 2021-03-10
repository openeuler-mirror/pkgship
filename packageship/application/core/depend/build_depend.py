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
Build depend
"""
import copy
from packageship.libs.log import LOGGER
from packageship.application.query.depend import BuildRequires
from packageship.application.database.cache import buffer_cache
from .basedepend import BaseDepend
from .install_depend import InstallDepend

class BuildDepend(BaseDepend):
    """
    Description: query build depend of package

    Attributes:
        db_list: database priority list
        search_build_dict: stored source name for next binary search loop
        search_install_dict: stored bianry name for next install search loop
        binary_dict: stored the result for depend binary info
        source_dict: stored the resulth for depend source info
        depend_history: Query other dependent class
        com_not_found_pro: stored the comopent name which cannot find the provided pkg
        _search_set: stored the bianry name for this search loop
        __level: count the depend level
        __query_buildreq: query databases for getting build requires
    """

    def __init__(self, db_list, depend=None):
        """
        Args:
            db_list: database priority list
            depend: the type of BaseDepend class
        """
        if db_list:
            self.db_list = db_list
        else:
            raise AttributeError("the input of db_list is none")

        super(BuildDepend, self).__init__()

        self._init_search_dict(self.search_build_dict, self.db_list)
        self.__level = 0
        self.__query_buildreq = BuildRequires(db_list)
        if isinstance(depend, BaseDepend):
            self.depend_history = depend
            self.binary_dict = depend.binary_dict
            self.source_dict = depend.source_dict
            self.com_not_found_pro = depend.com_not_found_pro
            self.search_build_dict = depend.search_build_dict

    def build_depend(self, src_name, level=0, self_build=False):
        """
        Description: get source rpm package(s) build depend relation
        Args:
            src_name: the list of package names needed to be searched
            level: The number of levels of dependency querying,
                          the default value of level is 0, which means search all dependency
            self_build: whether to query self build
        Exception:
            AttributeError: the input value is invalid
        """
        if not isinstance(src_name, list):
            raise AttributeError("the input is invalid")
        for source in src_name:
            if source:
                self.search_build_dict.get("non_db").add(source)

        self.__level += 1
        self.__query_one_level_dep(level, self_build)
        if self.__level == level:
            return

        if self_build:
            while self._check_search(self.search_build_dict):
                self.__level += 1
                self.__query_one_level_dep(level, self_build)
                if self.__level == level:
                    break
        else:
            self.search_install_dict = self.search_build_dict
            install = InstallDepend(self.db_list, self)
            install.install_depend([], level=(level - 1) if level else 0)
            self.binary_dict, self.source_dict = install.depend_dict

    def __query_one_level_dep(self, level, self_build):
        """
        Description: query the one level build dep in database
        Args:
            level: The number of levels of dependency querying,
                    the default value of level is 0, which means search all dependency
            self_build: whether to query self build
        Returns:
            resp: the response for one level depend result
       """
        resp = self._query_in_db(
            search_dict=self.search_build_dict,
            func=self.__query_buildreq.get_build_req)
        # for build depend search, the first loop of search set is source packages,
        # but the second loop of the search set is binary packages,
        # so cannot use that set to remove duplicates
        if self.__level == 1:
            searched_pkg = copy.deepcopy(self._search_set)
        if not self_build:
            self._search_set.clear()

        # check the input packages searched result
        for pkg_info in resp:
            if not pkg_info:
                LOGGER.warning("There is a None type in resp")
                continue
            src_name = pkg_info.get("source_name")
            
            if not src_name:
                continue
            # check the input packages searched result
            if self.__level == 1:
                searched_pkg.discard(src_name)

            if not self._has_searched_dep(src_name, "build"):
                depend_set = set()
                #for non build depend, the list would be empty
                build_list = []
                for req in pkg_info.get("requires"):
                    com_bin_name = req.get("com_bin_name")
                    com_src_name = req.get("com_src_name")
                    com_db = req.get("com_database")
                    # for self build, need to update the search dict for next search loop
                    if self.depend_history:
                        self.depend_history.add_search_dict(
                            "build",
                            com_db,
                            com_bin_name=com_bin_name,
                            com_src_name=com_src_name)

                    # insert req info in last level loop
                    if not self_build and self.__level == level:
                        self._insert_com_info(req)

                    # add the bin name into depend set
                    if self._checka_and_add_com_value(
                            req,
                            self.search_build_dict,
                            self_build=self_build):
                        depend_set.add(com_bin_name)
                build_list = list(depend_set)

                self._insert_into_source_dict(
                    name=src_name,
                    version=pkg_info.get("src_version", "NOT FOUND"),
                    database=pkg_info.get("database", "NOT FOUND"),
                    build=build_list
                )
        self._search_set.clear()
        if self.__level == 1 and searched_pkg and not self.depend_history:
            self.log_msg = f"Can not find the packages: {str(searched_pkg)} in all databases"
            LOGGER.warning(self.log_msg)

    def __call__(self, **kwargs):
        self.__dict__.update(
            dict(packagename=kwargs["packagename"], dependency_type="builddep"))
        @buffer_cache(depend=self)
        def _depends(**kwargs):
            self.build_depend(src_name=kwargs["packagename"],
                              level=kwargs["parameter"]["level"],
                              self_build=kwargs["parameter"]["self_build"])
        _depends(**kwargs)
