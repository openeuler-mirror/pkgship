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
test_get_pkgship_cmd
"""
from packageship.application.cli.commands.db import DbPriorityCommand
from test.cli import DATA_BASE_INFO
from test.cli.dbs_command import DbsTest


class TestDB(DbsTest):
    """
    class for test DB priority
    """
    cmd_class = DbPriorityCommand

    def test_true_params(self):
        """
        test true params
        """
        self.mock_es_search(return_value=DATA_BASE_INFO)
        self.excepted_str = """
DB priority
['os-version']
        """
        self.assert_result()


    def test_different_db_priority(self):
        """
        test different db priority
        """
        self.excepted_str = """
DB priority
['os-version-1', 'os-version-2', 'os-version-3']
        """
        self.mock_es_search(return_value=self.read_file_content("different_priority_dbs.json"))
        self.assert_result()

    def test_same_db_priority(self):
        """
        test same db priority
        """
        self.excepted_str = """
DB priority
['os-version-1', 'aa', 'bbb', 'test']
        """
        self.mock_es_search(return_value=self.read_file_content("same_priority_dbs.json"))
        self.assert_result()

    def test_wrong_db_data(self):
        """
        test wrong dbs data
        """
        self.excepted_str = """
ERROR_CONTENT  :Unable to get the generated database information
HINT           :Make sure the generated database information is valid
        """
        self.mock_es_search(return_value={})
        self.assert_result()
