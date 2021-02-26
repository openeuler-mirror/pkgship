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
from packageship.application.query.depend import BeDependRequires
from test.base_code.read_mock_data import MockData

MOCK_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


class TestBeDependQuery(TestCase):
    JUDY_BE_DEPEND_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, 'JudyBeDepend.json'))

    def setUp(self):
        self.query_instance = Query()
        self.be_depend_instance = BeDependRequires()

    def test_normal_query(self):
        self.query_instance.session.query = MagicMock(return_value=self.JUDY_BE_DEPEND_INFO)

        result = self.be_depend_instance.get_be_req(binary_list=['Judy'], database='openeuler')
        expect_value = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, 'returnJudyResult.json'))

        self.assertEqual(result, expect_value)

    def test_not_exist(self):
        self.query_instance.session.query = MagicMock(return_value={})
        result = self.be_depend_instance.get_be_req(binary_list=['Test'], database='openeuler')

        self.assertEqual(result, [])
