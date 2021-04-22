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
test_build_dep_cmd
"""
from test.cli import DATA_BASE_INFO
from unittest.mock import PropertyMock
from test.cli.depend_command import DependTestBase
from packageship.application.common.exc import ElasticSearchQueryException
from requests.exceptions import ConnectionError, RequestException
from packageship.application.cli.commands.builddep import BuildDepCommand


class TestBuildDep(DependTestBase):
    """
    class for TestBuildDep
    """
    cmd_class = BuildDepCommand
    binary_file = "os-version-binary.json"
    component_file = "os-version-binary-component.json"
    source_file = "os-version-source.json"

    def test_true_params_level0(self):
        """
        test true params
        """
        self.command_params = ["Judy"]
        self.excepted_str = self.read_file_content("build_depend_data/builddep_Judy_level0.txt", is_json=False)
        self.assert_result()

    def test_true_params_level1(self):
        """
        test true params
        """
        self.command_params = ["Judy", "-level=1"]
        self.excepted_str = self.read_file_content("build_depend_data/builddep_Judy_level1.txt", is_json=False)
        self.assert_result()

    def test_true_params_dbs_level0(self):
        """
        test true params
        """
        self.command_params = ["Judy", "-dbs=os-version"]
        self.excepted_str = self.read_file_content("build_depend_data/builddep_Judy_dbs_level0.txt", is_json=False)
        self.assert_result()

    def test_true_params_dbs_level1(self):
        """
        test true params
        """
        self.command_params = ["Judy", "-dbs=os-version", "-level=1"]
        self.excepted_str = self.read_file_content("build_depend_data/builddep_Judy_dbs_level1.txt", is_json=False)
        self.assert_result()

    def test_wrong_level(self):
        """
        test wrong params
        """
        self.command_params = ["CUnit", "-level=-100"]
        self.excepted_str = """
ERROR_CONTENT  :Request parameter error
HINT           :Please check the parameter is valid and query again
        """
        self.assert_exc_result()

    def test_wrong_package_name(self):
        """
        test the package name is not in the database
        """
        self.command_params = ["test"]
        self.excepted_str = """
ERROR_CONTENT  :The querying package does not exist in the databases
HINT           :Use the correct package name and try again
            """
        self.assert_exc_result()

    def test_db_name_error(self):
        """test_db_name_error"""

        self.command_params = ["Judy", "-dbs=os-version-123"]
        self.excepted_str = """
ERROR_CONTENT  :Request parameter error
HINT           :Please check the parameter is valid and query again
"""
        self.assert_exc_result()

    def test_error_es_data_return_not_resp(self):
        """test_get_be_req_error_data_to_raise_keyerror"""

        self.command_params = ["Judy_123", "-dbs=os-version"]
        self.excepted_str = """
ERROR_CONTENT  :The querying package does not exist in the databases
HINT           :Use the correct package name and try again
"""
        self.mock_es_search(side_effect=[DATA_BASE_INFO, {}])
        self.assert_exc_result()

    def test_raise_es_error(self):
        """test_raise_es_error"""

        self.command_params = ["Judy", "-dbs=os-version"]
        self.excepted_str = """
ERROR_CONTENT  :Server error
HINT           :Please check the service and try again
    """
        self.mock_es_search(side_effect=[DATA_BASE_INFO, ElasticSearchQueryException])
        self._execute_command()

    def test_request_raise_connecterror(self):
        """test_request_raise_connecterror"""

        self.command_params = ["Judy", "-dbs=os-version"]
        self.excepted_str = """
ERROR_CONTENT  :There seems to be a problem with the service
HINT           :Please check the connection and try again
"""
        self._to_update_kw_and_make_mock(
            "packageship.application.common.remote.RemoteService.request",
            effect=ConnectionError,
        )
        self.assert_exc_result()

    def test_request_raise_requestexception(self):
        """test_request_raise_requestexception"""

        self.command_params = ["Judy", "-dbs=os-version"]
        self.excepted_str = """
ERROR_CONTENT  :
HINT           :The remote connection is abnormal, please check the 'remote_host' parameter value to ensure the connectivity of the remote address
"""
        self._to_update_kw_and_make_mock(
            "packageship.application.common.remote.RemoteService.request",
            effect=RequestException,
        )
        self.assert_exc_result()

    def test_request_text_raise_jsonerror(self):
        """test_request_text_raise_jsonerror"""

        self.command_params = ["Judy", "-dbs=os-version"]
        self.excepted_str = """
ERROR_CONTENT  :{"test":\'hahaha\',}
HINT           :The content is not a legal json format,please check the parameters is valid
"""
        self._to_update_kw_and_make_mock(
            "packageship.application.common.remote.RemoteService.text",
            new_callable=PropertyMock,
            return_value="""{"test":'hahaha',}"""
        )
        self.assert_exc_result()

    def test_request_status_500(self):
        """test_request_status_500"""

        self.command_params = ["Judy", "-dbs=os-version"]
        self.excepted_str = """
ERROR_CONTENT  :Server error
HINT           :Please check the service and try again
"""

        self._to_update_kw_and_make_mock(
            "packageship.application.common.remote.RemoteService.status_code",
            new_callable=PropertyMock,
            return_value=500,
        )

        self._to_update_kw_and_make_mock(
            "packageship.application.common.remote.RemoteService.text",
            new_callable=PropertyMock,
            return_value="",
        )
        self.assert_exc_result()
