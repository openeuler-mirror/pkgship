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


class ComparisonBedepend(InitTestBase, RelationComparison):
    """Compare the results of the bedepend relation"""
    _dirname = os.path.dirname(__file__)

    def setUp(self):
        super(ComparisonBedepend, self).setUp()
        self._pass = False
        self.prepare(test=self, dirname=self._dirname)
        self._mock_source_depend()

    def _comparison_result(self, client, actions, stats_only=False, *args, **kwargs):
        json_path = os.path.join(self._dirname, "bedepend.json")
        right_relation = self._load_json(path=json_path)
        if "bedepend" in actions[0]["_index"]:
            for _bedepend in actions:
                if _bedepend["_source"]["binary_name"] != "Judy":
                    continue
                self._pass = True
                self.assertDictEqual(right_relation, _bedepend["_source"])
                break

    def test_comparison_bedepend(self):
        """
        Compare the results of the source package
        """
        self.command_params = []
        self._execute_command()
        self.assertEqual(True, self._pass)

    def tearDown(self) -> None:
        self.tear_down()
