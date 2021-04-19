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
test get all binary packages
"""
from pathlib import Path
from requests import RequestException, Response
from packageship.application.cli.commands.allpkg import AllPackageCommand
from packageship.application.common.exc import ElasticSearchQueryException
from test.cli import DATA_BASE_INFO
from test.cli.package_command import PackageTestBase

MOCK_DATA_FOLDER = Path(Path(__file__).parent, "mock_data")
EXPECTED_DATA_FOLDER = Path(Path(__file__).parent, "mock_data", "expected_data")


class TestAllPackage(PackageTestBase):
    """
    class for test all binary packages
    """
    cmd_class = AllPackageCommand

    def test_true_params_for_all_bin_packages(self):
        """
        test true params for all binary packages
        """

        self.excepted_str = self.read_file_content(
            "pkg_list_expected_data.txt",
            folder=EXPECTED_DATA_FOLDER,
            is_json=False
        )
        self.command_params = ["os-version"]
        self.mock_es_search(return_value=DATA_BASE_INFO)
        self.mock_es_scan(return_value=self.read_file_content(
            "pkg_list.json",
            folder=MOCK_DATA_FOLDER))
        self.assert_result()

    def test_wrong_dbs_for_all_bin_packages(self):
        """
        test wrong dbs for all binary packages
        """

        self.excepted_str = """
ERROR_CONTENT  :Request parameter error
HINT           :Please check the parameter is valid and query again"""
        self.command_params = ["version123"]
        self.mock_es_search(return_value=DATA_BASE_INFO)
        self.assert_result()

    def test_None_bin_packages_info(self):
        """
        test None bin packages
        """
        self.excepted_str = """
ERROR_CONTENT  :There is no such table in the database
HINT           :Make sure the table is valid"""
        self.command_params = ["os-version"]
        self.mock_es_search(return_value=DATA_BASE_INFO)
        self.mock_es_scan(return_value=None)
        self.assert_result()

    def test_pkgInfoGetingError(self):
        """
        test pkgInfoGetingError for all bin packages
        """
        self.excepted_str = """
ERROR_CONTENT  :Failed to Connect the database
HINT           :Check the connection"""
        self.command_params = ["os-version"]
        self.mock_es_search(return_value=DATA_BASE_INFO)
        self.mock_es_scan(return_value=[])
        self.assert_result()

    def test_raise_es_error(self):
        """test_raise_es_error"""
        self.command_params = ["os-version"]
        self.mock_es_search(return_value=DATA_BASE_INFO)
        self.mock_es_scan(side_effect=ElasticSearchQueryException)
        self.excepted_str = """
ERROR_CONTENT  :Failed to Connect the database
HINT           :Check the connection
"""
        self.assert_result()

    def test_request_raise_requestexception(self):
        """test_request_raise_requestexception"""
        self.command_params = ["os-version"]
        self.excepted_str = """
ERROR_CONTENT  :
HINT           :The remote connection is abnormal, please check the 'remote_host' parameter value to ensure the connectivity of the remote address
"""
        self.mock_requests_get(side_effect=[RequestException])
        self.assert_result()

    def test_request_text_raise_jsonerror(self):
        """test_request_text_raise_jsonerror"""
        class Resp:
            text = """{"test":\'123\',}"""
            status_code = 200

        self.command_params = ["os-version"]
        self.excepted_str = """
ERROR_CONTENT  :{"test":'123',}
HINT           :The content is not a legal json format,please check the parameters is valid
        """
        self.mock_requests_get(return_value=Resp())
        self.assert_result()

    def test_request_status_429(self):
        """test_request_status_429"""
        class Resp:
            status_code = 429

        self.command_params = ["os-version"]
        self.excepted_str = """
Too many requests in a short time, please request again later
"""
        self.mock_requests_get(return_value=Resp())
        self.assert_result()

    def test_request_status_500(self):
        """test_request_status_500"""
        self.excepted_str = """
ERROR_CONTENT  :500 Server Error: None for url: None
HINT           :The remote connection is abnormal, please check the 'remote_host' parameter value to ensure the connectivity of the remote address
"""
        self.command_params = ["os-version", "-s"]
        r = Response()
        r.status_code = 500
        self.mock_requests_get(return_value=r)
        self.assert_result()

