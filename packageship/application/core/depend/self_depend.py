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
Self depend
"""
from packageship.libs.log import LOGGER
from packageship.application.query.pkg import QueryPackage
from packageship.application.database.cache import buffer_cache
from .basedepend import BaseDepend
from .install_depend import InstallDepend
from .build_depend import BuildDepend


class SelfDepend(BaseDepend):

    """
    Description: query self depend of packages

    Attributes:
        db_list: database priority list
        search_install_dict: stored bianry name for next install search loop
        search_build_dict: stored source name for next build search loop
        search_subpack_dict: stored source name for next subpack search loop
        binary_dict: stored the result for depend binary info
        source_dict: stored the resulth for depend source info
        subpack: True means the search reasult would cover the package's subpack
        com_not_found_pro: stored the comopent name which cannot find the provided pkg
        _search_set: stored the bianry name for this search loop
        __query_pkg: query databases for getting subpack packages
    """

    def __init__(self, db_list):
        """
        Args:
            db_list: database priority list
        """
        if db_list:
            self.db_list = db_list
        else:
            raise AttributeError("the input of db_list is none")

        super(SelfDepend, self).__init__()
        self._init_search_dict(self.search_install_dict, self.db_list)
        self._init_search_dict(self.search_build_dict, self.db_list)
        self._init_search_dict(self.search_subpack_dict, self.db_list)

        self.__query_pkg = QueryPackage(self.db_list)
        self.subpack = False

    def self_depend(self, pkg_name, pkgtype="binary", self_build=False, with_subpack=False):
        """
        Description: get source(binary) rpm package(s) self depend relation
        Args:
            pkg_name: the list of package names needed to be searched
            db_priority: database name list
            packtype: the type of query package (source/binary)
            with_subpack: whether to query subpackages
            self_build: whether to query self build
        Exception:
            AttributeError: the input value is invalid
        """
        if not isinstance(pkg_name, list):
            raise AttributeError("the input is invalid")

        install = InstallDepend(self.db_list, self)
        build = BuildDepend(self.db_list, self)
        self.subpack = with_subpack
        for pkg in pkg_name:
            if pkg:
                if pkgtype == "source":
                    self.search_subpack_dict.get("non_db").add(pkg)
                else:
                    self.search_install_dict.get("non_db").add(pkg)
        if pkgtype == "source":
            self.__query_subpack()
        # end this loop while those three dictionry's value are None
        while self._check_search(self.search_install_dict) \
                or self._check_search(self.search_build_dict) \
                or self._check_search(self.search_subpack_dict):
            while self._check_search(self.search_install_dict):
                install.install_depend([])
            while self._check_search(self.search_build_dict):
                build.build_depend([], self_build=self_build)
            while with_subpack and self._check_search(self.search_subpack_dict):
                self.__query_subpack()

    def __query_subpack(self):
        """
        Description: query the source package's subpack in database
        Returns:
            resp: the response for subpack info result
       """
        resp = self._query_in_db(
            search_dict=self.search_subpack_dict,
            func=self.__query_pkg.get_bin_name)

        if not resp:
            LOGGER.warning(
                "Cannot get any resp for the packages ")

        for pkg_info in resp:
            if not pkg_info:
                LOGGER.warning(
                    "There is a None type in resp for ")
                continue
            src_name = pkg_info.get("source_name")
            db_name = pkg_info.get("database")
            if not (db_name and src_name):
                continue
            for bin_info in pkg_info.get("binary_infos"):
                bin_name = bin_info.get("bin_name")
                if bin_name and bin_name not in self.binary_dict:
                    self.search_install_dict[db_name].add(bin_name)

    def add_search_dict(self, add_type, com_db, com_bin_name=None, com_src_name=None):
        """
        Description: check wheather the package name insert into next search loop
        Args:
            add_type: "build" would influence next install search
                         "install" would influence next build search
            com_db: database name which update pkg seached in
            com_bin_name: the bianry package name for check
            com_src_name: the source package name for check
        """

        if com_db not in self.db_list:
            return
        if add_type == "build" and com_bin_name \
                and not self._has_searched_dep(com_bin_name, "install"):
            self.search_install_dict.get(com_db).add(com_bin_name)
        elif add_type == "install" and com_src_name \
                and not self._has_searched_dep(com_src_name, "build"):
            self.search_build_dict.get(com_db).add(com_src_name)

        if self.subpack and com_src_name \
                and not self._has_searched_dep(com_src_name, "build"):
            self.search_subpack_dict.get(com_db).add(com_src_name)

    def __call__(self, **kwargs):
        # self.packagename = kwargs["packagename"]
        # self.dependency_type = "selfdep"
        self.__dict__.update(
            dict(packagename=kwargs["packagename"], dependency_type="selfdep"))
        @buffer_cache(depend=self)
        def _depend(**kwargs):
            self.self_depend(pkg_name=kwargs["packagename"],
                             pkgtype=kwargs["parameter"]["packtype"],
                             self_build=kwargs["parameter"]["self_build"],
                             with_subpack=kwargs["parameter"]["with_subpack"])
        _depend(**kwargs)
