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
import json
from json.decoder import JSONDecodeError
from requests.exceptions import ConnectionError as ConnErr

from packageship.application.cli.base import BaseCommand
from packageship.libs.log import LOGGER
from packageship.application.common.constant import ResponseCode
from packageship.application.query import database

db_list = database.get_db_priority()
DB_NAME = 0


class BuildDepCommand(BaseCommand):
    """
    Description: query the compilation dependencies of the specified package
    Attributes:
        parse: Command line parsing example
        params: Command line parameters
        collection: Is there a collection parameter
        collection_params: Command line collection parameters
    """

    def __init__(self):
        """
        Description: Class instance initialization
        """
        super(BuildDepCommand, self).__init__()
        self.parse = BaseCommand.subparsers.add_parser(
            'builddep', help='query the compilation dependencies of the specified package')
        self.collection = True
        self.params = [
            ('-level', 'str', 'Specify the dependency level that needs to be queried, by default to the last', 0,
             'store'),
            ('-remote', 'str', 'The address of the remote service', False, 'store_true')]
        self.collection_params = [
            ('sourceName', 'source package name'),
            ('-dbs', 'Operational database collection')
        ]

    def register(self):
        """
        Description: Command line parameter injection
        Args:

        Returns:

        Raises:

        """
        super(BuildDepCommand, self).register()
        # collection parameters
        for cmd_params in self.collection_params:
            self.parse.add_argument(
                cmd_params[0], nargs='*', default=None, help=cmd_params[1])
        self.parse.set_defaults(func=self.do_command)

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
        _url = self.read_host + '/dependinfo/dependlist'
        try:
            self.request.request(
                _url, 'post', body=json.dumps({
                    'packagename': params.sourceName,
                    'depend_type': 'builddep',
                    "parameter": {
                        "db_priority": params.dbs if params.dbs else db_list,
                        "level": params.level
                    }
                }),
                headers=self.headers)
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
                        self.print_('query {} buildDepend result display:'.format(
                            params.sourceName))
                        self.print_('Binary')
                        print(self.bin_table)
                        self.print_('Source')
                        print(self.src_table)
                        self.print_('Statistics')
                        print(self.statistics_table)
                        self.print_('Sum')
                        print(self.sum_table)
            else:
                self.output_error_formatted(self.request.text, self.request.status_code)
