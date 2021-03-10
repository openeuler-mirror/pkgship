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
Class: BeDependCommand
"""
import json
from json.decoder import JSONDecodeError
from requests.exceptions import ConnectionError as ConnErr

from packageship.application.cli.base import BaseCommand

from packageship.libs.log import LOGGER
from packageship.application.common.constant import ResponseCode

DB_NAME = 0


class BeDependCommand(BaseCommand):
    """
    Description: dependent query
    Attributes:
        parse: Command line parsing example
        params: Command line parameters
    """

    def __init__(self):
        """
        Description: Class instance initialization
        """
        super(BeDependCommand, self).__init__()
        self.parse = BaseCommand.subparsers.add_parser(
            'bedepend', help='dependency query for the specified package')
        self.collection = True
        self.params = [
            ('dbName', 'str', 'need to query the repositories of dependencies', '', 'store'),
            ('-w', 'str', 'Specifying -w means that you need to find sub-packages, not required by default', False,
             'store_true'),
            ('-b', 'str', 'the queried package is binary, and the source package is queried by default', False,
             'store_true'),
            ('-install', 'str',
             'Specify -install means that the query is dependent on the installation,-Install and -build cannot exist at the same time',
             False, 'store_true'),
            ('-build', 'str',
             'Specify -build means that the query is compiled to be dependent,-Install and -build cannot exist at the same time',
             False, 'store_true'),
            ('-remote', 'str', 'The address of the remote service', False, 'store_true')]
        self.collection_params = [('pkgName', 'source package name')]

    def register(self):
        """
        Description: Command line parameter injection
        Args:

        Returns:

        Raises:

        """
        super(BeDependCommand, self).register()
        for cmd_params in self.collection_params:
            self.parse.add_argument(
                cmd_params[0], nargs='*', default=None, help=cmd_params[1])
        self.parse.set_defaults(func=self.do_command)

    def do_command(self, params):
        """
        Description: Action to execute command
        Args:
            params: command lines params
        Returns:

        Raises:
            ConnectionError: self.request connection error
        """
        if params.build and params.install:
            print("error: argument -install not allowed with argument -build")
            print(self.parse.parse_args(['-h']))
            return
        self._set_read_host(params.remote)
        if params.b:
            pack_type = 'binary'
        else:
            pack_type = 'source'
        if params.install:
            install_or_build = "install"
        elif params.build:
            install_or_build = "build"
        else:
            install_or_build = ""
        _url = self.read_host + '/dependinfo/dependlist'
        try:
            self.request.request(_url, 'post', body=json.dumps(
                {
                    'packagename': params.pkgName,
                    'depend_type': 'bedep',
                    "parameter": {
                        "db_priority": [params.dbName],
                        "packtype": pack_type,
                        "with_subpack": params.w,
                        "search_type": install_or_build
                    }}), headers=self.headers)
        except ConnErr as conn_error:
            LOGGER.error(conn_error)
            self.output_error_formatted(str(conn_error), "CONN_ERROR")
        else:
            if self.request.status_code == 200:
                try:
                    response_data = json.loads(self.request.text)
                    if response_data.get('code') == ResponseCode.SUCCESS:
                        self.parse_depend_package(response_data)
                    else:
                        self.output_error_formatted(response_data.get('message'),
                                                    response_data.get('code'))
                except JSONDecodeError as json_error:
                    LOGGER.error(json_error)
                    self.output_error_formatted(
                        self.request.text, "JSON_DECODE_ERROR")
                else:
                    if getattr(self.bin_table, 'rowcount') or getattr(self.src_table, 'rowcount') or getattr(
                            self.statistics_table, 'rowcount'):
                        self.print_('query {} beDepend result display:'.format(
                            params.pkgName))
                        self.print_('Binary')
                        print(self.bin_table)
                        self.print_('Source')
                        print(self.src_table)
                        self.print_('Statistics')
                        print(self.statistics_table)
                        self.print_('Sum')
                        print(self.sum_table)
            else:
                self.output_error_formatted(
                    self.request.text, self.request.status_code)
