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
Description: Entry method for custom commands
Class: AllPackageCommand
"""
import json
from json.decoder import JSONDecodeError
from packageship.application.cli.base import BaseCommand
from requests.exceptions import RequestException
from requests.exceptions import ConnectionError as ConnErr
from packageship.application.common.constant import ResponseCode


class AllPackageCommand(BaseCommand):
    """
    Description: get all package commands
    Attributes:
        parse: Command line parsing example
        params: Command line parameters
        table: Output table
    """

    def __init__(self):
        """
        Description: Class instance initialization
        """
        super(AllPackageCommand, self).__init__()

        self.parse = BaseCommand.subparsers.add_parser(
            'list', help='get all package data')
        self.table = None
        self.src_table = self.create_table(
            ['Package Name', 'Database', 'Version', 'License', "URL"])
        self.bin_table = self.create_table(
            ['Package Name', 'Database', 'Version', 'License', "URL", "Source Name"])
        self.params = [('database', 'str', 'name of the database operated', '', 'store'),
                       ('-packagename', 'str',
                        'Package name that needs fuzzy matching', '', 'store'),
                       ('-s', 'str', 'Specify -s to query the source package information, If not specified, query '
                                     'binary package information by default', None, 'store_true'),
                       ('-remote', 'str', 'The address of the remote service', False, 'store_true')]

    def register(self):
        """
        Description: Command line parameter injection
        Args:

        Returns:

        Raises:

        """
        super(AllPackageCommand, self).register()
        self.parse.set_defaults(func=self.do_command)

    def __create_src_table(self, package_all, table_name):
        """
        Description: Create source package table
        Args:
            package_all: package info
            table_name: source or binary
        Returns:

        Raises:

        """
        for package_item in package_all:
            src_row_data = [package_item.get('pkg_name', ''),
                            table_name,
                            package_item.get('version', ''),
                            package_item.get('license', ''),
                            package_item.get('url', '')]
            self.src_table.add_row(src_row_data)
        if getattr(self.src_table, 'rowcount'):
            print(self.src_table)
        else:
            print('Sorry, no relevant information has been found yet')

    def __create_bin_table(self, package_all, table_name):
        """
        Description: Create binary package table
        Args:
            package_all: package info
            table_name: source or binary
        Returns:

        Raises:

        """
        for package_item in package_all:
            bin_row_data = [package_item.get('pkg_name', ''),
                            table_name,
                            package_item.get('version', ''),
                            package_item.get('license', ''),
                            package_item.get('url', ''),
                            package_item.get('source_name', '')]
            self.bin_table.add_row(bin_row_data)
        if getattr(self.bin_table, 'rowcount'):
            print(self.bin_table)
        else:
            print('Sorry, no relevant information has been found yet')

    def __parse_package(self, response_data, table_name, src_or_bin):
        """
        Description: Parse the corresponding data of the package
        Args:
            response_data: http request response content
        Returns:

        Raises:

        """
        package_all = response_data.get('resp')
        if isinstance(package_all, list):
            if src_or_bin:
                self.__create_src_table(package_all, table_name)
            else:
                self.__create_bin_table(package_all, table_name)

    def do_command(self, params):
        """
        Description: Action to execute command
        Args:
            params: Command line parameters
        Returns:

        Raises:
            ConnectionError: Request connection error
        """
        self._set_read_host(params.remote)
        if params.s:
            src_or_bin = 'src'
        else:
            src_or_bin = 'bin'

        _url = self.read_host + \
            '/packages/{src_or_bin}?database_name={database_name}&query_pkg_name={pkg_name}&page_num={page}' \
            '&page_size={pagesize}&command_line=True'.format(
                src_or_bin=src_or_bin,
                database_name=params.database,
                pkg_name=params.packagename,
                page=1,
                pagesize=200).replace(' ', '')
        try:
            response = self.request.get(_url)
        except ConnErr as conn_error:
            self.output_error_formatted("", "CONN_ERROR")
        except RequestException as request_exception:
            self.output_error_formatted(request_exception, "REMOTE_ERROR")
        else:
            if response.status_code == 200:
                try:
                    response_data = json.loads(response.text)
                    if response_data.get('code') == ResponseCode.SUCCESS:
                        self.__parse_package(
                            response_data, params.database, params.s)
                    else:
                        self.output_error_formatted(response_data.get('message'),
                                                    response_data.get('code'))
                except JSONDecodeError as json_error:
                    self.output_error_formatted(
                        response.text, "JSON_DECODE_ERROR")
            else:
                self.http_error(response)
