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
import json
import unittest
from unittest import mock
from test.coverage_tests.base_code import ReadTestBase
from test.coverage_tests.common_files.constant import ResponseCode
from packageship.application.core.depend.basedepend import BaseDepend
from packageship.application.common.exc import ElasticSearchQueryException


class TestDownloadFile(ReadTestBase):
    """
    Download test of excel file
    """
    REQUESTS_KWARGS = {
        "url": "/dependinfo/downloadfiles",
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
            json.dumps({"packagename": [],
                        "depend_type": "installdep",
                        "parameter": {
                            "db_priority": ["os_version_1"],
                            "level": 0}}),
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

    def test_build_dep(self):
        """
        Returns:

        """
        resp_dict = self.client.post("/dependinfo/downloadfiles", data=json.dumps({
            "packagename": ["Judy"],
            "depend_type": "builddep",
            "parameter": {
                "db_priority": ["os_version_1"],
                "self_build": False,
                "packtype": "source",
                "level": 1,
                "with_subpack": False}}), content_type="application/json")
        self.assertIsNotNone(resp_dict)

    def test_self_dep(self):
        """
        Returns:

        """
        resp_dict = self.client.post("/dependinfo/downloadfiles", data=json.dumps({
            "packagename": ["Judy"],
            "depend_type": "selfdep",
            "parameter": {
                "db_priority": ["os_version_1"],
                "self_build": False,
                "packtype": "source",
                "with_subpack": False}}), content_type="application/json")
        self.assertIsNotNone(resp_dict)

    def test_install_dep(self):
        """
        Returns:

        """
        resp_dict = self.client.post("/dependinfo/downloadfiles", data=json.dumps({
            "packagename": ["Judy"],
            "depend_type": "installdep",
            "parameter": {
                "db_priority": ["os_version_1"],
                "level": 2}}), content_type="application/json")
        self.assertIsNotNone(resp_dict)

    def test_be_dep(self):
        """
        Returns:

        """
        resp_dict = self.client.post("/dependinfo/downloadfiles", data=json.dumps({
            "packagename": ["Judy"],
            "depend_type": "bedep",
            "parameter": {
                "db_priority": ["os_version_1"],
                "packtype": "source",
                "with_subpack": False,
                "search_type": "install"}}), content_type="application/json")
        self.assertIsNotNone(resp_dict)

    def test_down_src(self):
        """
        Returns:

        """
        resp_dict = self.client.post("/dependinfo/downloadfiles", data=json.dumps({
            "packagename": ["Judy"],
            "depend_type": "src",
            "parameter": {
                "db_priority": ["os_version_1"],
                "packtype": "source",
                "with_subpack": False,
                "search_type": "install"}}), content_type="application/json")
        self.assertIsNotNone(resp_dict)

    @mock.patch.object(BaseDepend, "download_depend_files")
    def test_down_wrong(self, mock_download_depend_files):
        """
        Returns:

        """
        mock_download_depend_files.return_value = ""
        resp_dict = self.client.post("/dependinfo/downloadfiles", data=json.dumps({
            "packagename": ["Judy"],
            "depend_type": "bedep",
            "parameter": {
                "db_priority": ["os_version_1"],
                "packtype": "source",
                "with_subpack": False,
                "search_type": "install"}}), content_type="application/json")
        self.assertIsNotNone(resp_dict)

    @mock.patch.object(BaseDepend, "download_depend_files")
    def test_wrong_folder_path(self, mock_download_depend_files):
        """
        Returns:

        """
        mock_download_depend_files.return_value = "etc/Download/test"
        resp_dict = self.client.post("/dependinfo/downloadfiles", data=json.dumps({
            "packagename": ["Judy"],
            "depend_type": "bedep",
            "parameter": {
                "db_priority": ["os_version_1"],
                "packtype": "source",
                "with_subpack": False,
                "search_type": "install"}}), content_type="application/json")
        self.assertIsNotNone(resp_dict)

    @mock.patch("packageship.application.core.depend.DispatchDepend.execute",
                side_effect=ElasticSearchQueryException('error'))
    def test_es_error(self, mock_es_error):
        """
        test_es_error
        Returns:
        """
        mock_es_error.return_value = None
        resp_dict = self.client.post("/dependinfo/downloadfiles", data=json.dumps({
            "packagename": ["Judy"],
            "depend_type": "selfdep",
            "parameter": {
                "db_priority": ["os_version_1"],
                "self_build": False,
                "packtype": "source",
                "with_subpack": False}}), content_type="application/json")
        self.response_json_format(resp_dict.json)


if __name__ == '__main__':
    unittest.main()
