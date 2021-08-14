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
Compare cli parent test class
"""
import os
import shutil
from pathlib import Path

from flask import Response

from test.cli import ClientTest

MOCK_DATA_PATH = Path(Path(__file__).parent, "mock_data")
OUT_PATH = Path(Path(__file__).parent, "out_path")


class CompareBase(ClientTest):
    """
    Compare cli parent test class
    """
    success_code = 200
    mock_data_file = MOCK_DATA_PATH
    out_path = OUT_PATH

    def setUp(self) -> None:
        super(CompareBase, self).setUp()
        if not os.path.isdir(self.out_path):
            os.mkdir(self.out_path)
        os.chmod(self.out_path, 0o755)

    def mock_get_version_success(self):
        """
        Mock query pkgship version success
        """
        response = Response()
        response.status_code = 200
        self.mock_requests_get(return_value=response)

    def mock_query_all_database(self):
        """
        Simulate query all initialization database operations
        """
        database_mock_file = os.path.join(self.mock_data_file, 'database_info.json')
        self.mock_es_search(return_value=self.read_file_content(database_mock_file))

    def assert_exception_output(self):
        """
        Assert exception information output
        """
        try:
            self._execute_command()
        except ValueError as e:
            self.assertEqual(self.excepted_str, str(e))

    def tearDown(self) -> None:
        """
        Clean up the generated files
        """
        super().tearDown()
        shutil.rmtree(os.path.join(self.out_path))
