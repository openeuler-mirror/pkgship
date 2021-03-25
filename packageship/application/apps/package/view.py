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
description: Interface processing
class: SourcePackages, BinaryPackages, SourcePackageInfo,BinaryPackageInfo,DatabasePriority
PkgshipVersion,TableColView
"""
import math
from flask import request
from flask import jsonify
from flask_restful import Resource

from packageship.application.query import database
from packageship.application.core.baseinfo import pkg_version
from packageship.application.serialize.package import PackageSchema
from packageship.application.serialize.package import SingleSchema
from packageship.application.core.pkginfo.pkg import Package
from packageship.application.core.pkginfo.pkg import SourcePackage
from packageship.application.core.pkginfo.pkg import BinaryPackage
from packageship.application.serialize.validate import validate
from packageship.application.common.rsp import RspMsg
from packageship.application.common.exc import ElasticSearchQueryException, DatabaseConfigException


class ParsePackageMethod(Resource):
    """
    Description: Common Method
    """

    def __init__(self):
        self.rspmsg = RspMsg()

    def parse_package(self, package_all, pagesize):
        """
        Description: Parsing package data with dependencies
        Args:
            package_all: http request response content
            pagesize: Quantity displayed on one page
        Returns:
            Summarized data table
        Raises:
        """
        total_count = package_all["total"]
        total_page = math.ceil(total_count / int(pagesize))
        packageinfo_list = package_all["data"]
        package_info_set = packageinfo_list
        response = self.rspmsg.body('success', resp=package_info_set)
        response["total_count"] = total_count
        response["total_page"] = total_page
        return response


class SourcePackages(ParsePackageMethod):
    """
    Description: interface for source package info management
    Restful API: get
    ChangeLog:
    """

    def get(self):
        """
        Get all package info from a database

        Args:
            database_name: Data base name
            page_num:
            page_size:
            query_pkg_name:
        Returns:
            for example::
               {
                   "code": "",
                    "total_count": xx,
                      "total_page": xx,
                      "resp": [
                        {
                          "pkg_name": "Judy",
                          "license": "Apache 2.0",
                          "version": "2.0.0",
                          "url":"http://www.xxx.com",
                          "database": "Mainline"
                        },
                        ...
                    "msg": ""
                }
        Raises:
        """
        data = request.args
        result, error = validate(PackageSchema, data, load=True)

        if error:
            response = self.rspmsg.body('param_error')
            response['total_count'] = None
            response['total_page'] = None
            return jsonify(response)

        page_num = result.get("page_num")
        page_size = result.get("page_size")
        query_pkg_name = [result.get("query_pkg_name")] if result.get(
            "query_pkg_name") else []
        find_package = Package()
        try:
            result_all = find_package.all_src_packages(
                result.get("database_name"), page_num=page_num, page_size=page_size, package_list=query_pkg_name,
                command_line=result.get("command_line"))
        except (ElasticSearchQueryException, DatabaseConfigException) as e:
            return jsonify(self.rspmsg.body('connect_db_error'))
        if result_all:
            return jsonify(self.parse_package(result_all, page_size))
        return jsonify(self.rspmsg.body("table_name_not_exist"))


class BinaryPackages(ParsePackageMethod):
    """
    Description: interface for binary package info management
    Restful API: get
    ChangeLog:
    """

    def get(self):
        """
        Get all package info from a database

        Args:
            database_name: Data base name
            page_num:
            page_size:
            query_pkg_name:
        Returns:
            for example::
               {
                   "code": "",
                    "total_count": xx,
                      "total_page": xx,
                      "resp": [
                        {
                          "pkg_name": "Judy",
                          "license": "Apache 2.0",
                          "version": "2.0.0",
                          "url":"http://www.xxx.com",
                          "source_name": "Judy",
                          "database": "Mainline"
                        },
                        ...
                        "msg": ""
                }
        Raises:
        """
        data = request.args
        result, error = validate(PackageSchema, data, load=True)
        if error:
            response = self.rspmsg.body('param_error')
            response['total_count'] = None
            response['total_page'] = None
            return jsonify(response)
        page_num = result.get("page_num")
        page_size = result.get("page_size")
        query_pkg_name = [result.get("query_pkg_name")] if result.get(
            "query_pkg_name") else []
        find_package = Package()
        try:
            result_all = find_package.all_bin_packages(
                result.get("database_name"), page_num=page_num, page_size=page_size, package_list=query_pkg_name,
                command_line=result.get("command_line"))
        except (ElasticSearchQueryException, DatabaseConfigException) as e:
            return jsonify(self.rspmsg.body('connect_db_error'))
        if result_all:
            return jsonify(self.parse_package(result_all, page_size))
        return jsonify(self.rspmsg.body("table_name_not_exist"))


class SourcePackageInfo(Resource):
    """
    Description: single source package management
    Restful API: get
    ChangeLog:
    """

    def get(self, pkg_name):
        """
        Searching a package info

        Args:
            database_name: Database name
            pkg_name: Source code package name
        Returns:
            for examples::
                {
                  "code":200,
                  "msg":"",
                  "resp": {
                    "openEuler:20.09":[
                        {
                          "pkg_name": "Judy",
                          "license": "Apache 2.0",
                          "version": "2.0",
                          "release":"oe.13",
                          "url": "http://www.xxx.com",
                          "summary":"xxxxxxxxxxxxxxxxx",
                          "description":"xxxxxxxxxx",
                          "buildrequired": ["build_rpm1","build_rpm2"],
                          "subpack":[
                            {
                              "bin_name":"Judy",
                              "provides": [
                                {
                                  "component":"Judy_com1",
                                  "required_by_bin":["CUnit-devel","tomcat"],
                                  "required_by_src":["CUnit","gcc"]
                                }
                              ],
                              "requires":[
                                {
                                  "component":"Judy_req1",
                                  "provided_by":["glibc"]
                                }]}]},
                        {
                          "pkg_name": "glibc",
                          "...": "..."
                        }
                    ]
                  }
                }
        Raises:
        """
        # Get verification parameters
        rspmsg = RspMsg()
        data = dict()
        data["database_name"] = request.args.get("database_name")
        data["pkg_name"] = pkg_name
        result, error = validate(SingleSchema, data, load=True)
        if error:
            response = rspmsg.body('param_error')
            return jsonify(response)
        pkg_name = [result.get("pkg_name")]
        database_name = [result.get("database_name")]
        find_source_package = SourcePackage()
        try:
            pkg_result = find_source_package.src_package_info(
                pkg_name, database_name)
        except (ElasticSearchQueryException, DatabaseConfigException) as e:
            return jsonify(rspmsg.body('connect_db_error'))
        if pkg_result:
            return jsonify(rspmsg.body('success', resp=pkg_result))
        return jsonify(rspmsg.body('pack_name_not_found'))


class BinaryPackageInfo(Resource):
    """
    Description: single binary package management
    Restful API: get
    ChangeLog:
    """

    def get(self, pkg_name):
        """
        Searching a package info

        Args:
            dbName: Database name, not required parameter
            sourceName: Source code package name, must pass
        Returns:
            for
            examples::
                {
                "code": "",
                "resp": [{
                "buildDep": [],
                "dbname": "",
                "license": "",
                "sourceName": "",
                "subpack": { },
                "version": ""}],
                "msg": ""
                 }
        Raises:
            DisconnectionError: Unable to connect to database exception
            AttributeError: Object does not have this property
            TypeError: Exception of type
            Error: Abnormal error
        """
        # Get verification parameters
        rspmsg = RspMsg()
        data = dict()
        data["database_name"] = request.args.get("database_name")
        data["pkg_name"] = pkg_name
        result, error = validate(SingleSchema, data, load=True)
        if error:
            response = rspmsg.body('param_error')
            return jsonify(response)
        pkg_name = [result.get("pkg_name")]
        database_name = [result.get("database_name")]
        find_binary_package = BinaryPackage()
        try:
            pkg_result = find_binary_package.bin_package_info(
                pkg_name, database_name)
        except (ElasticSearchQueryException, DatabaseConfigException) as e:
            return jsonify(rspmsg.body('connect_db_error'))
        if pkg_result:
            return jsonify(rspmsg.body('success', resp=pkg_result))
        return jsonify(rspmsg.body('pack_name_not_found'))


class DatabasePriority(Resource):
    """
    Description: Get the default repository sort
    Restful API: get
    ChangeLog
    """

    def get(self):
        """
        Get the default repository priority order

        Args:
        Returns:
            for
            examples::
                {
                "code": "200",
                "resp":["database2", "database3", "database4"],
                "msg": ""
                }
        Raises:
            DisconnectionError: Unable to connect to database exception
            AttributeError: Object does not have this property
            TypeError: Exception of type
            Error: Abnormal error
        """
        rspmsg = RspMsg()
        try:
            name_list = database.get_db_priority()
        except (ElasticSearchQueryException, DatabaseConfigException) as e:
            return jsonify(rspmsg.body('connect_db_error'))
        if not name_list:
            return jsonify(rspmsg.body('not_found_database_info'))
        res_dict = rspmsg.body('success', resp=name_list)
        return jsonify(res_dict)


class PkgshipVersion(Resource):
    """
    Description: Get the version number of pkgship
    Restful API: get
    ChangeLog:
    """

    def get(self):
        """
        Get the version number of pkgship

        Args:
        Returns:
            for
            examples::
                {
                "code": "200",
                "version":"1.0",
                "release":"13",
                "msg": ""
                }
        Raises:
        """
        rspmsg = RspMsg()
        version, release = pkg_version.get_pkgship_version()
        if not all([version, release]):
            return jsonify(rspmsg.body('get_pkgship_version_failed'))
        res_dict = rspmsg.body('success', version=version, release=release)
        return jsonify(res_dict)


class TableColView(Resource):
    """
    The default column of the package shows the interface
    """

    def __columns_names(self):
        """
        Mapping of column name and title
        """
        columns = [
            ('name', 'Name', True),
            ('version', 'Version', True),
            ('release', 'Release', True),
            ('url', 'Url', True),
            ('rpm_license', 'License', False)
        ]
        return columns

    def __columns_mapping(self):
        """
        Columns mapping
        """
        columns = list()
        for column in self.__columns_names():
            columns.append({
                'column_name': column[0],
                'label': column[1],
                'default_selected': column[2]
            })
        return columns

    def get(self):
        """
        Get the default display column of the package

        """
        table_mapping_columns = self.__columns_mapping()
        rspmsg = RspMsg()
        res_dict = rspmsg.body('success', resp=table_mapping_columns)
        return jsonify(res_dict)
