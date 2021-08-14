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
Test compare cli
"""
import os.path

from requests import RequestException

from packageship.application.cli.commands.comparedep import CompareCommand
from test.cli.compare_command import CompareBase

SINGLE_CSV_FILE_COUNT = 1
CSV_FILE_COUNT = 4


class CompareTest(CompareBase):
    """
    Test compare cli
    """
    cmd_class = CompareCommand

    def test_service_not_start(self):
        """
        The service is not started when the test query is compared
        """
        self.mock_requests_get(side_effect=RequestException)
        self.command_params = ['-t', 'build']
        self.excepted_str = "[ERROR] The pkgship service is not started,please start the service first"
        self.assert_exception_output()

    def test_input_empty(self):
        """
        Test input parameters have null values
        """
        self.command_params = ['-t', 'build']
        self.excepted_str = "[ERROR] Parameter error, please check the parameter and query again."
        self.assert_exception_output()

    def test_depend_type_unavailable(self):
        """
        Dependency type for which test input is not available
        """
        self.command_params = ['-t', 'test', '-dbs', 'openEuler21.03', '-o', str(self.out_path)]
        self.excepted_str = "[ERROR] Dependent type (test) is not supported, please enter again."
        self.assert_exception_output()

    def test_input_same_database(self):
        """
        Test input the same database
        """
        self.command_params = ['-t', 'build', '-dbs', 'openEuler21.03', 'openEuler21.03', '-o', str(self.out_path)]
        self.excepted_str = "[ERROR] Duplicate database entered."
        self.assert_exception_output()

    def test_input_more_than_four_dbs(self):
        """
        Test input more than 4 databases
        """
        self.command_params = ['-t', 'build', '-dbs', 'fedora30', 'fedora31', 'fedora32', 'fedora33', 'fedora34', '-o',
                               str(self.out_path)]
        self.excepted_str = "[ERROR] Supports up to four databases."
        self.assert_exception_output()

    def test_input_not_support_db(self):
        """
        Unsupported database for test input
        """
        self.command_params = ['-t', 'build', '-dbs', 'openEuler20.09', '-o', str(self.out_path)]
        self.excepted_str = "[ERROR] Database (openEuler20.09) is not supported, please enter again."
        self.assert_exception_output()

    def test_out_path_is_not_exist(self):
        """
        Test output path is empty
        """
        test_path = os.path.join(self.out_path, "test")
        self.command_params = ['-t', 'build', '-dbs', 'openEuler21.03', '-o', str(test_path)]
        self.excepted_str = f"[ERROR] Output path ({str(test_path)}) " \
                            f"not exist or does not support user pkgshipuser writing."
        self.assert_exception_output()

    def test_out_path_is_not_permission(self):
        """
        Test No access to  output path
        """
        os.chmod(self.out_path, 0o644)
        self.command_params = ['-t', 'build', '-dbs', 'openEuler21.03', '-o', str(self.out_path)]
        self.excepted_str = f"[ERROR] Output path ({str(self.out_path)}) " \
                            f"not exist or does not support user pkgshipuser writing."
        self.assert_exception_output()

    def test_one_database_input(self):
        """
        Test input into a database
        """
        self.command_params = ['-t', 'build', '-dbs', 'openEuler21.03', '-o', str(self.out_path)]
        self.excepted_str = '[INFO] The data comparison is successful'
        self.assertIn(self.excepted_str, self.print_result)
        self._assert_csv_count(SINGLE_CSV_FILE_COUNT)

    def test_normal_input(self):
        """
        Test input into a database
        """
        self.command_params = ['-t', 'install', '-dbs', 'openEuler21.03', 'fedora32', 'centos7', '-o', str(self.out_path)]
        self.excepted_str = '[INFO] The data comparison is successful'
        self.assertIn(self.excepted_str, self.print_result)
        self._assert_csv_count(CSV_FILE_COUNT)

    def _assert_csv_count(self, csv_num):
        """
        Determine the number of csv generated
        """
        csv_files = list()
        for _, _, file in os.walk(self.out_path):
            csv_files = [file_name for file_name in file if file_name.endswith('.csv')]
        self.assertEqual(len(csv_files), csv_num)
