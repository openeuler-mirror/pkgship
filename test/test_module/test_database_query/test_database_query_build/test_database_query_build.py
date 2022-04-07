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
# !/usr/bin/python3
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
from packageship.application.query.depend import BuildRequires
from test.base_code.read_mock_data import MockData

MOCK_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


class TestBuildRequireDbQuery(TestCase):
    DATABASE_LIST = ['os_version_1', 'os_version_2']
    JUDY_SOURCE_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "JudySource.json"))
    COMPONENTS_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "components_info,json"))
    EXCEPT_RETURN_VALUE = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "returnJudyResult.json"))

    def setUp(self):
        """
        Precondition for test cases
        Returns:
        """
        self.query_instance = Query()
        self.build_instance = BuildRequires(database_list=self.DATABASE_LIST)

    def test_empty_param(self):
        """
        Test input empty source_list
        Returns:
        """
        result = self.build_instance.get_build_req(source_list=[])
        expect_value = []

        self.assertEqual(expect_value, result)

    def test_specify_database(self):
        """
        Test specify database
        Returns:
        """
        self.query_instance.session.query = MagicMock(side_effect=[
            self.JUDY_SOURCE_INFO,
            self.COMPONENTS_INFO
        ])

        result = self.build_instance.get_build_req(source_list=['Judy'], specify_db='os_version_1')

        self.assertEqual(result, self.EXCEPT_RETURN_VALUE)

    def test_no_specify_database(self):
        """
         Test not specify database
         Returns:
         """
        self.query_instance.session.query = MagicMock(side_effect=[
            self.JUDY_SOURCE_INFO,
            self.COMPONENTS_INFO
        ])

        result = self.build_instance.get_build_req(source_list=['Judy'])

        self.assertEqual(result, self.EXCEPT_RETURN_VALUE)

    def test_query_no_data(self):
        """
        Test query for packages that do not exist
        Returns:
        """
        self.query_instance.session.query = MagicMock(return_value={})
        result = self.build_instance.get_build_req(source_list=['Judy'], specify_db='os_version_1')

        self.assertEqual(result, [])
