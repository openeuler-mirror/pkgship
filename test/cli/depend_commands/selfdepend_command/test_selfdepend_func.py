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
"""
Test query self_depend
"""
import os
from collections import namedtuple

from packageship.application.cli.commands.selfdepend import SelfDependCommand
from packageship.application.common.exc import ElasticSearchQueryException
from test.cli.depend_commands import DependTestBase

EXPECT_DATA_FILE = os.path.join(os.path.abspath(os.path.dirname(__file__)), "except_data")


class TestSelfDepend(DependTestBase):
    """
    Class of test query self depend
    """
    cmd_class = SelfDependCommand
    binary_file = "os-version-binary.json"
    source_file = "os-version-source.json"
    package_source_file = "os-version-source-package.json"
    component_file = "os-version-binary-component.json"
    PostResponse = namedtuple('PostResponse', ['status_code', 'text'])

    def test_normal(self):
        """
        No additional parameters when testing the query
        Returns:
        """
        self.command_params = ['Judy', '-dbs', 'os-version']
        self.excepted_str = self.read_file_content(self._get_expect_data('selfdep.txt'), is_json=False)
        self.assert_result()

    def test_normal_with_b(self):
        """
        Additional parameter -b when testing the query
        Returns:
        """
        self.command_params = ['Judy', '-dbs', 'os-version', '-b']
        self.excepted_str = self.read_file_content(self._get_expect_data('selfdep_b.txt'), is_json=False)
        self.assert_result()

    def test_normal_with_bs(self):
        """
        Additional parameter -b,-s when testing the query
        Returns:
        """
        self.command_params = ['Judy', '-dbs', 'os-version', '-b', '-s']
        self.excepted_str = self.read_file_content(self._get_expect_data('selfdep_bs.txt'), is_json=False)
        self.assert_result()

    def test_normal_with_bw(self):
        """
        Additional parameter -b,-w when testing the query
        Returns:
        """
        self.command_params = ['Judy', '-dbs', 'os-version', '-b', '-w']
        self.excepted_str = self.read_file_content(self._get_expect_data('selfdep_bw.txt'), is_json=False)
        self.assert_result()

    def test_normal_with_bsw(self):
        """
        Additional parameter -b,-s,-w when testing the query
        Returns:
        """
        self.command_params = ['Judy', '-dbs', 'os-version', '-b', '-s', '-w']
        self.excepted_str = self.read_file_content(self._get_expect_data('selfdep_bsw.txt'), is_json=False)
        self.assert_result()

    def test_normal_with_s(self):
        """
        Additional parameter -s when testing the query
        Returns:
        """
        self.command_params = ['Judy', '-dbs', 'os-version', '-s']
        self.excepted_str = self.read_file_content(self._get_expect_data('selfdep_s.txt'), is_json=False)
        self.assert_result()

    def test_normal_with_sw(self):
        """
        Additional parameter -s,-w when testing the query
        Returns:
        """
        self.command_params = ['Judy', '-dbs', 'os-version', '-s', '-w']
        self.excepted_str = self.read_file_content(self._get_expect_data('selfdep_sw.txt'), is_json=False)
        self.assert_result()

    def test_normal_with_w(self):
        """
        Additional parameter -w when testing the query
        Returns:
        """
        self.command_params = ['Judy', '-dbs', 'os-version', '-w']
        self.excepted_str = self.read_file_content(self._get_expect_data('selfdep_w.txt'), is_json=False)
        self.assert_result()

    def test_normal_no_specify_db(self):
        """
        Do not specify the database when testing the query
        Returns:
        """
        self.command_params = ['Judy']
        self.excepted_str = self.read_file_content(self._get_expect_data('selfdep.txt'), is_json=False)
        self.assert_result()

    def test_not_found_package(self):
        """
        Test query a not exist package
        Returns: None
        """
        self.command_params = ['Judy1', '-dbs', 'os-version']
        self.excepted_str = "ERROR_CONTENT  :The querying package does not exist in the databases\n" \
                            "HINT           :Use the correct package name and try again"
        self.assertEquals(self.excepted_str, self.print_result)

    def test_uninviliable_param(self):
        """
        Test input uninviliable param
        Returns: None
        """
        self.command_params = ["Judy", "-f"]
        with self.assertRaises(SystemExit):
            self._execute_command()

    def test_es_has_exception(self):
        """
        Test elasticsearch is uninviliable
        Returns:
        """
        self.command_params = ['Judy', '-dbs', 'os-version']
        self.mock_es_search(side_effect=[ElasticSearchQueryException])
        self.excepted_str = "ERROR_CONTENT  :Request parameter error\n" \
                            "HINT           :Please check the parameter is valid and query again"
        self.assert_exc_result()

    def test_request_exception(self):
        """
        Test request has exception
        Returns:
        """
        self.command_params = ['Judy', '-dbs', 'os-version']
        self.mock_requests_post(return_value=self.PostResponse(status_code=500, text=""))
        self.assert_exc_result()

    @staticmethod
    def _get_expect_data(file_name):
        """
        Get expected data
        Args:
            file_name: file of  expected data
        Returns:
        """
        return os.path.join(EXPECT_DATA_FILE, file_name)
