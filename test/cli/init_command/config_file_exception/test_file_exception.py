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
from test.cli.init_command import InitTestBase
from packageship.application.initialize.integration import del_temporary_file, RepoConfig


SRC_FILE_NONE = """
- dbname: openeuler
  src_db_file:
  bin_db_file: https://mirrors.huaweicloud.com/fedora/releases/30/Everything/aarch64/os/
  priority: 2
"""

BIN_FILE_NONE = """
- dbname: openeuler
  src_db_file: https://mirrors.huaweicloud.com/fedora/releases/30/Everything/source/tree/
  bin_db_file:
  priority: 2
"""

SRC_FILE_ERROR = """
- dbname: openeuler
  src_db_file: /ROOT/openeuler
  bin_db_file: https://mirrors.huaweicloud.com/fedora/releases/30/Everything/aarch64/os/
  priority: 2
"""

BIN_FILE_ERROR = """
- dbname: openeuler
  src_db_file: https://mirrors.huaweicloud.com/fedora/releases/30/Everything/source/tree/
  bin_db_file: /ROOT/openeuler
  priority: 2
"""

RIGHT_FILE_CONFIG = """
- dbname: openeuler
  src_db_file: https://mirrors.huaweicloud.com/fedora/releases/30/Everything/source/tree/
  bin_db_file: file:///mirrors.huaweicloud.com/fedora/releases/30/Everything/aarch64/os/
  priority: 2
"""


class FileException(InitTestBase):
    """Exception for 'file' in configuration file"""
    _dirname = os.path.dirname(__file__)

    def setUp(self):
        super(FileException, self).setUp()
        self._src_file_none = self.create_conf_file(
            content=SRC_FILE_NONE, path=self._create_file_path)
        self._bin_file_none = self.create_conf_file(
            content=BIN_FILE_NONE, path=self._create_file_path)
        self._src_file_error = self.create_conf_file(
            content=SRC_FILE_ERROR, path=self._create_file_path)
        self._bin_file_error = self.create_conf_file(
            content=BIN_FILE_ERROR, path=self._create_file_path)
        self._right_file_config = self.create_conf_file(
            content=RIGHT_FILE_CONFIG, path=self._create_file_path)

        self._repo_config = RepoConfig()

    def test_src_file_none(self):
        """
        source file is none
        """
        self._repo_config.load_config(path=self._src_file_none)
        self.assertEqual(False, self._repo_config.validate)

    def test_src_file_error(self):
        """
        source file is error
        """
        self._repo_config.load_config(path=self._src_file_error)
        self.assertEqual(False, self._repo_config.validate)

    def test_bin_file_none(self):
        """
        binary file is none
        """
        self._repo_config.load_config(path=self._bin_file_none)
        self.assertEqual(False, self._repo_config.validate)

    def test_bin_file_error(self):
        """
        binary file is error
        """
        self._repo_config.load_config(path=self._bin_file_error)
        self.assertEqual(False, self._repo_config.validate)

    def test_right_file(self):
        """
        right config file
        """
        self._repo_config.load_config(path=self._right_file_config)
        self.assertEqual(True, self._repo_config.validate)

    def tearDown(self) -> None:
        folder = os.path.join(self._dirname, "conf")
        del_temporary_file(path=folder, folder=True)
