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
test get all bin package
"""
import os
import unittest
from unittest import mock
from mock import patch

from packageship.application.common.exc import ParametersError
from packageship.application.core. pkginfo.pkg import Package
from packageship.application.query.pkg import QueryPackage
from packageship.application.query import database
from test.base_code.read_mock_data import MockData

pkg = Package()
MOCK_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

class TestAllBinPackage(unittest.TestCase):
    """
    class for test all bin package
    """

    def setUp(self) -> None:
        database.get_db_priority = mock.Mock(
            return_value=["openeuler", "fedora"])

    def test_wrong_parameters(self):
        """
        test not found database info response
        Returns:

        """
        with self.assertRaises(ParametersError):
            pkg.all_bin_packages("openEuler1", page_num=1, page_size=20)

        with self.assertRaises(ParametersError):
            pkg.all_bin_packages("openeuler", page_num=0, page_size=1)

        with self.assertRaises(ParametersError):
            pkg.all_bin_packages("openeuler", page_num=1, page_size=0)

        with self.assertRaises(ParametersError):
            pkg.all_bin_packages("openeuler", page_num="a", page_size=0)

        with self.assertRaises(ParametersError):
            pkg.all_bin_packages("openeuler", page_num=1, page_size=201)

        with self.assertRaises(ParametersError):
            pkg.all_bin_packages("openeuler", page_num=1, page_size=1, command_line="111")

    @patch.object(QueryPackage, "get_bin_info")
    def test_get_empty_bin_info(self, mock1):
        """
        test empty bin info
        Returns:

        """
        mock1.return_value = {}
        res = pkg.all_bin_packages("openeuler", page_num=1, page_size=20)
        self.assertEqual(res, {}, "Error in testing empty bin info.")

    @patch.object(QueryPackage, "get_bin_info")
    def test_wrong_bin_info(self, mock1):
        """
        test wrong bin info
        Returns:

        """
        mock1.return_value = {"total": 2}
        res = pkg.all_bin_packages("openeuler", page_num=1, page_size=20)
        self.assertEqual(res, {}, "Error in testing wrong bin info.")

    @patch.object(QueryPackage, "get_bin_info")
    def test_true_result(self, mock1):
        """
        test true result
        Returns:

        """
        ALL_BIN_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "all_bin_package_info.json"))
        mock1.return_value = ALL_BIN_INFO
        res = pkg.all_bin_packages("openeuler", page_num=1, page_size=20)
        self.assertNotEqual(res, {}, "Error in testing true response.")
