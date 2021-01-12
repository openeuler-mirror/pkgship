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
import json
import unittest


class TestBase(unittest.TestCase):
    """
        unittest unit test basic class
    """

    def client_request(
            self,
            url=None,
            method="GET",
            data=None,
            content_type=None):
        """
            Simulate client sending request
        """
        self.assertIsNotNone(url, msg="Error url")
        methods = {
            "GET", "POST", "PUT", "DELETE", "OPTIONS",
            "get", "post", "put", "delete", "options"
        }
        self.assertIn(method, methods, msg="Wrong way of requesting method")

        response = self.client.__getattribute__(
            method.lower())(url, data=data, content_type=content_type)
        response_content = json.loads(response.data)
        return response_content
