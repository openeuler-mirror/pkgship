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
"""
test get database name
"""
import unittest
from test.base_code.common_test_code import get_correct_json_by_filename, compare_two_values
from test.base_code.read_data_base import ReadTestBase
from packageship.libs.constants import ResponseCode


class TestBinPackageInfo(ReadTestBase):
    """
    class for test get binary package info
    """
    BASE_URL = "packages/packageInfo/file?db_name={}&pkg_name={}"
    REQUESTS_KWARGS = {
        "url": "",
        "method": "GET",
    }

    def test_not_found_database_info_response(self):
        """
        test not found database info response
        Returns:

        """
        self.REQUESTS_KWARGS["url"] = self.BASE_URL.format("openEuler", "dnf$CUnit")
        self.without_dbs_folder(self.REQUESTS_KWARGS, met=self, code=
        ResponseCode.NOT_FOUND_DATABASE_INFO)
        self.when_db_no_content(self.REQUESTS_KWARGS, met=self, code=
        ResponseCode.NOT_FOUND_DATABASE_INFO)

    def test_db_name_error_response(self):
        """
        test db name error response
        Returns:

        """
        self.REQUESTS_KWARGS["url"] = self.BASE_URL.format("test", "dnf$CUnit")
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)
        self.response_json_error_judge(resp_dict, resp_code=ResponseCode.DB_NAME_ERROR, method=self)

    def test_pkg_name_not_found_response(self):
        """
        test pkg name not found response
        Returns:

        """
        self.REQUESTS_KWARGS["url"] = self.BASE_URL.format("openEuler", "test$test1")
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)
        self.response_json_error_judge(resp_dict, resp_code=
        ResponseCode.PACK_NAME_NOT_FOUND, method=self)

    def test_true_params_result(self):
        """
        test_true_params_result
        Returns:

        """
        self.REQUESTS_KWARGS["url"] = self.BASE_URL.format("openEuler", "Judy$dnf")

        correct_json = get_correct_json_by_filename("filelist_info")
        self.assertNotEqual({}, correct_json, msg="Error reading JSON file name database_name")
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)
        self.assertTrue(compare_two_values(correct_json, resp_dict))


if __name__ == '__main__':
    unittest.main()
