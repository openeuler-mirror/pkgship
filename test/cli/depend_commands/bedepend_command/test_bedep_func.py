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
test_be_depend_cmd
"""
from pathlib import Path
from unittest.mock import PropertyMock
from requests.exceptions import ConnectionError, RequestException
from packageship.application.common.exc import ElasticSearchQueryException
from packageship.application.cli.commands.bedepend import BeDependCommand
from test.cli import DATA_BASE_INFO
from test.cli.depend_commands import DependTestBase

BEDEPEND_EXPECTED_DATA_FOLDER = Path(Path(__file__).parent, "expected_data")

class TestBeDepend(DependTestBase):
    """
    class for test Be Depend
    """

    cmd_class = BeDependCommand
    binary_file = "os-version-bedepend.json"
    source_file = "os-version-source-bedepend.json"

    def test_install_build_exist_at_the_same_time(self):
        """
        test install build exist at the same time
        """
        self.command_params = ["os-version", "Judy", "CUnit", "-install", "-build"]
        self.excepted_str = ""
        with self.assertRaises(SystemExit):
            self.assertTrue(self.excepted_str in self.r.getvalue())
            self._execute_command()

    def test_true_param_with_db_pkgname(self):
        """
        test_true_param_with_db_pkgname
        """

        self.command_params = ["os-version", "Judy"]
        self.excepted_str = self.read_file_content(
            "bedepend_Judy.txt",
            folder=BEDEPEND_EXPECTED_DATA_FOLDER,
            is_json=False,
        )
        self.assert_result()

    def test_true_params_b(self):
        """
        test true params
        """

        self.command_params = ["os-version", "Judy", "-b"]
        self.excepted_str = self.read_file_content(
            "bedepend_Judy_b.txt",
            folder=BEDEPEND_EXPECTED_DATA_FOLDER,
            is_json=False,
        )
        self.assert_result()

    def test_true_params_w(self):
        """
        test true params
        """

        self.command_params = ["os-version", "Judy", "-w"]
        self.excepted_str = self.read_file_content(
            "bedepend_Judy_w.txt",
            folder=BEDEPEND_EXPECTED_DATA_FOLDER,
            is_json=False,
        )
        self.assert_result()

    def test_true_params_w_b(self):
        """
        test true params
        """

        self.command_params = ["os-version", "Judy", "-w", "-b"]
        self.excepted_str = self.read_file_content(
            "bedepend_Judy_w_b.txt",
            folder=BEDEPEND_EXPECTED_DATA_FOLDER,
            is_json=False,
        )
        self.assert_result()

    def test_true_params_install(self):
        """
        test true params
        """

        self.command_params = ["os-version", "Judy", "-install"]
        self.excepted_str = self.read_file_content(
            "bedepend_Judy_install.txt",
            folder=BEDEPEND_EXPECTED_DATA_FOLDER,
            is_json=False,
        )
        self.assert_result()

    def test_true_params_build(self):
        """
        test true params
        """

        self.command_params = ["os-version", "Judy", "-build"]
        self.excepted_str = self.read_file_content(
            "bedepend_Judy_build.txt",
            folder=BEDEPEND_EXPECTED_DATA_FOLDER,
            is_json=False,
        )
        self.assert_result()

    def test_true_params_b_install(self):
        """
        test true params
        """

        self.command_params = ["os-version", "Judy", "-b", "-install"]
        self.excepted_str = self.read_file_content(
            "bedepend_Judy_b_install.txt",
            folder=BEDEPEND_EXPECTED_DATA_FOLDER,
            is_json=False,
        )
        self.assert_result()

    def test_true_params_b_build(self):
        """
        test true params
        """

        self.command_params = ["os-version", "Judy", "-b", "-build"]
        self.excepted_str = self.read_file_content(
            "bedepend_Judy_b_build.txt",
            folder=BEDEPEND_EXPECTED_DATA_FOLDER,
            is_json=False,
        )
        self.assert_result()

    def test_true_params_w_install(self):
        """
        test true params
        """

        self.command_params = ["os-version", "Judy", "-w", "-install"]
        self.excepted_str = self.read_file_content(
            "bedepend_Judy_w_install.txt",
            folder=BEDEPEND_EXPECTED_DATA_FOLDER,
            is_json=False,
        )
        self.assert_result()

    def test_true_params_w_build(self):
        """
        test true params
        """

        self.command_params = ["os-version", "Judy", "-w", "-build"]
        self.excepted_str = self.read_file_content(
            "bedepend_Judy_w_build.txt",
            folder=BEDEPEND_EXPECTED_DATA_FOLDER,
            is_json=False,
        )
        self.assert_result()

    def test_true_params_b_w_install(self):
        """
        test true params
        """

        self.command_params = ["os-version", "Judy", "-w", "-b", "-install"]
        self.excepted_str = self.read_file_content(
            "bedepend_Judy_b_w_install.txt",
            folder=BEDEPEND_EXPECTED_DATA_FOLDER,
            is_json=False,
        )
        self.assert_result()

    def test_true_params_b_w_build(self):
        """
        test true params
        """

        self.command_params = ["os-version", "Judy", "-w", "-b", "-build"]
        self.excepted_str = self.read_file_content(
            "bedepend_Judy_b_w_build.txt",
            folder=BEDEPEND_EXPECTED_DATA_FOLDER,
            is_json=False,
        )
        self.assert_result()

    def _assert_result(self):
        """ new assert_result method user assertEqual"""
        self.assertEqual(self.excepted_str.strip("\n").strip(), self.print_result)

    def test_db_name_error(self):
        """test_db_name_error"""

        self.command_params = ["os-version-123", "Judy"]
        self.excepted_str = """
ERROR_CONTENT  :Request parameter error
HINT           :Please check the parameter is valid and query again
"""
        self._assert_result()

    def test_package_not_found_src(self):
        """test_package_not_found"""

        self.command_params = ["os-version", "Judy_123"]
        self.excepted_str = """
ERROR_CONTENT  :The querying package does not exist in the databases
HINT           :Use the correct package name and try again
"""
        self._assert_result()

    def test_package_not_found_bin(self):
        """test_package_not_found"""

        self.command_params = ["os-version", "Judy_123", "-b"]
        self.excepted_str = """
ERROR_CONTENT  :The querying package does not exist in the databases
HINT           :Use the correct package name and try again
"""
        self._assert_result()

    def test_error_es_data_return_not_resp(self):
        """test_get_be_req_error_data_to_raise_keyerror"""

        self.command_params = ["os-version", "Judy_123", "-b"]
        self.excepted_str = """
ERROR_CONTENT  :The querying package does not exist in the databases
HINT           :Use the correct package name and try again
"""
        self.mock_es_search(side_effect=[DATA_BASE_INFO, {}])
        self._assert_result()

    def test_raise_es_error(self):
        """test_raise_es_error"""

        self.command_params = ["os-version", "Judy"]
        self.excepted_str = """
ERROR_CONTENT  :Failed to Connect the database
HINT           :Check the connection
"""
        self.mock_es_search(side_effect=[DATA_BASE_INFO, ElasticSearchQueryException])
        self._assert_result()

    def test_request_raise_connecterror(self):
        """test_request_raise_connecterror"""

        self.command_params = ["os-version", "Judy"]
        self.excepted_str = """
ERROR_CONTENT  :There seems to be a problem with the service
HINT           :Please check the connection and try again
"""
        self._to_update_kw_and_make_mock(
            "packageship.application.common.remote.RemoteService.request",
            effect=ConnectionError,
        )
        self._assert_result()

    def test_request_raise_requestexception(self):
        """test_request_raise_requestexception"""

        self.command_params = ["os-version", "Judy"]
        self.excepted_str = """
ERROR_CONTENT  :
HINT           :The remote connection is abnormal, please check the 'remote_host' parameter value to ensure the connectivity of the remote address
"""
        self._to_update_kw_and_make_mock(
            "packageship.application.common.remote.RemoteService.request",
            effect=RequestException,
        )
        self._assert_result()

    def test_request_text_raise_jsonerror(self):
        """test_request_text_raise_jsonerror"""

        self.command_params = ["os-version", "Judy"]
        self.excepted_str = """
ERROR_CONTENT  :{"test":\'123\',}
HINT           :The content is not a legal json format,please check the parameters is valid
"""
        self._to_update_kw_and_make_mock(
            "packageship.application.common.remote.RemoteService.text",
            new_callable=PropertyMock,
            return_value="""{"test":'123',}""",
        )
        self._assert_result()

    def test_request_status_500(self):
        """test_request_status_500"""

        self.command_params = ["os-version", "Judy"]
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
        self._assert_result()
