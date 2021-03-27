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
from unittest import TestCase
from unittest.mock import MagicMock

from packageship.application.query.pkg import QueryPackage
from test.coverage_tests.test_module.test_database_query.test_database_query_package.get_mock_data import ObtainMockData


class TestQueryBinaryPkgInfo(TestCase):
    """
    Test query binary packages detail
    """
    ALL_BINARY_RPM_INFO = ObtainMockData.get_data("allBinaryNoPaging.json")
    ALL_BINARY_INFO_PAGING = ObtainMockData.get_data("allBinaryPaging.json")
    JUDY_BINARY_INFO = ObtainMockData.get_data("JudyBinary.json")

    def setUp(self):
        """
        Set up function
        Returns: None

        """
        self.query_package = QueryPackage()
        self.session = self.query_package._db_session

    def test_command_line_of_cli(self):
        """
        Test query all binary packages, used for cli scenes
        Returns:
        """
        self.session.scan = MagicMock(return_value=self.ALL_BINARY_RPM_INFO)
        self.session.count = MagicMock(return_value={"count": 5})
        query_result = self.query_package.get_bin_info(binary_list=[], database='os_version_1', page_num=1, page_size=20,
                                                       command_line=True)
        self.assertIsNotNone(query_result['data'])

    def test_command_line_of_ui(self):
        """
        Test query all binary packages and paging, used for ui scenes
        Returns:
        """
        self.session.query = MagicMock(return_value=self.ALL_BINARY_INFO_PAGING)
        self.session.count = MagicMock(return_value={"count": 5})
        query_result = self.query_package.get_bin_info(binary_list=[], database='os_version_1', page_num=1, page_size=5,
                                                       command_line=False)
        self.assertEqual(len(query_result['data']), 5)

    def test_query_specify_of_ui(self):
        """
        Test query specify binary packages and paging of ui scenes
        Returns:
        """
        self.session.query = MagicMock(return_value=self.JUDY_BINARY_INFO)
        query_result = self.query_package.get_bin_info(binary_list=['Judy'], database='os_version_1', page_num=1,
                                                       page_size=5, command_line=False)
        self.assertIsNotNone(query_result['data'][0]['Judy'])

    def test_query_specify_of_cli(self):
        """
        Test query specify binary packages and paging of cli scenes
        Returns:
        """
        self.session.query = MagicMock(return_value=self.JUDY_BINARY_INFO)
        query_result = self.query_package.get_bin_info(binary_list=['Judy'], database='os_version_1', page_num=1,
                                                       page_size=5, command_line=True)
        self.assertIsNotNone(query_result['data'][0]['Judy'])

    def test_query_no_data(self):
        """
        Test query not exist binary packages and paging
        Returns:
        """
        self.session.query = MagicMock(return_value=dict(hits={}))
        query_result = self.query_package.get_bin_info(binary_list=['Judy'], database='os_version_1', page_num=1,
                                                       page_size=5, command_line=False)
        self.assertListEqual(query_result['data'], [])
