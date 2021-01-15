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
from unittest import mock
from test.test_module.test_packages.mock_db_data.read_mock_data import MockData
from mock import patch
from packageship.application.core. pkginfo.pkg import Package
from packageship.application.query.pkg import QueryPackage
from packageship.application.query import database

pkg = Package()


class TestAllSrcPackage(unittest.TestCase):
    """
    class for test all src package
    """

    def setUp(self) -> None:
        database.get_db_priority = mock.Mock(
            return_value=["openeuler", "fedora"])

    def test_wrong_parameters(self):
        """
        test wrong parameters

        """
        res = pkg.all_src_packages("openEuler1", page_num=1, page_size=20)
        self.assertEqual(res, {}, "Error in testing wrong parameter.")

        res = pkg.all_src_packages("openeuler", page_num=0, page_size=1)
        self.assertEqual(res, {}, "Error in testing wrong parameter.")

        res = pkg.all_src_packages("openeuler", page_num=1, page_size=0)
        self.assertEqual(res, {}, "Error in testing wrong parameter.")

        res = pkg.all_src_packages("openeuler", page_num="a", page_size=0)
        self.assertEqual(res, {}, "Error in testing wrong parameter.")

        res = pkg.all_src_packages("openeuler", page_num=1, page_size=201)
        self.assertEqual(res, {}, "Error in testing wrong parameter.")

    @patch.object(QueryPackage, "get_src_info")
    def test_get_empty_src_info(self, mock1):
        """
        test get empty src info

        """
        mock1.return_value = {}
        res = pkg.all_src_packages("openeuler", page_num=1, page_size=20)
        self.assertEqual(res, {}, "Error in testing empty src info result.")

    @patch.object(QueryPackage, "get_src_info")
    def test_wrong_src_info(self, mock1):
        """
        test wrong src info

        """
        mock1.return_value = {"total": 2}
        res = pkg.all_src_packages("openeuler", page_num=1, page_size=20)
        self.assertEqual(res, {}, "Error in testing wrong src info result.")

    @patch.object(QueryPackage, "get_src_info")
    def test_true_result(self, mock1):
        """
        test true result

        """
        mock1.return_value = MockData.read_mock_data("all_src_package.json")
        res = pkg.all_src_packages("openeuler", page_num=1, page_size=20)
        self.assertNotEqual(res, {}, "Error in testing true response.")


if __name__ == '__main__':
    unittest.main()
