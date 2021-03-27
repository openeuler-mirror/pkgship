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
 be_depend unittest
"""
import json
import unittest
from unittest import mock

from test.coverage_tests.base_code import ReadTestBase
from packageship.application.apps.dependinfo.view import DependList
from test.coverage_tests.common_files.constant import ResponseCode
from packageship.application import init_app
from packageship.application.core.depend.basedepend import BaseDepend
from test.coverage_tests.base_code.common_test_code import get_correct_json_by_filename
from packageship.application.common.exc import ElasticSearchQueryException

app = init_app('query')


class TestDependInfoDependList(ReadTestBase):
    """
    class for test depend list
    """
    REQUESTS_KWARGS = {
        "url": "/dependinfo/dependlist",
        "method": "post",
        "data": "",
        "content_type": "application/json"
    }

    def test_param_error_response(self):
        """
        test empty parameters:packagename,depend_type
        :return:
        """

        param_error_list = [
            "{}",
            json.dumps({"packagename": [],
                        "depend_type": "installdep",
                        "parameter": {
                            "db_priority": ["os_version_1"],
                            "level": 2}}),
            json.dumps({"packagename": [],
                        "depend_type": "bedep",
                        "parameter": {
                            "db_priority": ["os_version_1"],
                            "packtype": "source",
                            "with_subpack": True,
                            "search_type": "install"}}),
            json.dumps({"packagename": [],
                        "depend_type": "selfdep",
                        "parameter": {
                            "db_priority": ["os_version_1"],
                            "self_build": False,
                            "packtype": "source",
                            "with_subpack": False}}),
            json.dumps({"packagename": [],
                        "depend_type": "builddep",
                        "parameter": {
                            "db_priority": ["os_version_1"],
                            "level": 2,
                            "self_build": False}}),
            json.dumps({"packagename": ["Judy"],
                        "depend_type": "bedep",
                        "parameter": {
                            "db_priority": [],
                            "packtype": "source",
                            "with_subpack": True,
                            "search_type": "install"}}),
            json.dumps({"packagename": ["Judy"],
                        "depend_type": "bedep",
                        "parameter": {
                            "db_priority": [],
                            "packtype": "source",
                            "with_subpack": True,
                            "search_type": "xxx"}}),
            json.dumps({"packagename": [],
                        "depend_type": "selfdep",
                        "parameter": {
                            "db_priority": ["os_version_1"],
                            "self_build": False,
                            "packtype": "xxx",
                            "with_subpack": False}}),
        ]
        for error_param in param_error_list:
            self.REQUESTS_KWARGS["data"] = error_param

            resp_dict = self.client_request(**self.REQUESTS_KWARGS)
            self.response_json_error_judge(resp_dict,
                                           resp_code=ResponseCode.PARAM_ERROR, method=self)

    @mock.patch.object(BaseDepend, "depend_list")
    def test_empty_result(self, mock_depend_list):
        """
        test_true_params_result
        Returns:
        """
        depend_list = DependList()
        correct_data = get_correct_json_by_filename("empty_dependinfo_depend_list")
        input_value = correct_data["input"]
        output_for_input = correct_data["output"]
        mock_depend_list.return_value = output_for_input
        with app.test_request_context("/packages/dependlist", data=json.dumps(input_value),
                                      content_type="application/json"):
            response = depend_list.post()
            output_data = response.json
            self.response_json_format(output_data)

    @mock.patch.object(BaseDepend, "depend_list")
    def test_true_params_result(self, mock_depend_list):
        """
        test_true_params_result
        Returns:
        """
        depend_list = DependList()
        correct_list = get_correct_json_by_filename("dependinfo_depend_list")
        for correct_data in correct_list:
            input_value = correct_data["input"]
            output_for_input = correct_data["output"]
            mock_depend_list.return_value = output_for_input
            with app.test_request_context("/packages/dependlist", data=json.dumps(input_value),
                                          content_type="application/json"):
                response = depend_list.post()
                output_data = response.json
                self.response_json_format(output_data)

    @mock.patch("packageship.application.core.depend.DispatchDepend.execute",
                side_effect=ElasticSearchQueryException('es error'))
    def test_es_error(self, mock_es_error):
        """
        test_es_error
        Returns:
        """
        depend_list = DependList()
        input_value = {
            "packagename": [
                "Judy"
            ],
            "depend_type": "installdep",
            "parameter": {
                "db_priority": [
                    "os_version_1"
                ],
                "level": 2
            }
        }
        mock_es_error.return_value = None
        with app.test_request_context("/packages/dependlist", data=json.dumps(input_value),
                                      content_type="application/json"):
            response = depend_list.post()
            output_data = response.json
            self.response_json_format(output_data)


if __name__ == '__main__':
    unittest.main()
