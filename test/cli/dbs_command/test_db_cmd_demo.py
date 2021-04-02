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
        self.excepted_str = """
DB priority
['os-version']
        """
        self.assert_result()
