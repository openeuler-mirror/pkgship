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
packges test
"""
import unittest

from test.base_code.read_data_base import ReadTestBase


from packageship.application.apps.package.function.constants import ResponseCode


class TestPackages(ReadTestBase):
    """
    All package test cases
    """
    BASE_URL = "/packages?table_name={}&page_num={}&page_size={}"
    REQUESTS_KWARGS = {
        "url": "",
        "method": "GET"
    }

    def test_not_found_database_info_response(self):
        """
        Initialization failed. No database was generated. Database information could not be found
        Returns:

        """
        self.REQUESTS_KWARGS["url"] = self.BASE_URL.format("test", 1, 10)
        self.without_dbs_folder(
            self.REQUESTS_KWARGS,
            met=self,
            code=ResponseCode.TABLE_NAME_NOT_EXIST)
        self.when_db_no_content(
            self.REQUESTS_KWARGS,
            met=self,
            code=ResponseCode.TABLE_NAME_NOT_EXIST)

    def test_miss_required_parameter(self):
        """
        Missing required parameters
        """
        param_error_list = [
            self.BASE_URL.format("", "", ""),
            self.BASE_URL.format("test", -1, 10),
            self.BASE_URL.format("test", 0, 10),
            self.BASE_URL.format("test", 1.1, 10),
            self.BASE_URL.format("test", "e", 10),
            self.BASE_URL.format("test", 65536, 10),
            self.BASE_URL.format("test", 10, -1),
            self.BASE_URL.format("test", 10, 0),
            self.BASE_URL.format("test", 10, "e"),
            self.BASE_URL.format("test", 10, 1.1),
            self.BASE_URL.format("test", 10, 65536),
        ]
        for error_param in param_error_list:
            self.REQUESTS_KWARGS["url"] = error_param

            resp_dict = self.client_request(**self.REQUESTS_KWARGS)
            self.response_json_error_judge(
                resp_dict, resp_code=ResponseCode.PARAM_ERROR, method=self)

    def test_table_not_in_db(self):
        """The table name is not in the database"""
        self.REQUESTS_KWARGS["url"] = self.BASE_URL.format("test", "1", "10")
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)
        self.response_json_error_judge(
            resp_dict,
            resp_code=ResponseCode.TABLE_NAME_NOT_EXIST,
            method=self)

    def test_true_table_name(self):
        """The test table name is in the database"""
        self.REQUESTS_KWARGS["url"] = self.BASE_URL.format(
            "fedora30", "1", "1")
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)
        self.compare_response_get_out("packages", resp_dict)

    def test_true_like_name(self):
        """Test for correct fuzzy matches"""

        self.REQUESTS_KWARGS["url"] = self.BASE_URL.format(
            "fedora30", "1", "4") + "&query_pkg_name=A"
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)
        self.compare_response_get_out("packages_like_src", resp_dict)


if __name__ == '__main__':
    unittest.main()
