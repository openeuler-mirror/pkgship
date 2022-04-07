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
# -*- coding:utf-8 -*-
"""
test get table col info
"""
from test.base_code.read_data_base import ReadTestBase
import unittest
from packageship.application import init_app
from test.common_files.constant import ResponseCode
from packageship.application.apps.package.view import TableColView

app = init_app('query')
table_col = TableColView()


class TestTableCol(ReadTestBase):
    """
    table col acquisition test
    """
    BASE_URL = "/packages/tablecol"
    REQUESTS_KWARGS = {
        "url": "",
        "method": "GET"
    }

    def test_table_col(self):
        """
        Test the actual table col data sheet
        """
        self.REQUESTS_KWARGS["url"] = self.BASE_URL
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)
        self.assertEqual(ResponseCode.SUCCESS,
                         resp_dict.get("code"),
                         msg="Error in status code return")

    def test_table_col_view(self):
        """
        Test the actual table col data sheet
        """
        with app.app_context():
            response = table_col.get()
            output_data = response.json
            self.assertEqual(
                {'code': '200', 'message': 'Successful Operation',
                 'resp': [{'column_name': 'name', 'default_selected': True, 'label': 'Name'},
                          {'column_name': 'version', 'default_selected': True, 'label': 'Version'},
                          {'column_name': 'release', 'default_selected': True, 'label': 'Release'},
                          {'column_name': 'url', 'default_selected': True, 'label': 'Url'},
                          {'column_name': 'rpm_license', 'default_selected': False, 'label': 'License'}]},
                output_data)


if __name__ == '__main__':
    unittest.main()
