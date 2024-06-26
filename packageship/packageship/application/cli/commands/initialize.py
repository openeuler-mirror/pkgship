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
import pwd

import os
import threading
import time

from packageship.application.cli.base import BaseCommand
from packageship.application.common.exc import InitializeError, ResourceCompetitionError


class InitServiceThread(threading.Thread):
    """
    Description: Execute the initialization thread
    """

    def __init__(self, func, param, *args, **kwargs):
        super(InitServiceThread, self).__init__(*args, **kwargs)
        self._func = func
        self._args = param
        self.error = False

    def run(self):
        try:
            self._func(*self._args)
        except (InitializeError, ResourceCompetitionError) as error:
            self.error = True
            print("\r", error)


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
            "init", help="initialization of the database"
        )
        self.params = [
            ("-filepath", "str", "specify the path of conf.yaml", "", "store")
        ]
        self._char = ["/", "-", "\\"]

    def register(self):
        """
        Description: Command line parameter injection
        Args:

        Returns:

        Raises:

        """
        super(InitDatabaseCommand, self).register()
        self.parse.set_defaults(func=self.do_command)

    @property
    def login_user(self):
        """
        Description: The user logged in to the system
        """
        return pwd.getpwuid(os.getuid())[0]

    def do_command(self, params):
        """
        Description: Action to execute command
        Args:
            params: Command line parameters
        Returns:

        Raises:

        """

        if self.login_user not in ["root", "pkgshipuser"]:
            print("The current user does not have initial execution permission")
            return
        # Determine whether the service is started
        if not self.is_service_start():
            print("The pkgship service is not started,please start the service first")
            return

        from packageship.application.initialize.integration import InitializeService

        init = InitializeService()
        file_path = params.filepath
        if file_path:
            file_path = os.path.abspath(file_path)

        _init_service_thread = InitServiceThread(
            func=init.import_depend, param=(file_path,)
        )
        _init_service_thread.setDaemon(True)
        _init_service_thread.start()

        while _init_service_thread.is_alive():
            for number in range(3):
                print(
                    "\r",
                    "initializing{}".format("." * 10),
                    self._char[number],
                    end="",
                    flush=True,
                )
                time.sleep(0.5)
        print(os.linesep)
        if not _init_service_thread.error:
            self._display_error(init)

    def _display_error(self, initialize_service):
        if initialize_service.success:
            print("Database initialize success", end=os.linesep)
        else:
            print(
                "Initialize failed database: %s" % " ".join(initialize_service.fail),
                end=os.linesep,
            )
        if initialize_service.remove_error:
            print("Remove database failed:", end=os.linesep)
            for database, message in initialize_service.remove_error.items():
                print("%s: %s" % (database, message), end=os.linesep)
        if initialize_service.reindex_error:
            print(
                os.linesep,
                "The database name changes but the content is the same during",
                " initialization,an error occurred while renaming the index:",
                end=os.linesep,
            )
            _reindex, del_index = [], []
            for reindex_error in initialize_service.reindex_error:
                _reindex.append(reindex_error["reindex"])
                del_index.extend(reindex_error["del_index"])
            print("Reindex failed:", end=os.linesep)
            print(os.linesep.join(_reindex))
            print(
                os.linesep,
                "Please manually delete the following databases:",
                end=os.linesep,
            )
            print(os.linesep.join(del_index))
