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
import os
from unittest import TestCase
from unittest.mock import MagicMock

from packageship.application.query import Query
from packageship.application.query.depend import InstallRequires
from test.coverage_tests.base_code.read_mock_data import MockData

MOCK_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


class TestInstallRequireDbQuery(TestCase):
    DATABASE_LIST = ['os_version_1', 'os_version_2']
    JUDY_BINARY_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "JudyBinary.json"))
    PROVIDES_COMPONENTS_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "providesComponentsInfo.json"))
    FILES_COMPONENTS_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "filesComponentsInfo.json"))
    EXPECT_VALUE = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "returnJudyResult.json"))

    def setUp(self):
        """
        Precondition for test cases
        Returns:
        """
        self.query_instance = Query()
        self.install_instance = InstallRequires(database_list=self.DATABASE_LIST)

    def test_empty_param(self):
        """
        Test input empty binary_list
        Returns:
        """
        result = self.install_instance.get_install_req(binary_list=[])
        expect_value = []

        self.assertEqual(expect_value, result)

    def test_no_specify_db(self):
        """
        Test not specify database
        Returns:
        """
        self.query_instance.session.query = MagicMock(
            side_effect=[self.JUDY_BINARY_INFO,
                         self.PROVIDES_COMPONENTS_INFO,
                         self.FILES_COMPONENTS_INFO])

        result = self.install_instance.get_install_req(binary_list=['Judy'])
        result_require = self._format_return(result)
        expect_require = self._format_return(self.EXPECT_VALUE)

        self.assertEqual(expect_require, result_require)

    def test_specify_db(self):
        """
        Test specify database
        Returns:
        """
        self.query_instance.session.query = MagicMock(
            side_effect=[self.JUDY_BINARY_INFO,
                         self.PROVIDES_COMPONENTS_INFO,
                         self.FILES_COMPONENTS_INFO])

        result = self.install_instance.get_install_req(binary_list=['Judy'], specify_db='os_version_1')
        result_require = self._format_return(result)
        expect_require = self._format_return(self.EXPECT_VALUE)

        self.assertEqual(expect_require, result_require)

    def test_query_no_data(self):
        """
        Test query for packages that do not exist
        Returns:
        """
        self.query_instance.session.query = MagicMock(return_value={})
        result = self.install_instance.get_install_req(binary_list=['Judy'], specify_db='os_version_1')

        self.assertEqual(result, [])

    @staticmethod
    def _format_return(return_data):
        format_data = [dict(binary_name=data.get('binary_name'),
                            bin_version=data.get('bin_version'),
                            database=data.get('database'),
                            src_name=data.get('src_name'),
                            src_version=data.get('src_version'),
                            requires=data.get('requires').sort(key=lambda x: x.get('component')))
                       for data in return_data
                       ]
        return format_data
