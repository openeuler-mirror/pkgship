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
import shutil
import os
from packageship.application.core.baseinfo.pkg_version import get_pkgship_version
from packageship import BASE_PATH
try:
    spec_path = os.path.join(os.path.dirname(BASE_PATH), "pkgship.spec")
    shutil.copyfile(spec_path, spec_path + '.bak')
except FileNotFoundError:
    print("pkgship spec file does not exist.")


class TestVersionInfo(unittest.TestCase):
    """
    class for test get pkgship version and release info
    """

    def test_wrong_spec_path(self):
        """
        test not found database info response
        Returns:

        """
        try:
            os.remove(spec_path)
            version, release = get_pkgship_version()
            self.assertIsNone(
                version, "An error occurred when testing wrong spec path.")
            self.assertIsNone(
                version, "An error occurred when testing wrong spec path.")
        except (TypeError, FileNotFoundError):
            print("An error occurred when testing wrong spec path.")
        finally:
            if os.path.exists(spec_path + ".bak"):
                os.rename(spec_path + '.bak', spec_path)

    def test_true_result(self):
        """
        test_true_params_result
        Returns:

        """
        correct_version, correct_release = "1.1.0", "1"
        output_version, output_release = get_pkgship_version()
        self.assertEqual(correct_version, output_version,
                         msg="Error in getting pkgship version")
        self.assertEqual(correct_release, output_release,
                         msg="Error in getting pkgship release")

