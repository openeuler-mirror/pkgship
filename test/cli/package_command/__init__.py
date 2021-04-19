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

from test.cli import ClientTest,ES_COUNT_DATA


class PackageTestBase(ClientTest):
    def setUp(self) -> None:
        """
        set up PackageTestBase
        Returns:

        """
        super(PackageTestBase, self).setUp()
        self.mock_requests_get(side_effect=self.client.get)
        self.mock_es_count(return_value=ES_COUNT_DATA)


    @staticmethod
    def _process_depend_command_value(command_res: str):
        """Processing the output of execute command

        Args:
            command_res (str): execute command res

        Returns:
            binary_lines: binary packages lines
            source_lines: source packages lines
        """

        res_lines = []
        for ln in command_res.splitlines():
            line = ln.strip()
            if line.startswith("====") or line.startswith("-----"):
                continue
            if line:
                res_lines.append(line.strip().split())
        return res_lines

    def assert_result(self):
        """
        to execute and assert result
        Returns:

        """
        excepted_lines = self._process_depend_command_value(self.excepted_str)
        current_lines = self._process_depend_command_value(self.print_result)
        self.assertEqual(excepted_lines, current_lines)
