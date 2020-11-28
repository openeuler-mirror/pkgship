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
test get repodatas
"""

from test.base_code.read_data_base import ReadTestBase
import unittest


from packageship.application.apps.package.function.constants import ResponseCode


class TestGetRepodatas(ReadTestBase):
    """
    test get repodatas
    """
    BASE_URL = "/repodatas"
    REQUESTS_KWARGS = {
        "url": "",
        "method": "GET"
    }

    def test_not_found_database_info_response(self):
        """
        Initialization failed. No database was generated. Database information could not be found
        Returns:

        """
        self.REQUESTS_KWARGS["url"] = self.BASE_URL
        self.without_dbs_folder(
            self.REQUESTS_KWARGS,
            met=self,
            code=ResponseCode.NOT_FOUND_DATABASE_INFO)

    def test_redundant_parameters(self):
        """Tests for redundant parameters"""
        self.REQUESTS_KWARGS["url"] = self.BASE_URL + "?ddd"
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)

        self.compare_response_get_out("get_repodatas", resp_dict)

    def test_true_parameters(self):
        """Tests for true parameters"""
        self.REQUESTS_KWARGS["url"] = self.BASE_URL
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)
        self.compare_response_get_out("get_repodatas", resp_dict)


if __name__ == '__main__':
    unittest.main()
