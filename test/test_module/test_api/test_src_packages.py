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
src packages test
"""
import unittest
from unittest import mock
from packageship.application.core.pkginfo.pkg import Package
from test.base_code.read_data_base import ReadTestBase
from test.common_files.constant import ResponseCode
from test.base_code.common_test_code import get_correct_json_by_filename
from packageship.application.common.exc import ElasticSearchQueryException


class TestBinPackages(ReadTestBase):
    """
    All src package test cases
    """
    BASE_URL = "/packages/src?database_name={}&page_num={}&page_size={}"
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
            code=ResponseCode.PARAM_ERROR)
        self.when_db_no_content(
            self.REQUESTS_KWARGS,
            met=self,
            code=ResponseCode.PARAM_ERROR)

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

    @mock.patch.object(Package, "all_src_packages")
    def test_empty_resp(self, mock_src_bin_packages):
        """The table name is not in the database"""
        self.REQUESTS_KWARGS["url"] = self.BASE_URL.format("os_version_1", "1", "10")
        mock_src_bin_packages.return_value = []
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)
        self.assertEqual(resp_dict['code'], ResponseCode.TABLE_NAME_NOT_EXIST)

    @mock.patch.object(Package, "all_src_packages")
    def test_true_table_name(self, mock_src_bin_packages):
        """The test table name is in the database"""
        mock_data = get_correct_json_by_filename("src_packages")
        self.REQUESTS_KWARGS["url"] = self.BASE_URL.format(
            "os_version_1", "1", "1")
        mock_src_bin_packages.return_value = mock_data
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)
        self.response_json_format(resp_dict)

    @mock.patch("packageship.application.core.pkginfo.pkg.Package.all_src_packages",
                side_effect=ElasticSearchQueryException('es error'))
    def test_es_error(self, mock_es_error):
        """
        test_es_error
        Returns:
        """
        self.REQUESTS_KWARGS["url"] = self.BASE_URL.format(
            "os_version_1", "1", "1")
        mock_es_error.return_value = None
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)
        self.response_json_format(resp_dict)


if __name__ == '__main__':
    unittest.main()
