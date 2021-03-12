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
Class: PkgshipCommand
"""

try:
    from packageship.application.common.exc import Error
    from requests.exceptions import ConnectionError as ConnErr
    from packageship.application.cli.base import BaseCommand
except ImportError as import_error:
    print("Error importing related dependencies,"
          "please check if related dependencies are installed")
else:
    from packageship.application.common.constant import ResponseCode
    from packageship.application.common.constant import ListNode
    from packageship.application.common.constant import UWSIG_PATH
    from packageship.libs.terminal_table import TerminalTable
    from packageship.application.common.constant import ERROR_CON
    from packageship.application.cli.commands.allpkg import AllPackageCommand
    from packageship.application.cli.commands.bedepend import BeDependCommand
    from packageship.application.cli.commands.builddep import BuildDepCommand
    from packageship.application.cli.commands.selfdepend import SelfDependCommand
    from packageship.application.cli.commands.db import DbPriorityCommand
    from packageship.application.cli.commands.initialize import InitDatabaseCommand
    from packageship.application.cli.commands.installdep import InstallDepCommand
    from packageship.application.cli.commands.singlepkg import SingleCommand
    from packageship.application.cli.commands.version import VersionCommand


def main():
    """
    Description: Command line tool entry, register related commands

    Raises:
        Error: An error occurred while executing the command
    """
    try:
        packship_cmd = PkgshipCommand()
        packship_cmd.parser_args()
    except Error as error:
        print('Command execution error please try again')


class PkgshipCommand(BaseCommand):
    """
    Description: PKG package command line
    Attributes:
        statistics: Summarized data table
        table: Output table
        columns: Calculate the width of the terminal dynamically
        params: Command parameters
    """

    def __init__(self):
        """
        Description: Class instance initialization
        """
        super(PkgshipCommand, self).__init__()

    @classmethod
    def parser_args(cls):
        """
        Description: Register the command line and parse related commands
        Args:

        Returns:

        Raises:
            Error: An error occurred during command parsing
        """
        cls.register_command(InitDatabaseCommand())
        cls.register_command(AllPackageCommand())
        cls.register_command(BuildDepCommand())
        cls.register_command(InstallDepCommand())
        cls.register_command(SelfDependCommand())
        cls.register_command(BeDependCommand())
        cls.register_command(SingleCommand())
        cls.register_command(DbPriorityCommand())
        cls.register_command(VersionCommand())
        try:
            args = cls.parser.parse_args()
            args.func(args)
        except Error as error:
            print('The command execution failed due to:{}'.format(error))
