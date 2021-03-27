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
test get pkgship version and release info
"""
import unittest
from unittest import mock
from test.coverage_tests.common_files.constant import ResponseCode
from test.coverage_tests.base_code import ReadTestBase
from packageship.application import init_app
from packageship.application.apps.package.view import PkgshipVersion
from packageship.application.core.baseinfo import pkg_version

app = init_app('query')


class TestGetVersion(ReadTestBase):
    """
    Version acquisition test
    """
    BASE_URL = "/version"
    REQUESTS_KWARGS = {
        "url": "",
        "method": "GET"
    }

    def test_version(self):
        """
        Test the actual data sheet
        """
        correct_version, correct_release = "1.1.0", "1"
        self.REQUESTS_KWARGS["url"] = self.BASE_URL
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)
        self.assertEqual(ResponseCode.SUCCESS,
                         resp_dict.get("code"),
                         msg="Error in status code return")
        self.assertEqual(correct_version, resp_dict.get("version"),
                         msg="Error in getting pkgship version")
        self.assertEqual(correct_release, resp_dict.get("release"),
                         msg="Error in getting pkgship release")

    def test_true_result(self):
        """
        test_true_params_result
        Returns:

        """
        version = PkgshipVersion()
        with app.app_context():
            response = version.get()
            output_data = response.json
            self.assertEqual(
                {'code': '200', 'message': 'Successful Operation', 'release': '1', 'resp': None, 'version': '1.1.0'},
                output_data)

    def test_wrong_result(self):
        """
        test_true_params_result
        Returns:

        """
        version = PkgshipVersion()
        pkg_version.get_pkgship_version = mock.Mock(return_value=(None, None))
        with app.app_context():
            response = version.get()
            output_data = response.json
            self.assertEqual(
                {'code': '4011', 'message': 'Unable to get the generated database information', 'resp': None,
                 'tip': 'Make sure the generated database information is valid'}, output_data,
                msg="Error getting pkgship version")


if __name__ == '__main__':
    unittest.main()
