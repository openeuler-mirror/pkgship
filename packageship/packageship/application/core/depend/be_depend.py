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
from .basedepend import BaseDepend
from packageship.application.query.depend import BeDependRequires
from packageship.application.query.pkg import QueryPackage
from packageship.libs.log import LOGGER
from packageship.application.database.cache import buffer_cache


class BeDepend(BaseDepend):
    def __init__(self, **kwargs):
        super(BeDepend, self).__init__()
        self.__dict__.update(kwargs)
        self.database = self.parameter["db_priority"][0]
        self.provide = BeDependRequires()
        self.query_pkg = QueryPackage()

    def __get_subpacks(self, pkg_name_lst, is_init=False):
        """get source packages's subpacks

        Args:
            pkg_name_lst ([list]): [source packagenames list]

        Returns:
            [set]: [source package's subpacks]
        """
        binary_pkgs = set()
        if not pkg_name_lst:
            return binary_pkgs
        searched_pkg = set()
        for pkg_dict in self.query_pkg.get_src_info(
            pkg_name_lst, self.database, 1, len(pkg_name_lst)
        )["data"]:
            for _, pkg_info in pkg_dict.items():
                searched_pkg.add(pkg_info.get("src_name"))
                binary_pkgs.update(set(pkg_info.get("subpacks", [])))

        self._search_set.update(searched_pkg)
        if is_init:
            not_found_pkg = str(set(pkg_name_lst) - searched_pkg)
            self.log_msg = f"source packages {not_found_pkg} not found in {self.database}"
            LOGGER.warning(self.log_msg)
        return binary_pkgs

    def __update_binary_dict(self, dep_info):
        """update binary dict content

        Args:
            dep_info (dict): package depend info

        Returns:
            set: packages to search for next
        """
        next_search_binary = set()
        to_search_subpacks = set()
        bin_name = dep_info.get("binary_name")
        if not bin_name:
            return next_search_binary
        if bin_name not in self.binary_dict:
            self.binary_dict[bin_name] = {
                "name": bin_name,
                "version": dep_info.get("bin_version"),
                "source_name": dep_info.get("src_name"),
                "database": self.database,
                "install": [],
            }
        for pro in dep_info.get("provides", []):
            for req_bin_info in pro.get("install_require", []):
                next_search, next_src_names = self.__process_binary_data(
                    bin_name, req_bin_info
                )
                next_search_binary.update(next_search)
                to_search_subpacks.update(next_src_names)
        next_search_binary.update(self.__get_subpacks(to_search_subpacks))
        return next_search_binary

    def __update_source_dict(self, dep_info):
        """update source dict content

        Args:
            dep_info (dict): package depend info

        Returns:
            set: packages to search for next
        """
        next_search_pkgs = set()
        bin_name = dep_info.get("binary_name")
        if not bin_name:
            return next_search_pkgs

        src_name = dep_info.get("src_name")
        if src_name and src_name not in self.source_dict:
            self.source_dict[src_name] = {
                "name": src_name,
                "version": dep_info["src_version"],
                "database": self.database,
                "build": [],
            }

        for pro in dep_info.get("provides", []):
            for req_src_info in pro.get("build_require", []):
                next_search_pkgs.update(
                    self.__process_source_data(bin_name, req_src_info)
                )
        return next_search_pkgs

    def __process_binary_data(self, dep_name, req_bin_info):
        """[update binary data method]

        Args:
            dep_name ([str]): [deepend name]
            req_bin_info ([dict]): [package's install depend info ]

        Returns:
            [set]: [packages to search for next ]
        """
        with_subpack_src_names = set()
        next_search_binary = set()
        bin_key = req_bin_info.get("req_bin_name")
        src_name = req_bin_info.get("req_src_name")
        if not bin_key:
            return next_search_binary, with_subpack_src_names

        if bin_key not in self.binary_dict:
            self.binary_dict[bin_key] = {
                "name": bin_key,
                "version": req_bin_info["req_bin_version"],
                "source_name": src_name,
                "database": self.database,
                "install": [dep_name],
            }
            next_search_binary.add(bin_key)
            if self.parameter["with_subpack"] and src_name:
                with_subpack_src_names.add(src_name)
        else:
            if dep_name not in self.binary_dict[bin_key]["install"]:
                self.binary_dict[bin_key]["install"].append(dep_name)
        return next_search_binary, with_subpack_src_names

    def __process_source_data(self, dep_name, req_src_info):
        """[update source data method]

        Args:
            dep_name ([str]): [deepend name]
            req_src_info ([dict]): [package's build depend info ]

        Returns:
            [set]: [packages to search for next ]
        """
        next_search_pkgs = set()
        src_key = req_src_info["req_src_name"]
        if src_key not in self._search_set:
            next_search_pkgs.update(self.__get_subpacks([src_key]))
        if src_key not in self.source_dict:
            self.source_dict[src_key] = {
                "name": src_key,
                "version": req_src_info["req_src_version"],
                "database": self.database,
                "build": [dep_name],
            }
        else:
            if dep_name not in self.source_dict[src_key]["build"]:
                self.source_dict[src_key]["build"].append(dep_name)
        return next_search_pkgs

    def __both_update(self, dep_info):
        """update bianry data ,source data at the same time

        Args:
            dep_info (dict): package depend info

        Returns:
            set: packages to serach for next
        """
        next_search_pkgs = self.__update_binary_dict(dep_info)
        next_search_pkgs.update(self.__update_source_dict(dep_info))
        return next_search_pkgs

    def __get_update_data_method(self):
        """get update data method

        Returns:
            func: update_binary,update_source,both_upte
        """
        search_type = self.parameter.get("search_type")
        if not search_type:
            return self.__both_update
        if search_type == "install":
            return self.__update_binary_dict
        else:
            return self.__update_source_dict

    def __init_to_serach_pkgs(self):
        """init_to_serach_pkgs

        Returns:
            set: first to search binary pkgs
        """
        if self.parameter.get("packtype") == "source":
            return set(self.__get_subpacks(self.packagename, is_init=True))

        return set(self.packagename)

    def be_depend(self):
        """
        get source(binary) rpm package(s) bedepend relation
        """
        searched_pkgs = set()
        update_meth = self.__get_update_data_method()

        to_search = self.__init_to_serach_pkgs()
        is_init = True
        while to_search:
            resp = self.provide.get_be_req(to_search, self.database)
            if not resp:
                break

            next_search = set()

            for bedep_info in resp:
                searched_pkgs.add(bedep_info.get("binary_name"))
                next_pkgs = update_meth(bedep_info)
                next_search.update(next_pkgs)

            if is_init and self.parameter.get("packtype") == "binary":
                not_found_pkg = str(to_search - searched_pkgs)
                self.log_msg = f"binary packages {not_found_pkg} not found in {self.database}"
                LOGGER.warning(self.log_msg)
                is_init = False

            to_search = next_search - searched_pkgs

    def __call__(self, **kwargs):
        self.__dict__.update(dict(dependency_type="bedep"))

        @buffer_cache(depend=self)
        def _depends(**kwargs):
            self.be_depend()

        _depends(**kwargs)
