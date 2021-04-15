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
test_get_pkgship_version
"""
import os
from pathlib import Path
from requests import RequestException, Response
from packageship.application.cli.commands.version import VersionCommand
from packageship.application.core.baseinfo import pkg_version
from test.cli.version_command import VersionTest

DATA_FOLDER = Path(Path(__file__).parent, "mock_data")


class TestVersion(VersionTest):
    """
    class for test pkgship version
    """
    cmd_class = VersionCommand

    def test_true_params(self):
        """
        test true params
        """
        self.excepted_str = """
Version:2.1.0
Release:7.oe1
        """
        pkg_version.file_path = os.path.join(DATA_FOLDER, "version.yaml")
        self.command_params = ["-v"]
        self.assert_result()

    def test_file_not_exists(self):
        """
        test yaml file not exists
        """
        self.excepted_str = """
ERROR_CONTENT  :get pkgship version failed
HINT           :Make sure the file is valid
        """
        pkg_version.file_path = os.path.join(DATA_FOLDER, "tmp_version.yaml")
        self.command_params = ["-v"]
        self.assert_result()

    def test_request_raise_requestexception(self):
        """test_request_raise_requestexception"""
        self.command_params = ["-v"]
        self.excepted_str = """
ERROR_CONTENT  :
HINT           :The remote connection is abnormal, please check the 'remote_host' parameter value to ensure the connectivity of the remote address
"""
        self.mock_requests_get(side_effect=[RequestException])
        self.assert_result()

    def test_request_text_raise_jsonerror(self):
        """test_request_text_raise_jsonerror"""
        self.command_params = ["-v"]

        class Resp:
            text = """{"test":\'123\',}"""
            status_code = 200

        self.excepted_str = """
ERROR_CONTENT  :{"test":'123',}
HINT           :The content is not a legal json format,please check the parameters is valid
        """
        self.mock_requests_get(return_value=Resp())
        self.assert_result()

    def test_request_status_429(self):
        """test_request_status_429"""
        self.command_params = ["-v"]
        self.excepted_str = """
Too many requests in a short time, please request again later
"""
        r = Response()
        r.status_code = 429
        self.mock_requests_get(return_value=r)
        self.assert_result()

    def test_request_status_500(self):
        """test_request_status_500"""
        self.command_params = ["-v"]
        self.excepted_str = """
ERROR_CONTENT  :500 Server Error: None for url: None
HINT           :The remote connection is abnormal, please check the 'remote_host' parameter value to ensure the connectivity of the remote address
"""
        r = Response()
        r.status_code = 500
        self.mock_requests_get(return_value=r)
        self.assert_result()
