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
from unittest.mock import patch
from redis import Redis

from packageship.application.core.depend.build_depend import BuildDepend
from packageship.application.query.depend import InstallRequires, BuildRequires
from test.base_code.read_mock_data import MockData

MOCK_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
TRUE_INSTALL_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "true_install_info.json"))
TRUE_BUILD_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "true_build_info.json"))
WRONG_INSTALL_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "wrong_install_info.json"))
NOT_FOUND_COMP = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "not_found_component.json"))
NOT_SEARCHED_BUILD = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "not_searched_pkg_build_info.json"))
EXCEPT_SRC = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "except_src.json"))
LEVEL_1_EXCEPT_SRC = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "level_1_src.json"))


param = {
    "packagename": ["Judy"],
    "depend_type": "builddep",
    "parameter": {
      "db_priority": ["openeuler"],
      "level": 2,
      "self_build": True
    }
}

class TestBuildDdepend(unittest.TestCase):
    """
    class for test build depend info
    """

    @patch.object(BuildRequires, "get_build_req")
    def test_package_not_exists(self, mock1):
        """
        test package not exists

        """
        mock1.return_value = []
        build = BuildDepend(db_list=['openeuler'])
        build.build_depend(src_name=["Judy111"])
        binary, source = build.depend_dict
        self.assertEqual(binary, {}, "Error in testing package not exists.")
        self.assertEqual(source, {}, "Error in testing package not exists.")

    @patch.object(BuildRequires, "get_build_req")
    @patch.object(InstallRequires, "get_install_req")
    def test_build_1_level(self, mock1, mock2):
        """
        test build level 1

        """
        mock1.return_value = TRUE_INSTALL_INFO
        mock2.return_value = TRUE_BUILD_INFO
        build = BuildDepend(db_list=['openeuler'])
        build.build_depend(src_name=["Judy"], level=1)
        binary, source = build.depend_dict
        EXCEPT_BIN_INFO = {'sed': {'name': 'sed', 'version': '4.8', 'source_name': 'sed', 'database': 'openeuler'}}
        self.assertDictEqual(binary, EXCEPT_BIN_INFO, "Error in testing build level 1.")
        self.assertDictEqual(source, LEVEL_1_EXCEPT_SRC, "Error in testing build level 1.")



    @patch.object(BuildRequires, "get_build_req")
    @patch.object(InstallRequires, "get_install_req")
    def test_true_result(self, mock1, mock2):
        """
        test true result

        """
        mock1.return_value = TRUE_INSTALL_INFO
        mock2.return_value = TRUE_BUILD_INFO
        build = BuildDepend(db_list=['openeuler'])
        build.build_depend(src_name=["Judy"], level=2, self_build=True)
        binary, source = build.depend_dict
        self.assertDictEqual(binary, {}, "Error in testing true result.")
        self.assertDictEqual(source, EXCEPT_SRC, "Error in testing true result.")


    def test_empty_database(self):
        """
        test empty database

        """
        with self.assertRaises(AttributeError):

            build_depend = BuildDepend(db_list=[])
            build_depend.build_depend(src_name=["Judy"])

    def test_invalid_package_type(self):
        """
        test invalid package type

        """
        with self.assertRaises(AttributeError):
            build_depend = BuildDepend(db_list=['openeuler'])
            build_depend.build_depend(src_name="Judy")


    @patch.object(BuildRequires, "get_build_req")
    @patch.object(InstallRequires, "get_install_req")
    def test_empty_build_requires(self, mock1, mock2):
        """
        test empty build requires

        """
        mock1.return_value = TRUE_INSTALL_INFO
        mock2.return_value = [{}]
        build = BuildDepend(db_list=['openeuler'])
        build.build_depend(src_name=["Judy"], self_build=True)
        binary, source = build.depend_dict
        self.assertDictEqual(binary, {}, "Error in testing empty build requires.")
        self.assertDictEqual(source, {}, "Error in empty build requires.")


    @patch.object(BuildRequires, "get_build_req")
    @patch.object(InstallRequires, "get_install_req")
    def test_not_found_comp(self, mock1, mock2):
        """
        test not found component

        """
        mock1.return_value = TRUE_INSTALL_INFO
        mock2.return_value = NOT_FOUND_COMP
        build = BuildDepend(db_list=['openeuler'])
        build.build_depend(src_name=["Judy"], level=2, self_build=True)
        binary, source = build.depend_dict
        EXCEPT_SRC_INFO = {'Judy': {'name': 'Judy', 'version': '1.0.5', 'database': 'openeuler', 'build': []}}
        self.assertDictEqual(binary, {}, "Error in testing not found component.")
        self.assertDictEqual(source, EXCEPT_SRC_INFO, "Error in testing not found component.")

    @patch.object(BuildRequires, "get_build_req")
    @patch.object(InstallRequires, "get_install_req")
    def test_srcname_not_in_searched_pkg(self, mock1, mock2):
        """
        test srcname not in searched packages

        """
        mock1.return_value = TRUE_INSTALL_INFO
        mock2.return_value = NOT_SEARCHED_BUILD
        build = BuildDepend(db_list=['openeuler'])
        build.build_depend(src_name=["Judy"], level=2, self_build=True)
        binary, source = build.depend_dict
        EXCEPT_SRC_INFO = {'Judy11': {'name': 'Judy11', 'version': '1.0.5', 'database': 'openeuler', 'build': ['sed']}}
        self.assertDictEqual(binary, {}, "Error in testing srcname not in searched packages.")
        self.assertDictEqual(source, EXCEPT_SRC_INFO, "Error in testing srcname not in searched packages.")


    @mock.patch.object(Redis, "exists")
    def test_call_func_with_true_param(self, mock1):
        """
        test call func with true param
        Returns:

        """
        mock1.side_effect = [
            False,
            False,
            False,
            False
        ]
        InstallRequires.get_install_req = mock.Mock(return_value=TRUE_INSTALL_INFO)
        BuildRequires.get_build_req = mock.Mock(return_value=TRUE_BUILD_INFO)
        build = BuildDepend(db_list=['openeuler'])
        build(**param)
        binary, source = build.depend_dict
        self.assertDictEqual(binary, {}, "Error in testing call func with true param.")
        self.assertDictEqual(source, EXCEPT_SRC, "Error in testing call func with true param.")