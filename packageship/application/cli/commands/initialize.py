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
import random
import time
import pwd
import threading
from packageship.application.cli.base import BaseCommand
from packageship.application.common.exc import InitializeError, ResourceCompetitionError


class PrintThread(threading.Thread):
    """
    Description: Print Thread
    Attributes:

    """

    def __init__(self, *args, **kwargs):
        super(PrintThread, self).__init__(*args, **kwargs)
        self.__clear = False

    def run(self):
        while True:
            print("\r", "initializing{}".format(
                "." * random.randint(1, 4)), end='', flush=True)
            time.sleep(0.5)
            if self.__clear:
                break

    def stop(self):
        self.__clear = True


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

        def get_username():
            return pwd.getpwuid(os.getuid())[0]

        if get_username() not in ["root", "pkgshipuser"]:
            print("The current user does not have initial execution permission")
            return

        from packageship.application.initialize.integration import InitializeService
        init = InitializeService()
        file_path = params.filepath
        if file_path:
            file_path = os.path.abspath(file_path)
        try:
            print_t = PrintThread()
            print_t.start()
            init.import_depend(path=file_path)
            print_t.stop()
        except (InitializeError, ResourceCompetitionError) as error:
            print('\r', error)
        else:
            if init.success:
                print('\r', 'Database initialize success')
            else:
                print('\r', '%s initialize failed' % ','.join(init.fail))
