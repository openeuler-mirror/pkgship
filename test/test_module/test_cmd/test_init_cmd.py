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
# -*- coding:utf-8 -*-
"""
test_get_init_cmd
"""
import sys
import unittest
import argparse
from unittest import mock
from packageship.application.initialize.integration import InitializeService
from packageship.application.cli.commands.initialize import InitDatabaseCommand


class Redirect:
    _content = ""

    def write(self, s):
        self._content += s

    def flush(self):
        self._content = ""

    def getvalue(self):
        return self._content


class TestInit(unittest.TestCase):
    """
    class for test init
    """
    def setUp(self) -> None:
        self.r = Redirect()
        sys.stdout = self.r

    @mock.patch.object(InitializeService, "import_depend")
    def test_true_params(self, mock_import_depend):
        """
        test true params
        """
        parser = argparse.ArgumentParser()
        init_database = InitDatabaseCommand()
        mock_import_depend.return_value = {}
        parser.add_argument('-filepath')
        args = parser.parse_args(['-filepath', '"/etc/test_delete"'])
        init_database.do_command(args)
        c = self.r.getvalue().strip()
        s = 'Database initialize success'.strip()
        self.assertEqual(c, s)

    @mock.patch.object(InitializeService, "import_depend")
    def test_wrong_param(self, mock_import_depend):
        """
        test wrong param
        """
        with mock.patch("packageship.application.initialize.integration.InitializeService.success",
                        new_callable=mock.PropertyMock) as mock_success:
            parser = argparse.ArgumentParser()
            init_database = InitDatabaseCommand()
            mock_import_depend.return_value = {}
            mock_success.return_value = False
            parser.add_argument('-filepath')
            args = parser.parse_args(['-filepath', ''])
            init_database.do_command(args)
            c = self.r.getvalue().strip()
            s = 'initialize failed'.strip()
            self.assertEqual(c, s)
