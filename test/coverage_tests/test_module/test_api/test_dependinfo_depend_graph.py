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
from test.coverage_tests.common_files.constant import ResponseCode
from packageship.application import init_app
from packageship.application.apps.dependinfo.view import DependGraph
from packageship.application.core.depend.basedepend import BaseDepend
from test.coverage_tests.base_code.common_test_code import get_correct_json_by_filename
from packageship.application.common.exc import ElasticSearchQueryException

app = init_app('query')


class TestDependInfoDependGraph(ReadTestBase):
    """
    class for test depend graph
    """
    REQUESTS_KWARGS = {
        "url": "/dependinfo/dependgraph",
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
            json.dumps({
                "packagename": [],
                "depend_type": "builddep",
                "node_name": "glibc",
                "node_type": "binary",
                "parameter": {
                    "db_priority": [
                        "os_version_1",
                        "os_version_2"
                    ],
                    "level": 2,
                    "self_build": True
                }
            }),
            json.dumps({
                "packagename": ["Judy"],
                "depend_type": "xxx",
                "node_name": "",
                "node_type": "binary",
                "parameter": {
                    "db_priority": [
                        "os_version_1",
                        "os_version_2"
                    ],
                    "level": 2,
                    "self_build": True
                }
            }),
            json.dumps({
                "packagename": ["Judy"],
                "depend_type": "builddep",
                "node_name": "xxx",
                "node_type": "",
                "parameter": {
                    "db_priority": [
                        "os_version_1",
                        "os_version_2"
                    ],
                    "level": 2,
                    "self_build": True
                }
            }),
            json.dumps({
                "packagename": ["Judy"],
                "depend_type": "builddep",
                "node_name": "glibc",
                "node_type": "xxx",
                "parameter": {
                    "db_priority": [
                        "os_version_1",
                        "os_version_2"
                    ],
                    "level": 2,
                    "self_build": True
                }
            })
        ]
        for error_param in param_error_list:
            self.REQUESTS_KWARGS["data"] = error_param

            resp_dict = self.client_request(**self.REQUESTS_KWARGS)
            self.response_json_error_judge(resp_dict,
                                           resp_code=ResponseCode.PARAM_ERROR, method=self)

    @mock.patch.object(BaseDepend, "depend_info_graph")
    def test_empty_result(self, mock_depend_info_graph):
        """
        test_true_params_result
        Returns:
        """
        depend_graph = DependGraph()
        correct_data = get_correct_json_by_filename("empty_dependinfo_depend_graph")
        input_value = correct_data["input"]
        output_for_input = correct_data["output"]
        mock_depend_info_graph.return_value = output_for_input
        with app.test_request_context("/packages/dependgraph", data=json.dumps(input_value),
                                      content_type="application/json"):
            response = depend_graph.post()
            output_data = response.json
            self.response_json_format(output_data)

    @mock.patch.object(BaseDepend, "depend_info_graph")
    def test_true_params_result(self, mock_depend_info_graph):
        """
        test_true_params_result
        Returns:
        """
        depend_graph = DependGraph()
        correct_data = get_correct_json_by_filename("dependinfo_depend_graph")
        input_value = correct_data["input"]
        output_for_input = correct_data["output"]
        mock_depend_info_graph.return_value = output_for_input
        with app.test_request_context("/packages/dependgraph", data=json.dumps(input_value),
                                      content_type="application/json"):
            response = depend_graph.post()
            output_data = response.json
            self.response_json_format(output_data)

    @mock.patch("packageship.application.core.depend.DispatchDepend.execute",
                side_effect=ElasticSearchQueryException('error'))
    def test_es_error(self, mock_es_error):
        """
        test_es_error
        Returns:
        """
        depend_graph = DependGraph()
        correct_data = get_correct_json_by_filename("dependinfo_depend_graph")
        input_value = correct_data["input"]
        mock_es_error.return_value = None
        with app.test_request_context("/packages/dependgraph", data=json.dumps(input_value),
                                      content_type="application/json"):
            response = depend_graph.post()
            output_data = response.json
            self.response_json_format(output_data)


if __name__ == '__main__':
    unittest.main()
