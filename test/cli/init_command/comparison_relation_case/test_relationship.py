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
from unittest import mock
from pathlib import Path
from requests import RequestException
from packageship.libs.conf import configuration
from packageship.application.initialize.integration import del_temporary_file
from packageship.application.core.baseinfo import pkg_version
from test.cli.init_command import InitTestBase
from test.cli import ClientTest


CONFIG_CONTENT = """
- dbname: openeuler
  src_db_file: {src}
  bin_db_file: {bin}
  priority: 1
"""
MOCK_DATA_FOLDER = str(Path(Path(__file__).parents[3], "mock_data"))


class ComparisonRelationShip(InitTestBase, ClientTest):
    """Compare the results of the source package"""
    _dirname = os.path.dirname(__file__)

    def setUp(self):
        super(ComparisonRelationShip, self).setUp()
        self._prepare(dirname=self._dirname)

    def _prepare(self, dirname):
        """
        Construct the necessary conditions for comparison of results
        """
        path = os.path.join(dirname, "sqlites")
        _cofig_content = CONFIG_CONTENT.format(src="file://" + os.path.join(path, "src"),
                                               bin="file://" + os.path.join(path, "bin"))
        self._conf = self.create_conf_file(
            content=_cofig_content, path=self._create_file_path)
        configuration.TEMPORARY_DIRECTORY = os.path.join(dirname, "tmp")
        self.comparsion_than()

    def comparsion_result(self, client, actions, stats_only=False, *args, **kwargs):
        _index = actions[0]["_index"]
        if "source" in _index:
            self._comparison_source(actions=actions)
        elif "binary" in _index:
            self._comparison_binary(actions=actions)
        else:
            self._comparison_bedepend(actions=actions)

    def _comparison_source(self, actions):
        json_path = os.path.join(self._dirname, "relationship", "source.json")
        right_relation = self.read_file_content(path=json_path)
        for _source in actions:
            if _source["_source"]["name"] != "CUnit":
                continue
            self.assertDictEqual(right_relation, _source["_source"])
            break

    def _comparison_binary(self,  actions):
        json_path = os.path.join(self._dirname, "relationship", "binary.json")
        right_relation = self.read_file_content(path=json_path)
        for _binarys in actions:
            if _binarys["_source"]["name"] != "Judy":
                continue
            self.assertDictEqual(right_relation, _binarys["_source"])
            break

    def _comparison_bedepend(self, actions):
        json_path = os.path.join(
            self._dirname, "relationship", "bedepend.json")
        right_relation = self.read_file_content(path=json_path)
        for _bedepend in actions:
            if _bedepend["_source"]["binary_name"] != "Judy":
                continue
            self.assertDictEqual(right_relation, _bedepend["_source"])
            break

    def test_service_not_start(self):
        """
        Use case where the service is not started
        """
        self.mock_requests_get(side_effect=RequestException)
        self.command_params = []
        self.excepted_str = """The pkgship service is not started,please start the service first"""
        self.assert_result()

    def test_comparison_relationship(self):
        """
        Compare the results of the source package
        """
        pkg_version.file_path = os.path.join(
            MOCK_DATA_FOLDER, "tmp_version.yaml")
        self.mock_requests_get(side_effect=self.client.get)
        self.command_params = []
        self._execute_command()

    def tearDown(self) -> None:
        super().tearDown()
        folder = os.path.join(self._dirname, "conf")
        del_temporary_file(path=folder, folder=True)
        del_temporary_file(path=os.path.join(
            self._dirname, "tmp"), folder=True)
        configuration.TEMPORARY_DIRECTORY = "/opt/pkgship/tmp/"
