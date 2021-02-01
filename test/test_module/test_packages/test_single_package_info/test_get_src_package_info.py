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
test get src package info
"""
import unittest
import os
from unittest import mock
from mock import patch
from packageship.application.core. pkginfo.pkg import SourcePackage
from packageship.application.query.depend import BuildRequires, BeDependRequires, InstallRequires
from packageship.application.query.pkg import QueryPackage
from packageship.application.query import database
from test.base_code.read_mock_data import MockData

MOCK_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
TRUE_INSTALL_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "true_install_info.json"))
TRUE_SRC_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "true_src_info.json"))
WRONG_BUILD = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "wrong_build_info.json"))
EMPTY_SUBPACK_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "empty_subpack_src_info.json"))
BUILD_REQUIRES_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "build_requires_info.json"))
BE_DEPEND_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "be_depend_info.json"))
WRONG_BEDEPEND_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "wrong_be_depend_info.json"))
WRONG_INSTALL_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "wrong_install_info.json"))

class TestSrcPackageInfo(unittest.TestCase):
    """
    class for test src package detail info
    """

    def setUp(self) -> None:
        database.get_db_priority = mock.Mock(
            return_value=["openeuler", "fedora"])

    def test_database_not_exists(self):
        """
        test database does not exists

        """
        src_pkg = SourcePackage()
        res = src_pkg.src_package_info(["Judy"], ["openeuler1"])
        self.assertEqual(res, {}, "Error in testing database does not exists.")

    @patch.object(QueryPackage, "get_src_info")
    def test_get_empty_src_info(self, mock1):
        """
        test get empty src info

        """
        src_pkg = SourcePackage()
        mock1.return_value = {}
        res = src_pkg.src_package_info(["Judy"], ["openeuler"])
        self.assertEqual(res, {}, "Error in testing get empty src info.")

    @patch.object(QueryPackage, "get_src_info")
    def test_package_not_exists(self, mock1):
        """
        test package not exists

        """
        src_pkg = SourcePackage()
        mock1.return_value = {}
        res = src_pkg.src_package_info(["Judy1"], ["openeuler"])
        self.assertEqual(res, {}, "Error in testing package not exists.")

    @patch.object(QueryPackage, "get_src_info")
    def test_wrong_src_info(self, mock1):
        """
        test wrong src info

        """
        src_pkg = SourcePackage()
        mock1.return_value = {None}
        res = src_pkg.src_package_info(["Judy"], ["openeuler"])
        self.assertEqual(res, {}, "Error in testing wrong src info.")


    @patch.object(QueryPackage, "get_src_info")
    @patch.object(BuildRequires, "get_build_req")
    @patch.object(BeDependRequires, "get_be_req")
    @patch.object(InstallRequires, "get_install_req")
    def test_empty_build_info(self, mock1, mock2, mock3, mock4):
        """
        test empty build info

        """
        mock1.return_value = TRUE_INSTALL_INFO
        mock2.return_value = BE_DEPEND_INFO
        mock3.return_value = []
        mock4.return_value = TRUE_SRC_INFO
        src_pkg = SourcePackage()
        res = src_pkg.src_package_info(["Judy"], ["openeuler"])
        tmp = res["openeuler"][0]["buildrequired"]
        self.assertEqual(tmp, [], "Error in testing empty build info.")


    @patch.object(QueryPackage, "get_src_info")
    @patch.object(BuildRequires, "get_build_req")
    @patch.object(BeDependRequires, "get_be_req")
    @patch.object(InstallRequires, "get_install_req")
    def test_wrong_build_info(self, mock1, mock2, mock3, mock4):
        """
        test wrong build info

        """
        mock1.return_value = TRUE_INSTALL_INFO
        mock2.return_value = BE_DEPEND_INFO
        mock3.return_value = WRONG_BUILD
        mock4.return_value = TRUE_SRC_INFO
        src_pkg = SourcePackage()
        output_res = src_pkg.src_package_info(["Judy"], ["openeuler"])
        EXPECT_RES = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE,
                                                                 "wrong_build_for_res.json"))
        self.assertEqual(output_res, EXPECT_RES, "Error in testing wrong build info.")

    @patch.object(QueryPackage, "get_src_info")
    @patch.object(BuildRequires, "get_build_req")
    def test_empty_subpack_info(self, mock1, mock2):
        """
        test empty subpack info

        """
        mock1.return_value = [None]
        mock2.return_value = EMPTY_SUBPACK_INFO
        src_pkg = SourcePackage()
        res = src_pkg.src_package_info(["Judy"], ["openeuler"])
        self.assertEqual(res["openeuler"][0]["subpacks"], [], "Error in testing empty subpack info.")

    @patch.object(QueryPackage, "get_src_info")
    @patch.object(BuildRequires, "get_build_req")
    @patch.object(BeDependRequires, "get_be_req")
    @patch.object(InstallRequires, "get_install_req")
    def test_empty_provides_info(self, mock1, mock2, mock3, mock4):
        """
        test empty provides info

        """
        mock1.return_value = TRUE_INSTALL_INFO
        mock2.return_value = []
        mock3.return_value = BUILD_REQUIRES_INFO
        mock4.return_value = TRUE_SRC_INFO
        src_pkg = SourcePackage()
        res = src_pkg.src_package_info(["Judy"], ["openeuler"])
        output_provides = res["openeuler"][0]["subpacks"][0]["provides"]
        self.assertEqual(output_provides, [], "Error in testing empty provides info.")

    @patch.object(QueryPackage, "get_src_info")
    @patch.object(BuildRequires, "get_build_req")
    @patch.object(BeDependRequires, "get_be_req")
    @patch.object(InstallRequires, "get_install_req")
    def test_wrong_bedepend_info(self, mock1, mock2, mock3, mock4):
        """
        test wrong bedepend info

        """
        mock1.return_value = TRUE_INSTALL_INFO
        mock2.return_value = WRONG_BEDEPEND_INFO
        mock3.return_value = BUILD_REQUIRES_INFO
        mock4.return_value = TRUE_SRC_INFO
        src_pkg = SourcePackage()
        output_res = src_pkg.src_package_info(["Judy"])
        EXPECT_RES = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE,
                                                                 "wrong_depend_for_res.json"))
        self.assertEqual(output_res, EXPECT_RES, "Error in testing wrong bedepend info.")

    @patch.object(QueryPackage, "get_src_info")
    @patch.object(BuildRequires, "get_build_req")
    @patch.object(BeDependRequires, "get_be_req")
    @patch.object(InstallRequires, "get_install_req")
    def test_empty_install_info(self, mock1, mock2, mock3, mock4):
        """
        test empty install info

        """
        mock1.return_value = []
        mock2.return_value = BE_DEPEND_INFO
        mock3.return_value = BUILD_REQUIRES_INFO
        mock4.return_value = TRUE_SRC_INFO
        src_pkg = SourcePackage()
        output_res = src_pkg.src_package_info(["Judy"], ["openeuler"])
        EMPTY_INSTALL_RES = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE,
                                                                 "empty_install_for_res.json"))
        self.assertEqual(output_res, EMPTY_INSTALL_RES, "Error in testing empty install info.")


    @patch.object(QueryPackage, "get_src_info")
    @patch.object(BuildRequires, "get_build_req")
    @patch.object(BeDependRequires, "get_be_req")
    @patch.object(InstallRequires, "get_install_req")
    def test_wrong_install_info(self, mock1, mock2, mock3, mock4):
        """
        test wrong install info
        """
        mock1.return_value = WRONG_INSTALL_INFO
        mock2.return_value = BE_DEPEND_INFO
        mock3.return_value = BUILD_REQUIRES_INFO
        mock4.return_value = TRUE_SRC_INFO
        src_pkg = SourcePackage()
        output_res = src_pkg.src_package_info(["Judy"], ["openeuler"])
        EMPTY_INSTALL_RES = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE,
                                                                 "wrong_install_for_res.json"))
        self.assertEqual(output_res, EMPTY_INSTALL_RES, "Error in testing wrong install info.")

    @patch.object(QueryPackage, "get_src_info")
    @patch.object(BuildRequires, "get_build_req")
    @patch.object(BeDependRequires, "get_be_req")
    @patch.object(InstallRequires, "get_install_req")
    def test_true_install_info(self, mock1, mock2, mock3, mock4):
        """
        test true install info

        Returns:

        """
        mock1.return_value = TRUE_INSTALL_INFO
        mock2.return_value = BE_DEPEND_INFO
        mock3.return_value = BUILD_REQUIRES_INFO
        mock4.return_value = TRUE_SRC_INFO
        src_pkg = SourcePackage()
        output_res = src_pkg.src_package_info(["Judy"], ["openeuler"])
        TRUE_INSTALL_RES = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE,
                                                                 "true_install_for_res.json"))
        self.assertDictEqual(output_res, TRUE_INSTALL_RES, "Error in testing true install info.")
    #
    @patch.object(QueryPackage, "get_src_info")
    @patch.object(BuildRequires, "get_build_req")
    @patch.object(BeDependRequires, "get_be_req")
    @patch.object(InstallRequires, "get_install_req")
    def test_true_result_with_input_database(self, mock1, mock2, mock3, mock4):
        """
        test true result with input database

        """
        mock1.return_value = TRUE_INSTALL_INFO
        mock2.return_value = BE_DEPEND_INFO
        mock3.return_value = BUILD_REQUIRES_INFO
        mock4.return_value = TRUE_SRC_INFO
        src_pkg = SourcePackage()
        output_res = src_pkg.src_package_info(["Judy"], ["openeuler"])
        EXPECT_RES = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE,
                                                                 "true_result_with_input_database.json"))
        self.assertEqual(output_res, EXPECT_RES, "Error in testing true result with input database.")

