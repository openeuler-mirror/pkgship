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
import json
import unittest
from unittest import mock
from packageship.application.core.depend.graph import GraphInfo
from packageship.application.core.depend.basedepend import BaseDepend


class TestGraphInfo(unittest.TestCase):
    """test graph info"""

    def setUp(self):
        self._path = os.path.join(os.path.dirname(__file__), "data")

    @mock.patch.object(BaseDepend, "filter_dict")
    def test_graph_info_binary(self, mock_filter_dict):
        """Test Graph Data"""
        with open(os.path.join(self._path, "filter_dict.json"), "r") as f:
            data = json.loads(f.read())
            mock_filter_dict.return_value = data

        graph = GraphInfo(depend=BaseDepend())

        graph.generate_graph(root_node="Judy", package_type="binary")

    @mock.patch.object(BaseDepend, "filter_dict")
    def test_graph_info_source(self, mock_filter_dict):
        """Test Graph Data"""
        with open(os.path.join(self._path, "filter_dict.json"), "r") as f:
            data = json.loads(f.read())
            mock_filter_dict.return_value = data

        graph = GraphInfo(depend=BaseDepend())

        graph.generate_graph(root_node="Judy", package_type="source")

    @mock.patch.object(BaseDepend, "filter_dict")
    @mock.patch("packageship.application.core.depend.basedepend.BaseDepend.depend_dict",
                new_callable=mock.PropertyMock)
    def test_graph_type_source(self, mock_depend_dict,  mock_filter_dict):
        """source depend """

        mock_filter_dict.side_effect = ValueError()
        mock_depend_dict.return_value = ({
            "Judy-devel": {
                "name": "Judy-devel",
                "version": "v1.20.0.1",
                "source_name": "Judy",
                "level": 2,
                "database": "openeuler-20.03",
                "install": [
                    "attr",
                    "Judy"
                ]
            }
        }, {"Judy": {
            "name": "Judy",
            "version": "v1.20.0.1",
            "database": "openeuler-20.03",
            "build": [
                "gcc",
                "make"
            ]
        }, "CUnit": {
            "name": "CUnit",
            "version": "v1.20.0.1",
            "database": "openeuler-20.03"
        }})
        graph = GraphInfo(depend=BaseDepend())

        graph.generate_graph(root_node="Judy", package_type="source")
