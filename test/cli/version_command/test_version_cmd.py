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
test_get_pkgship_version
"""
import os
from pathlib import Path
from packageship.application.cli.commands.version import VersionCommand
from packageship.application.core.baseinfo import pkg_version
from test.cli.version_command import VersionTest

MOCK_DATA_FOLDER = str(Path(Path(__file__).parents[2], "mock_data"))



class TestVersion(VersionTest):
    """
    class for test pkgship version
    """
    cmd_class = VersionCommand

    def test_true_params(self):
        """
        test true params
        """
        self.excepted_str = """
Version:2.1.0
Release:7.oe1
        """
        pkg_version.file_path = os.path.join(MOCK_DATA_FOLDER, "version.yaml")
        self.command_params = ["-v"]
        self.assert_result()

    def test_file_not_exists(self):
        """
        test yaml file not exists
        """
        self.excepted_str = """
ERROR_CONTENT  :get pkgship version failed
HINT           :Make sure the file is valid
        """
        pkg_version.file_path = os.path.join(MOCK_DATA_FOLDER, "tmp_version.yaml")
        self.command_params = ["-v"]
        self.assert_result()
