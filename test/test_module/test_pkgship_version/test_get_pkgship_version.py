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
test get pkgship version and release info
"""
import unittest
import os

BASE_PATH = os.path.join(os.path.dirname(os.path.abspath(
        os.path.dirname(__file__))), "test_version")
version_path = os.path.join(os.path.dirname(BASE_PATH), "test_pkgship_version\\data\\", "version.yaml")
from packageship.application.core.baseinfo import pkg_version


class TestVersionInfo(unittest.TestCase):
    """
    class for test get pkgship version and release info
    """
    def test_file_not_exists(self):
        """
        test yaml not exists
        Returns:

        """
        output_version, output_release = pkg_version.get_pkgship_version()
        self.assertIsNone(output_version,
                         msg="Error in testing file not exists")
        self.assertIsNone(output_release,
                         msg="Error in testing file not exists")


    def test_true_result(self):
        """
        test_true_result
        Returns:

        """
        pkg_version.file_path = version_path
        correct_version, correct_release = "1.1.0", "1.oe1"
        output_version, output_release = pkg_version.get_pkgship_version()
        self.assertEqual(correct_version, output_version,
                         msg="Error getting pkgship version")
        self.assertEqual(correct_release, output_release,
                         msg="Error getting pkgship release")
