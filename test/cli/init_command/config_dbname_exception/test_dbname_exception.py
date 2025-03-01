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
from packageship.application.initialize.integration import InitializeService, InitializeError
from packageship.application.initialize.base import del_temporary_file


DBNAME_NONE = """
- dbname:
  src_db_file: https://mirrors.huaweicloud.com/fedora/releases/30/Everything/source/tree/
  bin_db_file: https://mirrors.huaweicloud.com/fedora/releases/30/Everything/aarch64/os/
  priority: 2
"""

DBNAME_UPPER = """
- dbname: openEuler
  src_db_file: https://mirrors.huaweicloud.com/fedora/releases/30/Everything/source/tree/
  bin_db_file: https://mirrors.huaweicloud.com/fedora/releases/30/Everything/aarch64/os/
  priority: 2
"""

DBNAME_NOT_EXISTS = """
- src_db_file: https://mirrors.huaweicloud.com/fedora/releases/30/Everything/source/tree/
  bin_db_file: https://mirrors.huaweicloud.com/fedora/releases/30/Everything/aarch64/os/
  priority: 2
"""

DBNAME_REPEAT = """
- dbname: openeuler
  src_db_file: https://mirrors.huaweicloud.com/fedora/releases/30/Everything/source/tree/
  bin_db_file: https://mirrors.huaweicloud.com/fedora/releases/30/Everything/aarch64/os/
  priority: 2
- dbname: openeuler
  src_db_file: https://mirrors.huaweicloud.com/fedora/releases/30/Everything/source/tree/
  bin_db_file: https://mirrors.huaweicloud.com/fedora/releases/30/Everything/aarch64/os/
  priority: 1
"""


class DbnameException(InitTestBase):
    """database name is none"""
    _dirname = os.path.dirname(__file__)

    def setUp(self):
        super(DbnameException, self).setUp()
        self._dbname_none = self.create_file(
            write_content=DBNAME_NONE, path=self._create_file_path)
        self._dbname_upper = self.create_file(
            write_content=DBNAME_UPPER, path=self._create_file_path)
        self._dbname_not_exists = self.create_file(
            write_content=DBNAME_NOT_EXISTS, path=self._create_file_path)
        self._dbname_repeat = self.create_file(
            write_content=DBNAME_REPEAT, path=self._create_file_path)
        self._init_service = InitializeService()

    def test_dbname_none_exception(self):
        """
        Exception with database name None in configuration file
        """
        with self.assertRaises(InitializeError):
            self.init_service.import_depend(path=self._dbname_none)

    def test_dbname_upper_exception(self):
        """
        Exception in uppercase configuration file
        """
        with self.assertRaises(InitializeError):
            self.init_service.import_depend(path=self._dbname_upper)

    def test_dbname_not_exists_exception(self):
        """
        Database name does not exist in configuration file
        """
        with self.assertRaises(InitializeError):
            self.init_service.import_depend(path=self._dbname_not_exists)

    def test_dbname_repeat_exception(self):
        """
        Database name repeat in configuration file
        """
        with self.assertRaises(InitializeError):
            self.init_service.import_depend(path=self._dbname_repeat)

    def tearDown(self) -> None:
        folder = os.path.join(self._dirname, "tmp")
        shutil.rmtree(folder)
