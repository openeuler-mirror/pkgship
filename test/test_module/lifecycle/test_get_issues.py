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
test get issues
"""
from test.base_code.read_data_base import ReadTestBase
import unittest

from packageship.application.apps.package.function.constants import ResponseCode


class TestGetIssue(ReadTestBase):
    """
    Issues test case
    """
    BASE_URL = "/lifeCycle/issuetrace?pkg_name={}&page_num={}&page_size={}"
    REQUESTS_KWARGS = {
        "url": "",
        "method": "GET"
    }

    def test_miss_required_parameter(self):
        """
        Missing required parameters
        """
        # test miss all page_num page_size
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

    def test_true_like_name(self):
        """Test for correct fuzzy matches"""

        self.REQUESTS_KWARGS["url"] = self.BASE_URL.format("dnf", "1", "4")
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)
        self.compare_response_get_out("issues", resp_dict)

    def test_issue_type(self):
        """
        test issue type
        """
        self.REQUESTS_KWARGS["url"] = "/lifeCycle/issuetype"
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)
        self.compare_response_get_out("issue_type", resp_dict)

    def test_issue_status(self):
        """
        test issue status
        """
        self.REQUESTS_KWARGS["url"] = "/lifeCycle/issuestatus"
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)
        self.compare_response_get_out("issue_status", resp_dict)


if __name__ == '__main__':
    unittest.main()
