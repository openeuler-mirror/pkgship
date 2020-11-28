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
"""TestUpdatePackage"""

import os

from packageship import BASE_PATH

from test.base_code.operate_data_base import OperateTestBase
import json
from packageship.application.apps.package.function.constants import ResponseCode


class TestBatchUpdatePackage(OperateTestBase):
    """TestUpdatePackage"""
    REQUESTS_KWARGS = {
        "url": "/lifeCycle/updatePkgInfo",
        "method": "put",
        "data": "",
        "content_type": "application/json"
    }

    def test_init_wrong(self):
        """
        Initialization failed. No database was generated. Database information could not be found
        Returns:

        """

        yaml_path = os.path.join(
            os.path.dirname(BASE_PATH),
            "test",
            "common_files",
            "test_true_yaml")
        self.REQUESTS_KWARGS["data"] = json.dumps({"batch": "1",
                                                   "filepath": yaml_path})
        self.without_dbs_folder(
            self.REQUESTS_KWARGS,
            met=self,
            code=ResponseCode.UPDATA_DATA_FAILED, test_type='operate')

    def test_missing_required_parameters(self):
        """Parameter error"""
        # all miss required parameters
        param_error_list = [
            "{}",
            json.dumps({"batch": ""}),
            json.dumps({"batch": "test"})
        ]
        for error_param in param_error_list:
            self.REQUESTS_KWARGS["data"] = error_param
            resp_dict = self.client_request(**self.REQUESTS_KWARGS)
            self.response_json_error_judge(
                resp_dict, resp_code=ResponseCode.PARAM_ERROR, method=self)

    def test_only_batch(self):
        """Only batch field"""
        self.REQUESTS_KWARGS["data"] = json.dumps({"batch": "1"})
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)
        self.response_json_error_judge(
            resp_dict,
            resp_code=ResponseCode.SPECIFIED_FILE_NOT_EXIST,
            method=self)

    def test_file_path_error(self):
        """file path error"""
        self.REQUESTS_KWARGS["data"] = json.dumps({"batch": "1",
                                                   "filepath": "/test/"})
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)
        self.response_json_error_judge(
            resp_dict,
            resp_code=ResponseCode.SPECIFIED_FILE_NOT_EXIST,
            method=self)

    def test_wrong_format_yaml(self):
        """test wrong format yaml"""

        yaml_path = os.path.join(
            os.path.dirname(BASE_PATH),
            "test",
            "common_files",
            "test_wrong_format_yaml")
        self.REQUESTS_KWARGS["data"] = json.dumps({"batch": "1",
                                                   "filepath": yaml_path})
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)
        self.response_json_error_judge(
            resp_dict,
            resp_code=ResponseCode.YAML_FILE_ERROR,
            method=self)

    def test_data_true_yaml(self):
        """test wrong main yaml"""
        yaml_path = os.path.join(
            os.path.dirname(BASE_PATH),
            "test",
            "common_files",
            "test_true_yaml")
        self.REQUESTS_KWARGS["data"] = json.dumps({"batch": "1",
                                                   "filepath": yaml_path})
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)
        self.response_json_error_judge(
            resp_dict, resp_code=ResponseCode.SUCCESS, method=self)

    def test_single_update_miss_pkg(self):
        """update single miss pkg name"""
        self.REQUESTS_KWARGS["data"] = json.dumps({"batch": 0,
                                                   "pkg_name": ""})
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)
        self.response_json_error_judge(
            resp_dict,
            resp_code=ResponseCode.PACK_NAME_NOT_FOUND,
            method=self)

    def test_single_update_error_level(self):
        """update single error level"""
        param_error_list = [
            json.dumps({"batch": 0, "pkg_name": "a", "maintainlevel": ""}),
            json.dumps({"batch": 0, "pkg_name": "a", "maintainlevel": "a"}),
            json.dumps({"batch": 0, "pkg_name": "a", "maintainlevel": "6"}),
            json.dumps({"batch": 0, "pkg_name": "a", "maintainlevel": "-1"}),
        ]
        for error_param in param_error_list:
            self.REQUESTS_KWARGS["data"] = error_param
            resp_dict = self.client_request(**self.REQUESTS_KWARGS)
            self.response_json_error_judge(
                resp_dict, resp_code=ResponseCode.PARAM_ERROR, method=self)

    def test_true_single_update(self):
        """true single update"""
        self.REQUESTS_KWARGS["data"] = json.dumps({"batch": 0,
                                                   "pkg_name": "a",
                                                   "maintainlevel": "1"})
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)
        self.response_json_error_judge(
            resp_dict, resp_code=ResponseCode.SUCCESS, method=self)
