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
test get self_build depend info
"""
import unittest
import os
from unittest import mock
from mock import patch
from redis import Redis

from packageship.application.core.depend import SelfDepend
from packageship.application.query.depend import InstallRequires, BuildRequires
from packageship.application.query.pkg import QueryPackage
from test.base_code.read_mock_data import MockData

MOCK_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
TRUE_INSTALL_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "true_install_info.json"))
TRUE_BUILD_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "true_build_info.json"))
EXCEPT_SRC = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "except_src.json"))
EXCEPT_BIN = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "except_bin.json"))
BIN_NAME_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "bin_name_info.json"))
WRONG_UPDATE_DB = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "wrong_update_db_install.json"))
WRONG_UPDATE_DB_EXCEPT_BIN = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "wrong_update_db_except_bin.json"))
EMPTY_DB_SRC_NAME = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "empty_db_src_name.json"))
WRONG_BIN_NAME_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "wrong_bin_name_info.json"))

param = {
    "packagename": ["Judy"],
    "depend_type": "selfdep",
    "parameter": {
      "db_priority": ["openeuler"],
      "self_build": True,
      "packtype": "source",
      "with_subpack": True
    }
}


class TestSelfBuildDdepend(unittest.TestCase):
    """
    class for test self build depend info
    """

    @patch.object(QueryPackage, "get_bin_name")
    @patch.object(BuildRequires, "get_build_req")
    @patch.object(InstallRequires, "get_install_req")
    def test_with_wrong_subpack(self, mock1, mock2, mock3):
        """
        test with wrong subpack

        """
        mock1.return_value = TRUE_INSTALL_INFO
        mock2.return_value = TRUE_BUILD_INFO
        mock3.return_value = [None]
        self_depend = SelfDepend(db_list=['openeuler'])
        self_depend.self_depend(pkg_name=["Judy"], pkgtype="source")
        binary, source = self_depend.depend_dict
        self.assertDictEqual(binary, {}, "Error in testing wrong subpack.")
        self.assertDictEqual(source, {}, "Error in testing wrong subpack.")



    @patch.object(QueryPackage, "get_bin_name")
    @patch.object(BuildRequires, "get_build_req")
    @patch.object(InstallRequires, "get_install_req")
    def test_with_empty_subpack(self, mock1, mock2, mock3):
        """
        test with empty subpack

        """
        mock1.return_value = TRUE_INSTALL_INFO
        mock2.return_value = TRUE_BUILD_INFO
        mock3.return_value = []
        self_depend = SelfDepend(db_list=['openeuler'])
        self_depend.self_depend(pkg_name=["Judy"], pkgtype="source")
        binary, source = self_depend.depend_dict
        self.assertEqual(binary, {}, "Error in testing empty subpack.")
        self.assertEqual(source, {}, "Error in testing empty subpack.")



    @patch.object(QueryPackage, "get_bin_name")
    @patch.object(BuildRequires, "get_build_req")
    @patch.object(InstallRequires, "get_install_req")
    def test_with_true_subpack(self, mock1, mock2, mock3):
        """
        test true subpack

        """
        mock1.return_value = TRUE_INSTALL_INFO
        mock2.return_value = TRUE_BUILD_INFO
        mock3.return_value = BIN_NAME_INFO
        self_depend = SelfDepend(db_list=['openeuler'])
        self_depend.self_depend(pkg_name=["Judy"], pkgtype="source", with_subpack=True)
        binary, source = self_depend.depend_dict
        binary["Judy"]["install"] = sorted(binary["Judy"]["install"])
        self.assertDictEqual(binary, EXCEPT_BIN, "Error in testing true subpack.")
        self.assertDictEqual(source, EXCEPT_SRC, "Error in testing true subpack.")


    @patch.object(QueryPackage, "get_bin_name")
    @patch.object(BuildRequires, "get_build_req")
    @patch.object(InstallRequires, "get_install_req")
    def test_empty_db_src_name(self, mock1, mock2, mock3):
        """
        test empty db src name

        """
        mock1.return_value = TRUE_INSTALL_INFO
        mock2.return_value = TRUE_BUILD_INFO
        mock3.return_value = WRONG_BIN_NAME_INFO
        self_depend = SelfDepend(db_list=['openeuler'])
        self_depend.self_depend(pkg_name=["Judy"], pkgtype="source", with_subpack=True)
        binary, source = self_depend.depend_dict
        self.assertDictEqual(binary, {}, "Error in empty db src name.")
        self.assertDictEqual(source, {}, "Error in empty db src name.")


    @patch.object(BuildRequires, "get_build_req")
    @patch.object(InstallRequires, "get_install_req")
    def test_wrong_update_db(self, mock1, mock2):
        """
        test wrong update db

        """
        mock1.return_value = WRONG_UPDATE_DB
        mock2.return_value = TRUE_BUILD_INFO
        self_depend = SelfDepend(db_list=['openeuler', 'fedora30'])
        self_depend.self_depend(pkg_name=["Judy"])
        binary, source = self_depend.depend_dict
        binary["Judy"]["install"] = sorted(binary["Judy"]["install"])
        EXPECT_SRC = {'Judy': {'name': 'Judy', 'version': '1.0.5', 'database': 'openeuler1'}}
        self.assertDictEqual(binary, WRONG_UPDATE_DB_EXCEPT_BIN, "Error in testing wrong update db.")
        self.assertDictEqual(source, EXPECT_SRC, "Error in testing wrong update db.")


    @patch.object(BuildRequires, "get_build_req")
    @patch.object(InstallRequires, "get_install_req")
    def test_true_result(self, mock1, mock2):
        """
        test true result

        """
        mock1.return_value = TRUE_INSTALL_INFO
        mock2.return_value = TRUE_BUILD_INFO
        self_depend = SelfDepend(db_list=['openeuler', 'fedora30'])
        self_depend.self_depend(pkg_name=["Judy"])
        binary, source = self_depend.depend_dict
        binary["Judy"]["install"] = sorted(binary["Judy"]["install"])
        self.assertDictEqual(binary, EXCEPT_BIN, "Error in testing true result.")
        self.assertDictEqual(source, EXCEPT_SRC, "Error in testing true result.")

    def test_wrong_package_type(self):
        """
        test wrong package type

        """
        with self.assertRaises(AttributeError):
            self_depend = SelfDepend(db_list=['openeuler'])
            self_depend.self_depend(pkg_name="Judy")


    def test_empty_dblist(self):
        """
        test empty dblist

        """
        with self.assertRaises(AttributeError):
            self_depend = SelfDepend(db_list=[])
            self_depend.self_depend(pkg_name="Judy")


    @mock.patch.object(Redis, "exists")
    def test_call_func_with_true_param(self, mock1):
        """
        test with redis

        """
        mock1.side_effect = [
            False,
            False,
            False,
            False
        ]
        InstallRequires.get_install_req = mock.Mock(return_value=TRUE_INSTALL_INFO)
        BuildRequires.get_build_req = mock.Mock(return_value=TRUE_BUILD_INFO)
        QueryPackage.get_bin_name = mock.Mock(return_value=BIN_NAME_INFO)
        self_depend = SelfDepend(db_list=['openeuler'])
        self_depend(**param)
        binary, source = self_depend.depend_dict
        binary["Judy"]["install"] = sorted(binary["Judy"]["install"])
        self.assertDictEqual(binary, EXCEPT_BIN, "Error in testing with redis.")
        self.assertDictEqual(source, EXCEPT_SRC, "Error in testing with redis.")
