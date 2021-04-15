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
import os
import shutil
from test.cli.init_command import InitTestBase
from packageship.application.initialize.integration import RepoConfig


PRIORITY_NOT_INT = """
- dbname: openeuler
  src_db_file: https://mirrors.huaweicloud.com/fedora/releases/30/Everything/source/tree/
  bin_db_file: file:///mirrors.huaweicloud.com/fedora/releases/30/Everything/aarch64/os/
  priority: priority
"""

PRIORITY_IS_ZERO = """
- dbname: openeuler
  src_db_file: https://mirrors.huaweicloud.com/fedora/releases/30/Everything/source/tree/
  bin_db_file: file:///mirrors.huaweicloud.com/fedora/releases/30/Everything/aarch64/os/
  priority: 0
"""

PRIORITY_IS_DECIMAL = """
- dbname: openeuler
  src_db_file: https://mirrors.huaweicloud.com/fedora/releases/30/Everything/source/tree/
  bin_db_file: file:///mirrors.huaweicloud.com/fedora/releases/30/Everything/aarch64/os/
  priority: 1.5
"""

PRIORITY_G_100 = """
- dbname: openeuler
  src_db_file: https://mirrors.huaweicloud.com/fedora/releases/30/Everything/source/tree/
  bin_db_file: file:///mirrors.huaweicloud.com/fedora/releases/30/Everything/aarch64/os/
  priority: 101
"""

PRIORITY_RIGHT = """
- dbname: openeuler
  src_db_file: https://mirrors.huaweicloud.com/fedora/releases/30/Everything/source/tree/
  bin_db_file: file:///mirrors.huaweicloud.com/fedora/releases/30/Everything/aarch64/os/
  priority: 1
"""


class PriorityException(InitTestBase):
    """Exception testing for database priority"""
    _dirname = os.path.dirname(__file__)

    def setUp(self):
        super(PriorityException, self).setUp()
        self._priority_not_int = self.create_file(
            write_content=PRIORITY_NOT_INT, path=self._create_file_path)
        self._priority_is_zero = self.create_file(
            write_content=PRIORITY_IS_ZERO, path=self._create_file_path)
        self._priority_is_decimal = self.create_file(
            write_content=PRIORITY_IS_DECIMAL, path=self._create_file_path)
        self._priority_g_100 = self.create_file(
            write_content=PRIORITY_G_100, path=self._create_file_path)
        self._priority_right = self.create_file(
            write_content=PRIORITY_RIGHT, path=self._create_file_path)

        self._repo_config = RepoConfig()

    def test_priority_not_int(self):
        """
        Priority is not an integer
        """
        self._repo_config.load_config(path=self._priority_not_int)
        self.assertEqual(False, self._repo_config.validate)

    def test_priority_is_zero(self):
        """
        The priority is zero
        """
        self._repo_config.load_config(path=self._priority_is_zero)
        self.assertEqual(False, self._repo_config.validate)

    def test_priority_is_decimal(self):
        """
        The priority is a decimal type
        """
        self._repo_config.load_config(path=self._priority_is_decimal)
        self.assertEqual(False, self._repo_config.validate)

    def test_priority_g_100(self):
        """
        Priority is higher than 100
        """
        self._repo_config.load_config(path=self._priority_g_100)
        self.assertEqual(False, self._repo_config.validate)

    def test_priority_right(self):
        """
        Proper priority configuration
        """
        self._repo_config.load_config(path=self._priority_right)
        self.assertEqual(True, self._repo_config.validate)

    def tearDown(self) -> None:
        folder = os.path.join(self._dirname, "tmp")
        shutil.rmtree(folder)
