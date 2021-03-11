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
Class: VersionCommand
"""
import json
from json.decoder import JSONDecodeError
from requests.exceptions import ConnectionError as ConnErr
from packageship.application.common.constant import ResponseCode
from packageship.application.cli.base import BaseCommand


class VersionCommand(BaseCommand):
    """
    Description: Issue and life cycle information involved in batch processing packages
    Attributes:
        parse: Command line parsing example
        params: Command line parameters
    """

    def __init__(self):
        """
        Description: Class instance initialization
        """
        super(VersionCommand, self).__init__()

        # self.parse = BaseCommand.subparsers.add_parser(
        #     'v', help='Get version information')
        self.parse = BaseCommand.parser
        self.params = [
            ('-v', 'str', 'Get version information', None, 'store_true'),
            ('-remote', 'str', 'The address of the remote service', False, 'store_true')
        ]

    def register(self):
        """
        Description: Command line parameter injection

        """
        super(VersionCommand, self).register()
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
        if not params.v:
            print(self.parse.parse_args(['-h']))
            return
        _url = self.read_host + '/version'

        try:
            response = self.request.get(_url, headers=self.headers)
        except ConnErr as conn_error:
            self.output_error_formatted("", "CONN_ERROR")
        else:
            if response.status_code == 200:
                try:
                    _response_content = json.loads(response.text)
                    if _response_content.get('code') == ResponseCode.SUCCESS:
                        print('Version:{}'.format(
                            _response_content.get('version', [])))
                        print('Release:{}'.format(
                            _response_content.get('release', [])))
                    else:
                        self.output_error_formatted(_response_content.get('message'),
                                                    _response_content.get('code'))
                except JSONDecodeError as json_error:
                    self.output_error_formatted(
                        response.text, "JSON_DECODE_ERROR")
            else:
                self.http_error(response)
