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
Class: SingleCommand
"""
import json
from json.decoder import JSONDecodeError
from requests.exceptions import ConnectionError as ConnErr
from packageship.application.cli.base import BaseCommand

from packageship.application.common.constant import ResponseCode

DEPRECATION_LEN = 12
LIST_LEN = 6
ZERO = 0


class SingleCommand(BaseCommand):
    """
    Description: query single package information
    Attributes:
        parse: Command line parsing example
        params: Command line parameters
    """

    def __init__(self):
        """
        Description: Class instance initialization
        """
        super(SingleCommand, self).__init__()

        self.parse = BaseCommand.subparsers.add_parser(
            'pkginfo', help='query the information of a single package')
        self.params = [
            ('packagename', 'str', 'source package name', '', 'store'),
            ('database', 'str', 'name of the database operated', '', 'store'),
            ('-s', 'str', 'Specify -s to query the src source package information, If not specified, query bin binary '
                          'package information by default', None, 'store_true'),
            ('-remote', 'str', 'The address of the remote service', False, 'store_true')]
        self.provides_table = self.create_table(['Symbol', 'Required by'])
        self.requires_table = self.create_table(['Symbol', 'Provides by'])
        self.file_list_table = self.create_table(['Symbol', 'File List'])

    def register(self):
        """
        Description: Command line parameter injection
        Args:

        Returns:

        Raises:

        """
        super(SingleCommand, self).register()
        self.parse.set_defaults(func=self.do_command)

    # pylint: disable=too-many-branches
    def __parse_package_detail(self, response_data, src_or_bin):
        """
        Description: Parse the detail data of the package
        Args:
            response_data: http response data
        Returns:

        Raises:

        """
        _src_show_field_name = {'src_name': "Source Name", 'version': "Version",
                                'url': "Url", 'license': "License", 'summary': "Summary",
                                'description': "Description", 'build_dep': "Build Depend", 'subpacks': "Subpacks"}
        _bin_show_field_name = {'bin_name': "Binary Name", 'src_name': "Source Name", 'version': "Version",
                                'url': "Url", 'license': "License", 'release': "Release", 'summary': "Summary",
                                'description': "Description"}
        if src_or_bin:
            _show_field_name = _src_show_field_name
        else:
            _show_field_name = _bin_show_field_name
        _package_detail_info = response_data
        _line_content = []
        subpacks = []
        if not _package_detail_info:
            return
        for subpack_item in _package_detail_info.get('subpacks', []):
            subpacks.append(subpack_item['bin_name'])
        _package_detail_info['subpacks'] = subpacks
        for key, name_value in _show_field_name.items():
            value = _package_detail_info.get(key, "")
            if isinstance(value, list):
                value_s = self.show_separation(
                    value, LIST_LEN, separation_str=',')
                for idx, con in enumerate(value_s):
                    if idx != ZERO:
                        name_value = " "
                    _line_content.append("%-15s:%s" % (name_value, con))
            if key == "description":
                value = _package_detail_info.get(key).split()
                value_d = self.show_separation(value, DEPRECATION_LEN)
                for idx, con in enumerate(value_d):
                    if idx != ZERO:
                        name_value = " "
                    _line_content.append("%-15s:%s" % (name_value, con))
            if not isinstance(value, list) and key != "description":
                _line_content.append('%-15s:%s' % (name_value, value))
        for content in _line_content:
            self.print_(content=content)

    def __parse_provides(self, provides):
        """
        Description: Data analysis of provides package
        Args:
            provides: provides
        Returns:

        Raises:

        """
        if provides and isinstance(provides, list):
            for _provide in provides:
                _provide_list = _provide.get('required_by_bin', '') + \
                    _provide.get('required_by_src', '')
                _required_by = '\n'.join(
                    _provide_list) if _provide_list else ''
                self.provides_table.add_row(
                    [_provide['component'], _required_by])
        self.print_('Provides')
        if getattr(self.provides_table, 'rowcount'):
            print(self.provides_table)
        else:
            print('No relevant dependent data')
        self.provides_table.clear_rows()

    def __parse_requires(self, requires):
        """
        Description: Data analysis of requires package
        Args:
            requires: requires
        Returns:

        Raises:
        """
        if requires and isinstance(requires, list):
            for _require in requires:
                _provide_by = '\n'.join(
                    _require.get('provided_by', ''))
                self.requires_table.add_row(
                    [_require.get('component', ''), _provide_by])
        self.print_('Requires')
        if getattr(self.requires_table, 'rowcount'):
            print(self.requires_table)
        else:
            print('No related components')
        self.requires_table.clear_rows()

    def __parse_subpack(self, subpacks):
        """
        Description: Data analysis of binary package
        Args:
            subpacks: subpacks
        Returns:

        Raises:
        """
        for subpack_item in subpacks:
            print('-' * 50)
            self.print_(subpack_item.get('bin_name', ''))

            self.__parse_provides(subpack_item.get('provides', ''))
            self.__parse_requires(subpack_item.get('requires', ''))

    def __parse_filelist(self, filelist):
        """
        Description: Data analysis of file list
        Args:
            filelist: filelist
        Returns:

        Raises:
        """
        for key, value in filelist.items():
            _filelist = '\n'.join(value) if value else ''
            self.file_list_table.add_row([key, _filelist])

        self.print_('File List')
        if getattr(self.file_list_table, 'rowcount'):
            print(self.file_list_table)
        else:
            print('No related components')
        self.file_list_table.clear_rows()

    def __parse_src_package(self, response_data, database, src_or_bin):
        """
        Description: Parse the corresponding data of the package
        Args:
            response_data: http response data
        Returns:

        Raises:

        """
        parse_data = response_data['resp'].get(database)[ZERO]
        try:
            _subpacks = parse_data['subpacks']
            self.__parse_package_detail(parse_data, src_or_bin)
            self.__parse_subpack(_subpacks)
        except KeyError as key_error:
            print('No related components')

    def __parse_bin_package(self, response_data, database, src_or_bin):
        """
        Description: Parse the corresponding data of the package
        Args:
            response_data: http response data
        Returns:

        Raises:

        """
        parse_data = response_data['resp'].get(database)[ZERO]
        self.__parse_package_detail(parse_data, src_or_bin)
        try:
            _provides = parse_data['provides']
            self.__parse_provides(_provides)
            _requires = parse_data['requires']
            self.__parse_requires(_requires)
            _filelist = parse_data['filelist']
            self.__parse_filelist(_filelist)
        except KeyError as key_error:
            print('No related components')

    def do_command(self, params):
        """
        Description: Action to execute command
        Args:
            params: command lines params
        Returns:

        Raises:
            ConnectionError: self.request connection error
        """
        if params.s:
            src_or_bin = 'src'
        else:
            src_or_bin = 'bin'
        self._set_read_host(params.remote)

        _url = self.read_host + \
            '/packages/{src_or_bin}/{packagename}?database_name={database}&pkg_name={pkg_name}' \
                   .format(src_or_bin=src_or_bin, packagename=params.packagename, database=params.database,
                           pkg_name=params.packagename)
        try:
            response = self.request.get(_url)
        except ConnErr as conn_error:
            self.output_error_formatted(str(conn_error), "CONN_ERROR")
        else:
            if response.status_code == 200:
                try:
                    response_data = json.loads(response.text)
                    if response_data.get('code') == ResponseCode.SUCCESS:
                        if params.s:
                            self.__parse_src_package(
                                response_data, params.database, params.s)
                        else:
                            self.__parse_bin_package(
                                response_data, params.database, params.s)
                    else:
                        self.output_error_formatted(response_data.get('message'),
                                                    response_data.get('code'))
                except JSONDecodeError as json_error:
                    self.output_error_formatted(
                        response.text, "JSON_DECODE_ERROR")
            else:
                self.http_error(response)
