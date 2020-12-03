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
Less transmission is always parameter transmission
"""
import unittest
import json

from test.base_code.dependinfo_base_test import DependInfo
from packageship.application.apps.package.function.constants import ResponseCode


class TestDependInfoBeDepend(DependInfo):
    """
    The dependencies of the package are tested
    """
    REQUESTS_KWARGS = {
        "url": "/dependInfo/beDepend",
        "method": "post",
        "data": "",
        "content_type": "application/json"
    }

    def test_not_found_database_info_response(self):
        """
        Initialization failed. No database was generated. Database information could not be found
        Returns:
        """
        self.REQUESTS_KWARGS["data"] = json.dumps({"packagename": "CUnit", "dbname": "mainline"})
        self.without_dbs_folder(self.REQUESTS_KWARGS,
                                met=self, code=ResponseCode.NOT_FOUND_DATABASE_INFO)
        self.when_db_no_content(self.REQUESTS_KWARGS,
                                met=self, code=ResponseCode.NOT_FOUND_DATABASE_INFO)

    def test_param_error_response(self):
        """
        test empty parameters:packagename,dbname,withsubpack
        :return:
        """

        param_error_list = [
            "{}",
            json.dumps({"packagename": "",
                        "dbname": "mainline"}),
            json.dumps({"packagename": "dsd" * 220,
                        "dbname": "mainline"}),
            json.dumps({"packagename": 0,
                        "dbname": "mainline"}),
            json.dumps({"packagename": "CUnit",
                        "dbname": 12}),
            json.dumps({"packagename": "CUnit",
                        "dbname": ""}),
            json.dumps({"packagename": "CUnit",
                        "dbname": "ccc" * 50}),
            json.dumps({"packagename": "CUnit",
                        "dbname": "mainline", "withsubpack": "3"}),
            json.dumps({"packagename": "CUnit",
                        "dbname": "mainline", "withsubpack": ""})
        ]
        for error_param in param_error_list:
            self.REQUESTS_KWARGS["data"] = error_param

            resp_dict = self.client_request(**self.REQUESTS_KWARGS)
            self.response_json_error_judge(resp_dict,
                                           resp_code=ResponseCode.PARAM_ERROR, method=self)

    def test_pkg_name_not_found_response(self):
        """
        test package name not found
        """
        self.REQUESTS_KWARGS["data"] = json.dumps(
            {"packagename": "sdfUsdnit", "dbname": "mainline"})
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)

        self.response_json_error_judge(resp_dict,
                                       resp_code=ResponseCode.PACK_NAME_NOT_FOUND, method=self)

    def test_db_name_error_response(self):
        """
        test database name not found
        """
        self.REQUESTS_KWARGS["data"] = json.dumps({"packagename": "A", "dbname": "asdfavwfdsa"})

        resp_dict = self.client_request(**self.REQUESTS_KWARGS)

        self.response_json_error_judge(resp_dict, resp_code=ResponseCode.DB_NAME_ERROR, method=self)

    def test_true_params_result(self):
        """
        test_true_params_result
        Returns:
        """
        self.compare_resp_and_output("dependinfo_be_depend", met=self)


if __name__ == '__main__':
    unittest.main()
