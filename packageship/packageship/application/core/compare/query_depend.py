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
Query dependency information
"""
from packageship.application.common.constant import BUILD_DEPEND_TYPE, DEFAULT_PAGE_NUM, MAXIMUM_PAGE_SIZE, \
    INSTALL_DEPEND_TYPE
from packageship.application.query.depend import BuildRequires, InstallRequires
from packageship.application.query.pkg import QueryPackage
from packageship.libs.log import LOGGER


class QueryDepend(object):
    """
    Query dependency information of all packages
    """
    SOURCE_NAME = "source_name"
    BINARY_NAME = "binary_name"

    def __init__(self):
        """
        init
        """
        self.result = list()
        self.query_pkg = QueryPackage()

    def all_depend_info(self, depend_type, dbs):
        """
        Get all rpm info ,include source rpm(query build depend) and binary rpm (query install rpm)
        :param depend_type:
        :param dbs:
        :return:
        """
        if depend_type == BUILD_DEPEND_TYPE:
            LOGGER.info("Start to query all source rpm dependency information")
            self._get_source_rpm_depend(dbs)
        elif depend_type == INSTALL_DEPEND_TYPE:
            LOGGER.info("Start to query all binary rpm dependency information")
            self._get_bin_rpm_depend(dbs)

        return self.result

    def _get_source_rpm_depend(self, dbs):
        """
        Get one-level compilation dependency of all source packages in the database
        :param dbs: Database to be queried
        :return: None
        """
        for database in dbs:
            # First,query all source rpm name of specify database.
            all_source_rpm = self.query_pkg.get_src_info(src_list=None, database=database,
                                                         page_num=DEFAULT_PAGE_NUM,
                                                         page_size=MAXIMUM_PAGE_SIZE, command_line=True)
            all_source_rpm_name = list()
            for source_rpm in all_source_rpm.get('data'):
                all_source_rpm_name.extend(source_rpm.keys())
            LOGGER.info(f'The number of source packages in the {database} database is {len(all_source_rpm_name)}')
            # Second, query the one-level build dependencies of all packages based on the package name.
            build_query_engine = BuildRequires([database])
            all_source_rpm_depend = build_query_engine.get_build_req(source_list=all_source_rpm_name)
            # Third, format build dependencies
            format_source_rpm_depend = self._format_depend(all_source_rpm_depend, key_word=self.SOURCE_NAME)

            self.result.append({database: format_source_rpm_depend})

    def _get_bin_rpm_depend(self, dbs):
        """
         Get one-level install dependency of all binary packages in the database
        :param dbs: Database to be queried
        :return:
        """
        for database in dbs:
            # First,query all binary rpm name of specify database.
            all_bin_rpm = self.query_pkg.get_bin_info(binary_list=None, database=database,
                                                      page_num=DEFAULT_PAGE_NUM,
                                                      page_size=MAXIMUM_PAGE_SIZE, command_line=True)
            all_bin_rpm_name = list()
            for bin_rpm in all_bin_rpm.get('data'):
                all_bin_rpm_name.extend(bin_rpm.keys())
            LOGGER.info(f'The number of binary packages in the {database} database is {len(all_bin_rpm_name)}')
            # Second, query the one-level install dependencies of all packages based on the package name.
            install_query_engine = InstallRequires([database])
            all_binary_rpm_depend = install_query_engine.get_install_req(binary_list=all_bin_rpm_name)
            # Third, format build dependencies
            format_binary_rpm_depend = self._format_depend(all_binary_rpm_depend, key_word=self.BINARY_NAME)

            self.result.append({database: format_binary_rpm_depend})

    @staticmethod
    def _format_depend(all_rpm_depend, key_word):
        """
        Format the query dependent information.
        :param all_rpm_depend: depend info
        :param key_word: build or install
        :return: Formatted dependency information
        """
        format_rpm_depend = list()
        for rpm_depend_info in all_rpm_depend:
            format_rpm_depend.append({rpm_depend_info.get(key_word): rpm_depend_info})
        return format_rpm_depend
