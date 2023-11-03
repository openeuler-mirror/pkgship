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
test_install_dep_cmd
"""
from pathlib import Path
from unittest.mock import PropertyMock

from requests import RequestException

from packageship.application.cli.commands.installdep import InstallDepCommand
from packageship.application.common.exc import ElasticSearchQueryException
from test.cli import DATA_BASE_INFO
from test.cli.depend_commands import DependTestBase

INSTALLDEP_EXPECTED_DATA_FOLDER = Path(Path(__file__).parent, "expected_data")


class TestInstallDep(DependTestBase):
    """
    class for TestInstallDep
    """

    cmd_class = InstallDepCommand
    binary_file = "os-version-binary.json"
    component_file = "os-version-binary-component.json"

    def test_wrong_level_negative(self):
        """
        test Wrong parameter,Leve is a negative number
        """
        self.command_params = ["Judy", "-level=-100"]
        self.excepted_str = """
ERROR_CONTENT  :Request parameter error
HINT           :Please check the parameter is valid and query again
        """
        self.assert_exc_result()

    def test_wrong_level_0(self):
        """
        test Wrong parameter, Level is zero
        """
        self.command_params = ["Judy", "-level=0"]
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

    def test_wrong_db_name(self):
        """
        test the package name is not in the database
        """
        self.command_params = ["CUnit", "-dbs=test"]
        self.excepted_str = """
ERROR_CONTENT  :Request parameter error
HINT           :Please check the parameter is valid and query again
                """
        self.assert_exc_result()

    def test_true_level_0(self):
        """
        test Correct parameter,Only the package name
        """

        self.command_params = ["Judy"]
        self.excepted_str = self.read_file_content(
            "installdep_Judy.txt", folder=INSTALLDEP_EXPECTED_DATA_FOLDER, is_json=False
        )
        self.assert_result()

    def test_true_level_1(self):
        """
        The installation dependency specifies a query level of 1
        """

        self.command_params = ["Judy", "-level=1"]
        self.excepted_str = self.read_file_content(
            "install_Judy_level_1.txt",
            folder=INSTALLDEP_EXPECTED_DATA_FOLDER,
            is_json=False,
        )
        self.assert_result()

    def test_true_level_one_db(self):
        """
        The installation dependency specifies the query level as 1
        and specifies the database
        """
        self.command_params = ["Judy", "-level=1", "-dbs=os-version"]
        self.excepted_str = self.read_file_content(
            "installdep_Judy_level_1_dbs.txt",
            folder=INSTALLDEP_EXPECTED_DATA_FOLDER,
            is_json=False,
        )
        self.assert_result()

    def test_true_level_db(self):
        """
        The installation depends on the specified query for the specified database
        """
        self.command_params = ["Judy", "-dbs=os-version"]
        self.excepted_str = self.read_file_content(
            "installdep_Judy_dbs.txt",
            folder=INSTALLDEP_EXPECTED_DATA_FOLDER,
            is_json=False,
        )
        self.assert_result()

    def test_error_es_data_return_not_resp(self):
        """test_get_install_error_data_to_raise_keyerror"""

        self.command_params = ["Judy", "-dbs=os-version"]
        self.excepted_str = """
ERROR_CONTENT  :The querying package does not exist in the databases
HINT           :Use the correct package name and try again
    """
        self.mock_es_search(side_effect=[DATA_BASE_INFO, {}])
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
ERROR_CONTENT  :{"test":\'123\',}
HINT           :The content is not a legal json format,please check the parameters is valid
    """
        self._to_update_kw_and_make_mock(
            "packageship.application.common.remote.RemoteService.text",
            new_callable=PropertyMock,
            return_value="""{"test":'123',}""",
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
