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
TestInstallDepend
"""
import unittest
import json

from test.base_code.read_data_base import ReadTestBase
from packageship.application.apps.package.function.constants import ResponseCode


class TestDependInfoInstallDepend(ReadTestBase):
    """
    TestInstallDepend
    """
    REQUESTS_KWARGS = {
        "url": "/dependInfo/installDepend",
        "method": "POST",
        "data": "",
        "content_type": "application/json"
    }

    # Let's say something goes wrong with init
    def test_not_found_database_info_response(self):
        self.REQUESTS_KWARGS["data"] = json.dumps({"binaryName": "A1"})

        # When DBS folder does not exist
        self.without_dbs_folder(self.REQUESTS_KWARGS, met=self, code=ResponseCode.NOT_FOUND_DATABASE_INFO)
        # When there is DB_ but no data
        self.when_db_no_content(self.REQUESTS_KWARGS, met=self, code=ResponseCode.NOT_FOUND_DATABASE_INFO)

    # Data does not pass validation where the data is null plus length validation in Serialize
    def test_param_error_response(self):
        """
        test_empty_binaryName_dbList
        Returns:

        """
        param_error_list = [
            "{}",
            json.dumps({"binaryName": ""}),
            json.dumps({"binaryName": "dsd" * 200}),
            json.dumps({"binaryName": 0}),
            json.dumps({"binaryName": "CUnit",
                        "db_list": [12, 3, 4]}),
            json.dumps({"binaryName": "CUnit",
                        "db_list": "xxxxx"}),
        ]

        for error_param in param_error_list:
            self.REQUESTS_KWARGS["data"] = error_param

            resp_dict = self.client_request(**self.REQUESTS_KWARGS)
            self.response_json_error_judge(resp_dict, resp_code=ResponseCode.PARAM_ERROR, method=self)

    def test_pkg_name_not_found_response(self):
        self.REQUESTS_KWARGS["data"] = json.dumps({"binaryName": "qitiandasheng"})
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)

        self.response_json_error_judge(resp_dict, resp_code=ResponseCode.PACK_NAME_NOT_FOUND, method=self)

    def test_db_name_error_response(self):
        self.REQUESTS_KWARGS["data"] = json.dumps({"binaryName": "CUnit",
                                                   "db_list": ["shifu", "bajie"]
                                                   })

        resp_dict = self.client_request(**self.REQUESTS_KWARGS)

        self.response_json_error_judge(resp_dict, resp_code=ResponseCode.DB_NAME_ERROR, method=self)

    # Judge whether your result is correct or not
    def test_true_params_result(self):
        """
        test_true_params_result
        Returns:

        """
        self.compare_resp_and_output("dependinfo_install_depend", met=self)


if __name__ == '__main__':
    unittest.main()
