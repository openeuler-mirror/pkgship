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
test get database priority
"""
import os
import unittest
from packageship.application.query import database
from unittest.mock import MagicMock

from test.coverage_tests.base_code.read_mock_data import MockData
MOCK_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

class TestDBPriority(unittest.TestCase):
    """
    class for test get db priority
    """

    def test_wrong_query_db_result(self):
        """
        test wrong query db result
        """
        database.db_client.query = MagicMock(return_value={})
        db_list = database.get_db_priority()
        self.assertEqual(db_list, [], msg="Error in testing wrong query db result.")

    def test_true_result(self):
        """
        test true result

        """
        VERSION_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "db_priority.json"))
        database.db_client.query = MagicMock(return_value=VERSION_INFO)
        db_list = database.get_db_priority()
        self.assertNotEqual(db_list, [], msg="Error in testing true result.")

