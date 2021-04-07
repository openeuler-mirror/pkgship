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
import os
from test.cli.init_command import InitTestBase
from test.cli.init_command.relationship_than import RelationComparison


class ComparisonSource(InitTestBase, RelationComparison):
    """Compare the results of the source package"""
    _dirname = os.path.dirname(__file__)

    def setUp(self):
        super(ComparisonSource, self).setUp()
        self.prepare(test=self, dirname=self._dirname)
        self._mock_binary_depend()

    def _comparison_result(self, client, actions, stats_only=False, *args, **kwargs):
        source = actions[0]["_source"]
        json_path = os.path.join(self._dirname, "source.json")
        right_relation = self._load_json(path=json_path)
        self.assertDictEqual(right_relation, source)

    def test_comparison_source(self):
        """
        Compare the results of the source package
        """
        self.command_params = []
        self._execute_command()

    def tearDown(self) -> None:
        self.tear_down()
