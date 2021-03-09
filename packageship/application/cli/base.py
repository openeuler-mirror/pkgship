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
Class: BaseCommand
"""

try:
    import argparse
    import prettytable
    from requests import HTTPError
    from packageship.libs.conf import configuration
    from packageship.application.common.exc import Error
    from requests.exceptions import ConnectionError as ConnErr
    from packageship.libs.log import LOGGER
    from packageship.application.common.remote import RemoteService
except ImportError as import_error:
    print("Error importing related dependencies,"
          "please check if related dependencies are installed")
else:
    from packageship.application.common.constant import ResponseCode
    from packageship.application.common.constant import ERROR_CON
    from packageship.libs.terminal_table import TerminalTable


class BaseCommand():
    """
    Description: Basic attributes used for command invocation
    Attributes:
        write_host: Can write operation single host address
        read_host: Can read the host address of the operation
        headers: Send HTTP request header information
    """
    parser = argparse.ArgumentParser(
        description='package related dependency management')
    subparsers = parser.add_subparsers(
        help='package related dependency management')

    def __init__(self):
        """
        Description: Class instance initialization

        """
        self.statistics = dict()
        # Calculate the total width of the current terminal
        self.columns = 100
        self.params = []
        self.write_host = None
        self.read_host = None
        self.__http = 'http://'
        self.headers = {"Content-Type": "application/json",
                        "Accept-Language": "zh-CN,zh;q=0.9"}

        self.load_read_host()
        self.request = RemoteService()
        self.bin_table = self.create_table(
            ['Binary name', 'Source name', 'Version', 'Database name'])
        self.src_table = self.create_table(
            ['Source name', 'Version', 'Database name'])
        self.statistics_table = self.create_table(
            ['Database name', 'Binary Sum', 'Source Sum'])
        self.sum_table = self.create_table(
            ['Sum', 'Binary Sum', 'Source Sum'])

    def load_read_host(self):
        """
        Returns:Address to load read permission
        Args:

        Returns:
        Raises:

        """
        read_port = configuration.QUERY_PORT

        read_ip = configuration.QUERY_IP_ADDR
        if all([read_ip, read_port]):
            _read_host = self.__http + read_ip + ":" + str(read_port)

            setattr(self, 'read_host', _read_host)

    def _set_read_host(self, remote=False):
        """
            Set read domain name
        """
        if remote:
            self.read_host = configuration.REMOTE_HOST
        if self.read_host is None:
            raise Error(
                "The system does not configure the relevant port and ip correctly")

    @staticmethod
    def output_error_formatted(content, code):
        """
        Description: Output error formatted characters
        Args:
           content: Output content
           code: Error code
        Returns:

        Raises:

        """
        con = ERROR_CON[code]
        if content:
            con["ERROR_CONTENT"] = content
        for key, val in con.items():
            print("{:15}:{}".format(key, val))

    @staticmethod
    def create_table(title=None):
        """
        Description: Create printed forms
        Args:
            title: Table title
        Returns:
            ASCII format table
        Raises:

        """
        table = TerminalTable(title)
        # table.set_style(prettytable.PLAIN_COLUMNS)
        table.align = 'l'
        table.horizontal_char = '='
        table.junction_char = '='
        table.vrules = prettytable.NONE
        table.hrules = prettytable.FRAME
        return table

    @staticmethod
    def http_error(response):
        """
        Description: Log error messages for http
        Args:
            response: Response content of http request
        Returns:

        Raises:
            HTTPError: http request error
        """
        try:
            print(response.raise_for_status())
        except HTTPError as http_error:
            LOGGER.error(http_error)
            print('Request failed')
            print(http_error)

    @staticmethod
    def show_separation(value, separation, separation_str=" "):
        """
        Description:Split content as required
        Args:
            value: Need to be divided content
            separation: Split length
            separation_str: Delimiter
        Returns:
            value_separation: Content after segmentation as required
        Raises:
        """
        value_separation = []
        range_num = len(value) // separation + 1 if len(value) % separation \
            else len(value) // separation
        for idx in range(range_num):
            value_separation.append(separation_str.join(value[separation * idx:
                                                              separation * (idx + 1)]))
        return value_separation

    def print_(self, content=None, character='=', dividing_line=False):
        """
        Description: Output formatted characters
        Args:
           content: Output content
           character: Output separator content
           dividing_line: Whether to show the separator
        Returns:

        Raises:

        """
        # Get the current width of the console

        if dividing_line:
            print(character * self.columns)
        if content:
            print(content)
        if dividing_line:
            print(character * self.columns)

    @staticmethod
    def register_command(command):
        """
        Description: Registration of related commands

        Args:
            command: Related commands

        Returns:
        Raises:

        """
        command.register()

    def register(self):
        """
        Description: Command line parameter injection
        Args:

        Returns:

        Raises:

        """
        for command_params in self.params:
            self.parse.add_argument(  # pylint: disable=E1101
                command_params[0],
                # type=eval(command_params[1]),  # pylint: disable=W0123
                help=command_params[2],
                default=command_params[3],
                action=command_params[4])

    def parse_depend_package(self, response_data):
        """
        Description: Parse the detail data of the package
        Args:
            response_data: http response data
        Returns:

        Raises:

        """
        if response_data.get('code') == ResponseCode.SUCCESS:
            package_all = response_data.get('resp')
            for bin_data in package_all["binary_list"]:
                bin_row_data = [bin_data["binary_name"],
                                bin_data["source_name"],
                                bin_data["version"],
                                bin_data["database"]]
                self.bin_table.add_row(bin_row_data)
            for src_data in package_all["source_list"]:
                src_row_data = [src_data["source_name"],
                                src_data["version"],
                                src_data["database"]]
                self.src_table.add_row(src_row_data)
            for statistic in package_all["statistics"]:
                if "sum" in statistic:
                    self.sum_table.add_row([statistic['sum'],
                                            statistic['binarys_sum'],
                                            statistic['sources_sum']])
                else:
                    self.statistics_table.add_row([statistic['database'],
                                                   statistic['binary_sum'],
                                                   statistic['source_sum']])

