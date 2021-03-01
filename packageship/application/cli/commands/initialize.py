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
Class: InitDatabaseCommand
"""
import os
from packageship.application.cli.base import BaseCommand
from packageship.application.initialize.integration import InitializeService
from packageship.application.common.exc import InitializeError, ResourceCompetitionError


class InitDatabaseCommand(BaseCommand):
    """
    Description: Initialize database command
    Attributes:
        parse: Command line parsing example
        params: Command line parameters
    """

    def __init__(self):
        """
        Description: Class instance initialization
        """
        super(InitDatabaseCommand, self).__init__()
        self.parse = BaseCommand.subparsers.add_parser(
            'init', help='initialization of the database')
        self.params = [
            ('-filepath', 'str', 'specify the path of conf.yaml', '', 'store')]

    def register(self):
        """
        Description: Command line parameter injection
        Args:

        Returns:

        Raises:

        """
        super(InitDatabaseCommand, self).register()
        self.parse.set_defaults(func=self.do_command)

    def do_command(self, params):
        """
        Description: Action to execute command
        Args:
            params: Command line parameters
        Returns:

        Raises:

        """
        if os.getlogin() not in ["root", "pkgshipuser"]:
            print("The current user does not have initial execution permission")
            return
        init = InitializeService()
        file_path = params.filepath
        if file_path:
            file_path = os.path.abspath(file_path)
        try:
            init.import_depend(path=file_path)
        except (InitializeError, ResourceCompetitionError) as error:
            print(error)
        else:
            if init.success:
                print('Database initialize success')
            else:
                print('%s initialize failed' % ','.join(init.fail))
