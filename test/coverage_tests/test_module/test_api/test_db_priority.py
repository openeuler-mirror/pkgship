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
test get db priority
"""
import unittest
from unittest import mock
from test.coverage_tests.common_files.constant import ResponseCode
from packageship.application import init_app
from test.coverage_tests.base_code import ReadTestBase
from packageship.application.apps.package.view import DatabasePriority
from packageship.application.query import database
from packageship.application.common.exc import ElasticSearchQueryException

app = init_app('query')


class TestGetDBPriority(ReadTestBase):
    """
    Maintainer list acquisition test
    """
    BASE_URL = "/db_priority"
    REQUESTS_KWARGS = {
        "url": "",
        "method": "GET"
    }

    def test_db_priority(self):
        """
            Test the actual data sheet
        """
        self.REQUESTS_KWARGS["url"] = self.BASE_URL
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)
        self.assertEqual(ResponseCode.SUCCESS,
                         resp_dict.get("code"),
                         msg="Error in status code return")
        self.assertEqual(["os_version_1", "os_version_2"], resp_dict.get(
            'resp'), msg="The data content is incorrect")

    def test_true_result(self):
        """
        test_true_params_result
        Returns:

        """
        db_priority = DatabasePriority()
        with app.app_context():
            response = db_priority.get()
            output_data = response.json
            self.assertEqual(
                {'code': '200', 'message': 'Successful Operation', 'resp': ["os_version_1", "os_version_2"]},
                output_data)

    def test_wrong_result(self):
        """
        test_true_params_result
        Returns:

        """
        db_priority = DatabasePriority()
        database.get_db_priority = mock.Mock(return_value=[])
        with app.app_context():
            response = db_priority.get()
            output_data = response.json
            self.assertEqual(
                {'code': '4011', 'message': 'Unable to get the generated database information', 'resp': None,
                 'tip': 'Make sure the generated database information is valid'}, output_data,
                msg="Error getting pkgship version")

    @mock.patch("packageship.application.query.database.get_db_priority",
                side_effect=ElasticSearchQueryException('es error'))
    def test_es_error(self, mock_es_error):
        """
        test_es_error
        Returns:
        """
        self.REQUESTS_KWARGS["url"] = self.BASE_URL
        mock_es_error.return_value = None
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)
        self.response_json_format(resp_dict)


if __name__ == '__main__':
    unittest.main()
