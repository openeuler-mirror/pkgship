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
from test.test_module.test_database_query.test_database_query_package.get_mock_data import ObtainMockData


class TestQuerySrcName(TestCase):
    """
    Test query sources packages' binary packages
    """

    def setUp(self):
        """
        set up function
        Returns:

        """
        self.query_package = QueryPackage(database_list=['os_version_1', 'os_version_2'])
        self.session = self.query_package._db_session

    def test_query_specify_rpm(self):
        """
        Test query specify binary package
        Returns:
        """
        self.session.query = MagicMock(return_value=ObtainMockData.get_data('JudyBinary.json'))
        binary_list = ['Judy']
        result = self.query_package.get_src_name(binary_list=binary_list)
        expect_value = {'binary_name': 'Judy',
                        'bin_version': '1.0.5',
                        'database': 'os_version_1',
                        'src_name': 'Judy',
                        'src_version': '1.0.5'}

        self.assertEqual(result[0], expect_value)

    def test_binary_list_empty(self):
        """
        Test input a empty binary packages list
        Returns:

        """
        binary_list = []
        result = self.query_package.get_src_name(binary_list=binary_list)

        self.assertListEqual(result, [])

    def test_query_no_data(self):
        """
        Test query a not exist binary package
        Returns:

        """
        self.session.query = MagicMock(return_value={})
        binary_list = ["Test123"]
        result = self.query_package.get_src_name(binary_list=binary_list)

        self.assertListEqual(result, [])

    def test_query_specify_database(self):
        """
        Test query binary package and specify database
        Returns:

        """
        self.session.query = MagicMock(return_value={})
        binary_list = ["Test123"]
        result = self.query_package.get_src_name(binary_list=binary_list, specify_db='os_version_1')

        self.assertListEqual(result, [])
