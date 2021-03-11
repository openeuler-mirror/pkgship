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
Class: DbPriorityCommand
"""
import json
from json.decoder import JSONDecodeError
from requests.exceptions import ConnectionError as ConnErr
from requests.exceptions import RequestException
from packageship.application.cli.base import BaseCommand
from packageship.application.common.constant import ResponseCode


class DbPriorityCommand(BaseCommand):
    """
    Description: Get all data tables in the current life cycle
    Attributes:
        parse: Command line parsing example
        params: Command line parameters
    """

    def __init__(self):
        """
        Description: Class instance initialization
        """
        super(DbPriorityCommand, self).__init__()

        self.parse = BaseCommand.subparsers.add_parser(
            'dbs', help='Get all data bases')
        self.params = [
            ('-remote', 'str', 'The address of the remote service', False, 'store_true')
        ]

    def register(self):
        """
        Description: Command line parameter injection

        """
        super(DbPriorityCommand, self).register()
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
        self._set_read_host(params.remote)
        _url = self.read_host + '/db_priority'
        try:
            response = self.request.get(_url, headers=self.headers)
        except ConnErr as conn_error:
            self.output_error_formatted("", "CONN_ERROR")
        except RequestException as request_exception:
            self.output_error_formatted(request_exception, "REMOTE_ERROR")
        else:
            if response.status_code == 200:
                try:
                    _response_content = json.loads(response.text)
                    if _response_content.get('code') == ResponseCode.SUCCESS:
                        self.print_('DB priority')
                        print(_response_content.get('resp', []))
                    else:
                        self.output_error_formatted(_response_content.get('message'),
                                                    _response_content.get('code'))
                except JSONDecodeError as json_error:
                    self.output_error_formatted(
                        response.text, "JSON_DECODE_ERROR")
            else:
                self.http_error(response)
