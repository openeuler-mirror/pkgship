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


class TestQueryBinName(TestCase):
    """
    Test query binary packages‘ sources package
    """

    def setUp(self):
        """
        set up function
        Returns:

        """
        self.query_package = QueryPackage(database_list=['openeuler', 'fedora'])
        self.session = self.query_package._db_session

    def test_query_specify_rpm(self):
        """
        Test query specify binary package
        Returns:
        """
        self.session.query = MagicMock(
            return_value=ObtainMockData.get_data('JudySource.json'))
        source_list = ['Judy']
        result = self.query_package.get_bin_name(source_list=source_list)
        expect_value = ObtainMockData.get_data('returnJudyResult.json')

        self.assertEqual(result[0], expect_value)

    def test_src_list_empty(self):
        """
        Test input a empty binary packages list
        Returns:
        """
        source_list = []
        result = self.query_package.get_bin_name(source_list=source_list)

        self.assertListEqual(result, [])
