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
Description: query package information
"""
from packageship.application.common.exc import ParametersError, \
    DatabaseConfigException, ElasticSearchQueryException
from packageship.application.query import database as db
from packageship.application.query.pkg import QueryPackage
from packageship.libs.log import LOGGER

class Package:
    """
       Get all source package info and binary package info
    """

    def validate_parameter(self, database, page_num, page_size, command_line):
        """
            Check whether the parameters meet the specifications
            Args:
                database: database
                page_num: Paging query index
                page_size: Paging query size
                command_line： command_line or UI
            Returns: True or False

        """
        database_list = db.get_db_priority()
        if not isinstance(database, str) or database not in database_list:
            return False
        if not isinstance(page_num, int) or not isinstance(page_size, int):
            return False
        if page_num < 1 or page_size < 1 or page_size > 200:
            return False
        if command_line not in (True, False):
            return False
        return True

    def parse_pkg_info(self, package_info_dict, pkgname, database):
        """
            Parse the info of the source package or binary package
            Args:
                package_info_dict: source package info or binary package info
                pkgname: package mame
                database: database

            Returns:
                    pkg_info: parsed package info
        """
        pkg_info = {
            "pkg_name": pkgname,
            "license": package_info_dict.get("license"),
            "version": package_info_dict.get("version"),
            "url": package_info_dict.get("url"),
            "database": database
        }
        return pkg_info

    def all_src_packages(self, database, page_num=1, page_size=20,
                         package_list=None, command_line=False):
        """
        get all source rpm packages base info
        Args:
            database: database
            page_num: paging query index
            page_size: paging query size
            package_list: package list name
            command_line: command_line or UI

        Returns:
            all_src_dict: all parsed source package information dict
            for example:
                {
                "total": "",
                "data": ""
                }
        Attributes:
            AttributeError: Cannot find the attribute of the corresponding object
            IndexError: list index out of range
            TypeError: object does not support this property or method
            ElasticSearchQueryException: dataBase connect failed
            DatabaseConfigException: dataBase config error

        Raises:
            ParametersError: parameter error
        """
        if not self.validate_parameter(database, page_num, page_size, command_line):
            _msg = "Parameters error, please check the parameters."
            raise ParametersError(_msg)
        try:
            # query all source package info from database
            query_package = QueryPackage()
            all_src_info = query_package.get_src_info(
                package_list, database, page_num, page_size, command_line)

            if not all_src_info or not isinstance(all_src_info, dict):
                _msg = "Error in querying src info."
                LOGGER.error(_msg)
                return {}
            # parse all source package info
            parsed_all_src_info = []
            total_num = all_src_info.get("total")
            for pkg_info in all_src_info.get("data"):
                pkgname = list(pkg_info.keys())[0]
                parsed_pkg_info = self.parse_pkg_info(
                    pkg_info.get(pkgname), pkgname, database)
                parsed_all_src_info.append(parsed_pkg_info)
            all_src_dict = {"total": total_num, "data": parsed_all_src_info}
            return all_src_dict
        except (AttributeError, IndexError, TypeError,
                DatabaseConfigException, ElasticSearchQueryException):
            _msg = "Error in querying src info."
            LOGGER.error(_msg)
            return {}


    def all_bin_packages(self, database, page_num=1, page_size=20,
                         package_list=None, command_line=False):
        """
        get all binary package info
        Args:
            database: database
            page_num: paging query index
            page_size: paging query size
            package_list: package list name
            command_line： command_line or UI
        Returns:
            all_bin_dict: all binary package information dict
            for example::
                {
                "total": "",
                "data": ""
                }
        Attributes:
            AttributeError: Cannot find the attribute of the corresponding object
            IndexError: list index out of range
            TypeError: object does not support this property or method
            ElasticSearchQueryException: dataBase connect failed
            DatabaseConfigException: dataBase config error

        Raises:
            ParametersError: parameter error
        """
        if not self.validate_parameter(database, page_num, page_size, command_line):
            _msg = "Parameters error, please check the parameters."
            raise ParametersError(_msg)
        try:
            # query all binary package info from database
            query_package = QueryPackage()
            all_bin_info = query_package.get_bin_info(
                package_list, database, page_num, page_size, command_line)

            if not all_bin_info or not isinstance(all_bin_info, dict):
                _msg = "Error in querying binary package info."
                LOGGER.error(_msg)
                return {}

            parsed_all_bin_info = []
            total_num = all_bin_info.get("total")
            for pkg_info in all_bin_info.get("data"):
                pkgname = list(pkg_info.keys())[0]
                parsed_pkg_info = self.parse_pkg_info(
                    pkg_info.get(pkgname), pkgname, database)
                parsed_pkg_info["source_name"] = pkg_info.get(
                    pkgname).get("src_name")
                parsed_all_bin_info.append(parsed_pkg_info)
            all_bin_dict = {"total": total_num, "data": parsed_all_bin_info}
            return all_bin_dict
        except (AttributeError, IndexError, TypeError,
                DatabaseConfigException, ElasticSearchQueryException):
            _msg = "Error in querying binary package info."
            LOGGER.error(_msg)
            return {}


class SourcePackage:

    def src_package_info(self):
        """
            get a source package info (provides, requires, etc)
        """
        pass


class BinaryPackage:

    def bin_package_info(self):
        """
            get a binary package info (provides, requires, etc)
        """
        pass
