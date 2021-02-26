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
test get install depend info
"""
import unittest
import os
from unittest import mock

from mock import patch
from redis import Redis

from packageship.application.core.depend import InstallDepend
from packageship.application.query.depend import InstallRequires
from test.base_code.read_mock_data import MockData

MOCK_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
TRUE_INSTALL_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "true_install_info.json"))
WRONG_INSTALL_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "wrong_install_info.json"))
EXCEPT_BIN = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "expect_bin.json"))
EXCEPT_SRC = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "expect_src.json"))
PARAM_EXP_BIN = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "params_with_expect_bin.json"))
PARAM_EXP_SRC = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "params_with_expect_src.json"))
EMPTY_REQUIRES = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "empty_require_install_info.json"))
LEVEL_1_EXP_BIN = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "level_1_expect_bin.json"))
LEVEL_1_EXP_SRC = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "level_1_expect_src.json"))
REQUIRE_EXPECT_BIN = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "empty_require_except_bin.json"))
REQUIRE_EXCEPT_SRC = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "empty_require_except_src.json"))

param = {
    "packagename": ["Judy"],
    "depend_type": "installdep",
    "parameter": {
        "db_priority": ["openeuler"],
        "level": 2
    }
}


class TestInstallDdepend(unittest.TestCase):
    """
    class for test install depend info
    """

    @patch.object(InstallRequires, "get_install_req")
    def test_package_not_exists(self, mock1):
        """
        test package not exists

        """
        mock1.return_value = []
        install = InstallDepend(db_list=['openeuler'])
        install.install_depend(bin_name=["Judy111"])
        binary, source = install.depend_dict
        self.assertEqual(binary, {}, "Error in testing package not exists.")
        self.assertEqual(source, {}, "Error in testing package not exists.")


    @patch.object(InstallRequires, "get_install_req")
    def test_empty_requires(self, mock1):
        """
        test empty requires

        """
        mock1.return_value = EMPTY_REQUIRES
        install = InstallDepend(db_list=['openeuler'])
        install.install_depend(bin_name=["Judy"])
        binary, source = install.depend_dict
        self.assertDictEqual(binary, REQUIRE_EXPECT_BIN, "Error in testing empty requires.")
        self.assertDictEqual(source, REQUIRE_EXCEPT_SRC, "Error in testing empty requires.")

    @patch.object(InstallRequires, "get_install_req")
    def test_multi_packages(self, mock1):
        """
        test multi package

        """
        mock1.return_value = WRONG_INSTALL_INFO
        install = InstallDepend(db_list=['openeuler'])
        install.install_depend(bin_name=["Judy", "Judy1111"])
        binary, source = install.depend_dict
        binary["Judy"]["install"] = sorted(binary["Judy"]["install"])
        self.assertDictEqual(binary, EXCEPT_BIN, "Error in testing multi packages.")
        self.assertDictEqual(source, EXCEPT_SRC, "Error in testing multi packages.")

    @patch.object(InstallRequires, "get_install_req")
    def test_with_level_1(self, mock1):
        """
        test with level 1

        """
        mock1.return_value = TRUE_INSTALL_INFO
        install = InstallDepend(db_list=['openeuler'])
        install.install_depend(bin_name=["Judy"], level=1)
        binary, source = install.depend_dict
        binary["Judy"]["install"] = sorted(binary["Judy"]["install"])
        self.assertDictEqual(binary, LEVEL_1_EXP_BIN, "Error in testing level 1.")
        self.assertDictEqual(source, LEVEL_1_EXP_SRC, "Error in testing level 1.")

    def test_empty_database(self):
        """
        test empty database

        """
        with self.assertRaises(ValueError):
            database_list = []
            install = InstallDepend(db_list=database_list)
            install.install_depend(bin_name=["Judy"])

    def test_invalid_package_type(self):
        """
        test invalid package type

        """
        with self.assertRaises(AttributeError):
            install = InstallDepend(db_list=['openeuler'])
            install.install_depend(bin_name="Judy")


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
        install = InstallDepend(db_list=['openeuler'])
        install(**param)
        binary, source = install.depend_dict
        binary["Judy"]["install"] = sorted(binary["Judy"]["install"])
        self.assertDictEqual(binary, PARAM_EXP_BIN, "Error in testing redis.")
        self.assertDictEqual(source, PARAM_EXP_SRC, "Error in testing redis.")

    @patch.object(InstallRequires, "get_install_req")
    def test_true_response(self, mock1):
        """
        test true response

        """
        mock1.return_value = TRUE_INSTALL_INFO
        install = InstallDepend(db_list=['openeuler'])
        install.install_depend(bin_name=["Judy"])
        binary, source = install.depend_dict
        binary["Judy"]["install"] = sorted(binary["Judy"]["install"])
        self.assertDictEqual(binary, EXCEPT_BIN, "Error in testing true response.")
        self.assertDictEqual(source, EXCEPT_SRC, "Error in testing true response.")
