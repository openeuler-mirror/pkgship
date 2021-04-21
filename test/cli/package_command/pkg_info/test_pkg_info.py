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
test get single binary package info
"""
from pathlib import Path
from requests import RequestException, Response
from packageship.application.cli.commands.singlepkg import SingleCommand
from packageship.application.common.exc import ElasticSearchQueryException
from test.cli import DATA_BASE_INFO
from test.cli.package_command import PackageTestBase

MOCK_DATA_FOLDER = Path(Path(__file__).parent, "mock_data")
EXPECTED_DATA_FOLDER = Path(Path(__file__).parent, "mock_data", "expected_data")


class TestSingleBinaryPackage(PackageTestBase):
    """
    class for test single binary package
    """
    cmd_class = SingleCommand

    def test_true_params(self):
        """test true params"""
        self.excepted_str = self.read_file_content(
            "bin_true_params.txt",
            folder=EXPECTED_DATA_FOLDER,
            is_json=False
        )
        self.command_params = ["Judy", "os-version"]
        self.mock_es_search(side_effect=self.read_file_content(
            "pkg_info.json",
            folder=MOCK_DATA_FOLDER))
        self.assert_result()

    def test_wrong_dbs(self):
        """test wrong dbs"""
        self.excepted_str = """
ERROR_CONTENT  :Request parameter error
HINT           :Please check the parameter is valid and query again"""
        self.command_params = ["Judy", "version123"]
        self.mock_es_search(side_effect=self.read_file_content(
            "pkg_info.json",
            folder=MOCK_DATA_FOLDER))
        self.assert_result()

    def test_not_exists_package(self):
        """test not exists package"""
        self.excepted_str = """
ERROR_CONTENT  :The querying package does not exist in the databases
HINT           :Use the correct package name and try again"""
        self.command_params = ["Judy", "os-version"]
        single_package_not_exists_info = self.read_file_content(
            "pkg_info.json", folder=MOCK_DATA_FOLDER)[:1]
        single_package_not_exists_info.append({})
        self.mock_es_search(side_effect=single_package_not_exists_info)
        self.assert_result()

    def test_wrong_type_filelist(self):
        """test wrong type filelist"""

        def modify_filelist_data():
            """generate wrong type filelist"""
            wrong_type_filelist = self.read_file_content("pkg_info.json", folder=MOCK_DATA_FOLDER)
            wrong_type_filelist[1]["hits"]["hits"][0]["_source"]["filelists"][0]["filetypes"] = "h"
            return wrong_type_filelist

        self.excepted_str = self.read_file_content(
            "wrong_type_filelist.txt",
            folder=EXPECTED_DATA_FOLDER,
            is_json=False
        )
        self.command_params = ["Judy", "os-version"]
        self.mock_es_search(side_effect=modify_filelist_data())
        self.assert_result()

    def test_none_filelist(self):
        """test none filelist"""

        def generate_none_filelist():
            """generate none filelist"""
            error_filelist_info = self.read_file_content("pkg_info.json", folder=MOCK_DATA_FOLDER)
            error_filelist_info[1]["hits"]["hits"][0]["_source"]["filelists"] = None
            return error_filelist_info

        self.excepted_str = self.read_file_content(
            "error_filelist.txt",
            folder=EXPECTED_DATA_FOLDER,
            is_json=False)
        self.command_params = ["Judy", "os-version"]
        self.mock_es_search(side_effect=generate_none_filelist())
        self.assert_result()

    def test_error_single_bin_package(self):
        """test error single bin package"""
        self.excepted_str = """
ERROR_CONTENT  :The querying package does not exist in the databases
HINT           :Use the correct package name and try again
        """
        self.command_params = ["Judy", "os-version"]
        error_single_bin_info = self.read_file_content("pkg_info.json", folder=MOCK_DATA_FOLDER)
        error_single_bin_info[1] = {None}
        self.mock_es_search(side_effect=error_single_bin_info)
        self.assert_result()

    def test_empty_provides_for_bin(self):
        """test empty provides for bin"""

        def generate_empty_provides_data():
            """generate empty provides data"""
            empty_provides_single_bin = self.read_file_content("pkg_info.json", folder=MOCK_DATA_FOLDER)
            empty_provides_single_bin[2]["hits"]["hits"][0]["_source"]["provides"] = None
            return empty_provides_single_bin

        self.excepted_str = self.read_file_content(
            "bin_empty_provides.txt",
            folder=EXPECTED_DATA_FOLDER,
            is_json=False)
        self.command_params = ["Judy", "os-version"]
        self.mock_es_search(side_effect=generate_empty_provides_data())
        self.assert_result()

    def test_raise_es_error(self):
        """test_raise_es_error"""
        self.command_params = ["Judy", "os-version"]
        self.mock_es_search(side_effect=[DATA_BASE_INFO, ElasticSearchQueryException])
        self.excepted_str = """
    ERROR_CONTENT  :Failed to Connect the database
    HINT           :Check the connection
    """
        self.assert_result()

    def test_request_raise_requestexception(self):
        """test_request_raise_requestexception"""
        self.command_params = ["Judy", "os-version"]
        self.mock_es_search(side_effect=self.read_file_content("pkg_info.json", folder=MOCK_DATA_FOLDER))
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

        self.command_params = ["Judy", "os-version"]
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

        self.command_params = ["Judy", "os-version"]
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
        self.command_params = ["Judy", "os-version"]
        r = Response()
        r.status_code = 500
        self.mock_requests_get(return_value=r)
        self.assert_result()
