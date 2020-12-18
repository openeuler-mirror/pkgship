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
test_get_single_packages
"""

from test.base_code.read_data_base import ReadTestBase


from packageship.libs.constants import ResponseCode


class TestGetSinglePack(ReadTestBase):
    """
    Single package test case
    """
    BASE_URL = "packages/packageInfo?pkg_name={}&table_name={}"
    REQUESTS_KWARGS = {
        "url": "",
        "method": "GET"
    }

    def test_missing_required_parameters(self):
        """
        Missing required parameters
        """
        # Missing required parameters pkg_name
        param_error_list = [
            self.BASE_URL.format("", ""),
            self.BASE_URL.format("test", ""),
            self.BASE_URL.format("", -1)
        ]
        for error_param in param_error_list:
            self.REQUESTS_KWARGS["url"] = error_param
            resp_dict = self.client_request(**self.REQUESTS_KWARGS)
            self.response_json_error_judge(
                resp_dict, resp_code=ResponseCode.PARAM_ERROR, method=self)

    def test_wrong_pkg_name(self):
        """test wrong package name"""
        self.REQUESTS_KWARGS["url"] = self.BASE_URL.format("test", "mainline")
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)
        self.response_json_error_judge(
            resp_dict,
            resp_code=ResponseCode.PACK_NAME_NOT_FOUND,
            method=self)

    def test_wrong_table_name(self):
        """test wrong package name"""

        # Missing required parameters table_name
        self.REQUESTS_KWARGS["url"] = self.BASE_URL.format("test", "A")
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)
        self.response_json_error_judge(
            resp_dict,
            resp_code=ResponseCode.TABLE_NAME_NOT_EXIST,
            method=self)

    def test_true_parameters(self):
        """
        test true parameters
        """

        self.REQUESTS_KWARGS["url"] = self.BASE_URL.format("A", "fedora30")
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)
        self.compare_response_get_out("get_single_package", resp_dict)
