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
test get binary package info
"""
import unittest
import os
from unittest import mock
from mock import patch

from packageship.application.common.exc import DatabaseConfigException, ElasticSearchQueryException
from packageship.application.core.pkginfo.pkg import BinaryPackage
from packageship.application.query.depend import BeDependRequires, InstallRequires
from packageship.application.query.pkg import QueryPackage
from packageship.application.query import database
from test.base_code.read_mock_data import MockData

MOCK_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
TRUE_INSTALL_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "true_install_info.json"))
TRUE_BIN_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "true_bin_info.json"))
BUILD_REQUIRES_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "build_requires_info.json"))
BE_DEPEND_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "be_depend_info.json"))
EMPTY_FILELIST_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "empty_filelist_info.json"))
WRONG_TYPE_FILELIST_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "wrong_type_filelist_info.json"))
ERROR_FILELIST_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "error_filelist_info.json"))

class TestSrcPackageInfo(unittest.TestCase):
    """
    class for test src package detail info
    """

    def setUp(self) -> None:
        database.get_db_priority = mock.Mock(
            return_value=["openeuler", "fedora"])


    @patch.object(QueryPackage, "get_bin_info")
    def test_get_empty_bin_info(self, mock1):
        """
        test get empty bin info

        """
        mock1.return_value = {}
        bin_pkg = BinaryPackage()
        res = bin_pkg.bin_package_info(["Judy"], ["openeuler"])
        self.assertEqual(res, {}, "Error in testing get empty bin info.")

    @patch.object(QueryPackage, "get_bin_info")
    def test_wrong_bin_info(self, mock1):
        """
        test get wrong bin info

        """
        mock1.return_value = {None}
        bin_pkg = BinaryPackage()
        res = bin_pkg.bin_package_info(["Judy"], ["openeuler"])
        self.assertEqual(res, {}, "Error in testing wrong bin info.")

    @patch.object(QueryPackage, "get_bin_info")
    @patch.object(BeDependRequires, "get_be_req")
    @patch.object(InstallRequires, "get_install_req")
    def test_empty_filelist(self, mock1, mock2, mock3):
        """
        test empty filelist

        Returns:

        """
        mock1.return_value = TRUE_INSTALL_INFO
        mock2.return_value = BE_DEPEND_INFO
        mock3.return_value = EMPTY_FILELIST_INFO
        bin_pkg = BinaryPackage()
        output_res = bin_pkg.bin_package_info(["Judy"], ["openeuler"])
        EXPECT_RES = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE,
                                                                 "empty_filelist_for_res.json"))
        self.assertEqual(output_res, EXPECT_RES, "Error in testing empty filelist info.")


    @patch.object(QueryPackage, "get_bin_info")
    @patch.object(BeDependRequires, "get_be_req")
    @patch.object(InstallRequires, "get_install_req")
    def test_error_filelist(self, mock1, mock2, mock3):
        """
        test error filelist info

        Returns:

        """
        mock1.return_value = TRUE_INSTALL_INFO
        mock2.return_value = BE_DEPEND_INFO
        mock3.return_value = ERROR_FILELIST_INFO
        bin_pkg = BinaryPackage()
        output_res = bin_pkg.bin_package_info(["Judy"], ["openeuler"])
        EXPECT_RES = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE,
                                                                 "empty_filelist_for_res.json"))
        self.assertEqual(output_res, EXPECT_RES, "Error in testing error filelist info.")

    @patch.object(QueryPackage, "get_bin_info")
    @patch.object(BeDependRequires, "get_be_req")
    @patch.object(InstallRequires, "get_install_req")
    def test_wrong_type_filelist(self, mock1, mock2, mock3):
        """
        test wrong type filelist

        Returns:

        """
        mock1.return_value = TRUE_INSTALL_INFO
        mock2.return_value = BE_DEPEND_INFO
        mock3.return_value = WRONG_TYPE_FILELIST_INFO
        bin_pkg = BinaryPackage()
        output_res = bin_pkg.bin_package_info(["Judy"], ["openeuler"])
        EXPECT_RES = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE,
                                                                 "empty_filelist_for_res.json"))
        self.assertEqual(output_res, EXPECT_RES, "Error in testing wrong type filelist info.")

    @patch.object(QueryPackage, "get_bin_info")
    @patch.object(BeDependRequires, "get_be_req")
    @patch.object(InstallRequires, "get_install_req")
    def test_true_bin_info(self, mock1, mock2, mock3):
        """
        test true binary info

        Returns:

        """
        mock1.return_value = TRUE_INSTALL_INFO
        mock2.return_value = BE_DEPEND_INFO
        mock3.return_value = TRUE_BIN_INFO
        bin_pkg = BinaryPackage()
        output_res = bin_pkg.bin_package_info(["Judy"])
        EXPECT_RES = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE,
                                                                 "true_bin_for_res.json"))
        self.assertEqual(output_res, EXPECT_RES, "Error in testing true binary info.")

    @mock.patch.object(QueryPackage, "get_bin_info")
    def test_config_exception(self, mock1):
        """
        test config exception

        """
        with self.assertRaises(DatabaseConfigException):
            mock1.side_effect = DatabaseConfigException()
            src_pkg = BinaryPackage()
            res = src_pkg.bin_package_info(["Judy"], ["openeuler"])
            self.assertEqual(res, {}, "Error in testing config exception.")

    @mock.patch.object(QueryPackage, "get_bin_info")
    def test_es_query_exception(self, mock1):
        """
        test es query exception
        Returns:

        """
        with self.assertRaises(ElasticSearchQueryException):
            mock1.side_effect = ElasticSearchQueryException()
            src_pkg = BinaryPackage()
            res = src_pkg.bin_package_info(["Judy"], ["openeuler"])
            self.assertEqual(res, {}, "Error in testing es query exception.")

