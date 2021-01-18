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
from test.base_code.read_mock_data import MockData

MOCK_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


class TestInstallRequireDbQuery(TestCase):
    DATABASE_LIST = ['openeuler', 'fedora']
    JUDY_BINARY_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "JudyBinary.json"))
    JUDY_BINARY_INFO_NO_RELATION = MockData.read_mock_json_data(
        os.path.join(MOCK_DATA_FILE, "JudyBinaryNoRelation.json"))
    BASH_BINARY_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "bashBinary.json"))
    GLIBC_BINARY_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "glibcBinary.json"))
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
                         self.BASH_BINARY_INFO,
                         self.GLIBC_BINARY_INFO])

        result = self.install_instance.get_install_req(binary_list=['Judy'])

        self.assertEqual(self.EXPECT_VALUE, result)

    def test_specify_db(self):
        """
        Test specify database
        Returns:
        """
        self.query_instance.session.query = MagicMock(
            side_effect=[self.JUDY_BINARY_INFO,
                         self.BASH_BINARY_INFO,
                         self.GLIBC_BINARY_INFO])

        result = self.install_instance.get_install_req(binary_list=['Judy'], specify_db='openeuler')
        self.assertEqual(self.EXPECT_VALUE, result)

    def test_no_relation(self):
        """
        Test binary package requires info no relation
        Returns:
        """
        self.query_instance.session.query = MagicMock(
            side_effect=[self.JUDY_BINARY_INFO_NO_RELATION,
                         self.BASH_BINARY_INFO,
                         self.GLIBC_BINARY_INFO])

        result = self.install_instance.get_install_req(binary_list=['Judy'], specify_db='openeuler')
        self.assertEqual(self.EXPECT_VALUE, result)

    def test_query_no_data(self):
        """
        Test query for packages that do not exist
        Returns:
        """
        self.query_instance.session.query = MagicMock(return_value={})
        result = self.install_instance.get_install_req(binary_list=['Judy'], specify_db='openeuler')

        self.assertEqual(result, [])
