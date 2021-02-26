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
import unittest
from unittest import mock
from packageship.application.core.pkginfo.pkg import SourcePackage
from test.base_code.read_data_base import ReadTestBase
from test.common_files.constant import ResponseCode
from test.base_code.common_test_code import get_correct_json_by_filename
from packageship.application.common.exc import ElasticSearchQueryException


class TestGetSinglePack(ReadTestBase):
    """
    Single package test case
    """
    BASE_URL = "packages/src/Judy?database_name={}&pkg_name={}"
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
            self.BASE_URL.format(-1, "")
        ]
        for error_param in param_error_list:
            self.REQUESTS_KWARGS["url"] = error_param
            resp_dict = self.client_request(**self.REQUESTS_KWARGS)
            self.response_json_error_judge(
                resp_dict, resp_code=ResponseCode.PARAM_ERROR, method=self)

    def test_wrong_pkg_name(self):
        """test wrong package name"""
        self.REQUESTS_KWARGS["url"] = self.BASE_URL.format("openeuler", "test")
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)
        self.response_json_error_judge(
            resp_dict,
            resp_code=ResponseCode.PACK_NAME_NOT_FOUND,
            method=self)

    @mock.patch.object(SourcePackage, "src_package_info")
    def test_empty_resp(self, mock_src_package_info):
        """test wrong resp"""
        self.REQUESTS_KWARGS["url"] = self.BASE_URL.format("openeuler", "Judy")
        mock_src_package_info.return_value = []
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)
        self.assertEqual(resp_dict['code'], ResponseCode.PACK_NAME_NOT_FOUND)

    @mock.patch.object(SourcePackage, "src_package_info")
    def test_true_parameters(self, mock_src_package_info):
        """
        test true parameters
        """
        mock_data = get_correct_json_by_filename("get_single_src_package")

        self.REQUESTS_KWARGS["url"] = self.BASE_URL.format("openeuler", "Judy")
        mock_src_package_info.return_value = mock_data
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)
        self.response_json_format(resp_dict)

    @mock.patch("packageship.application.core.pkginfo.pkg.SourcePackage.src_package_info",
                side_effect=ElasticSearchQueryException('es error'))
    def test_es_error(self, mock_es_error):
        """
        test_es_error
        Returns:
        """
        self.REQUESTS_KWARGS["url"] = self.BASE_URL.format(
            "openeuler", "1", "1")
        mock_es_error.return_value = None
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)
        self.response_json_format(resp_dict)


if __name__ == '__main__':
    unittest.main()
