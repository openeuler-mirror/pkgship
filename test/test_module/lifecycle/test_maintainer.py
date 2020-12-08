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
import unittest
from packageship.libs.constants import ResponseCode


class TestGetMaintainers(ReadTestBase):
    """
    Maintainer list acquisition test
    """
    BASE_URL = "/lifeCycle/maintainer"
    REQUESTS_KWARGS = {
        "url": "",
        "method": "GET"
    }

    def test_maintainer(self):
        """
            Test the actual data sheet
        """
        self.REQUESTS_KWARGS["url"] = self.BASE_URL
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)
        self.assertEqual(ResponseCode.SUCCESS,
                         resp_dict.get("code"),
                         msg="Error in status code return")
        self.assertEqual(['userA', 'userB'], resp_dict.get(
            'data'), msg="The data content is incorrect")


if __name__ == '__main__':
    unittest.main()
