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
import operator
from test.cli.depend_commands import DependTestBase
from packageship.application.core.depend import DispatchDepend
from packageship.application.serialize.validate import validate
from packageship.application.serialize.dependinfo import DependSchema

FILES = {
    "level-0-binary-installdep": "judy-judy-level-0-binary-installdep.json",
    "level-0-source-builddep": "judy-judy-level-0-source-builddep.json",
    "level-0-binary-builddep": "judy-gcc-level-0-binary-builddep.json",
    "selfdep-info": "judy-info-selfdep.json",
    "selfdep-info-binary": "judy-info-selfdep-1.json",
    "selfdep-info-self-build": "judy-judy-selfdep-2.json",
    "selfdep-info-subpack": "judy-judy-selfdep-3.json",
    "selfdep-info-subpack-binary": "judy-judy-selfdep-4.json",
    "selfdep-info-self-build-packtype": "judy-judy-selfdep-5.json",
    "selfdep-info-self-build-subpack": "judy-judy-selfdep-6.json",
    "bedep-packtype": "judy-judy-bedep-1.json",
    "bedep-subpack": "judy-judy-bedep-2.json",
    "bedep-search-type": "judy-judy-bedep-3.json",
    "bedep-search-type-packtype": "judy-judy-bedep-4.json",
    "bedep-search-type-subpack": "judy-judy-bedep-5.json",
    "bedep-search-type-supack-packtype": "judy-judy-bedep-6.json"
}


class BaseGraph:
    """
    Graph dependent base class methods
    """
    data_folder = os.path.join(os.path.dirname(__file__), "data")

    def _extract_edges_paramter(self, data):
        """
        Extract request parameters and compare result values
        """
        return data.get("request"), data.get("edges")

    def get_depend_result(self, path):
        """
        Obtain comparative data
        """
        _data = self.read_file_content(path=os.path.join(
            self.data_folder, path))
        request_param, edges = self._extract_edges_paramter(data=_data)
        _param, _ = validate(DependSchema, request_param, load=True)
        return _param, edges

    def _get_graph_data(self, request_param):
        node_name = request_param.pop('node_name')
        node_type = request_param.pop('node_type')
        depend = DispatchDepend.execute(**request_param)
        _graph = depend.depend_info_graph(
            source=node_name, package_type=node_type)
        return _graph["edges"]

    def _order_by(self, graph, key="sourceID"):
        _graph = sorted(graph, key=operator.itemgetter(key))
        return sorted(_graph, key=operator.itemgetter("targetID"))

    def _comparison_results(self, edges, request_param):
        _graph = self._get_graph_data(request_param=request_param)

        self.assertListEqual(self._order_by(_graph), self._order_by(edges))


class TestInstalldepGraph(DependTestBase, BaseGraph):
    """
    The installation depends on the graph test
    """
    binary_file = "os-version-binary.json"
    component_file = "os-version-binary-component.json"

    def setUp(self):
        super(TestInstalldepGraph, self).setUp()

    def test_level_0_binary_installdep(self):
        """
        Install dependent graph tests
        """
        request_param, edges = self.get_depend_result(
            path=FILES["level-0-binary-installdep"])
        self._comparison_results(edges=edges, request_param=request_param)

    def test_level_0_source_installdep(self):
        """
        Install dependent graph tests
        """
        request_param, _ = validate(DependSchema, {
            "packagename": [
                "Judy"
            ],
            "depend_type": "installdep",
            "node_name": "Judy",
            "node_type": "source",
            "parameter": {
                "db_priority": [
                    "os-version"
                ]
            }
        }, load=True)

        self._comparison_results(edges=[], request_param=request_param)


class TestBuilddepGraph(DependTestBase, BaseGraph):
    """
    Compile the dependency graph test
    """
    binary_file = "os-version-binary.json"
    component_file = "os-version-binary-component.json"
    source_file = "os-version-source.json"

    def setUp(self):
        super(TestBuilddepGraph, self).setUp()

    def test_level_0_binary_builddep(self):
        """
        Compile dependent graph tests
        """
        request_param, edges = self.get_depend_result(
            path=FILES["level-0-binary-builddep"])
        self._comparison_results(edges=edges, request_param=request_param)

    def test_level_0_source_builddep(self):
        """
        Compile dependent graph tests
        """
        request_param, edges = self.get_depend_result(
            path=FILES["level-0-source-builddep"])
        self._comparison_results(edges=edges, request_param=request_param)


class TestSelfdepGraph(DependTestBase, BaseGraph):
    """
    Self dependent graph testing
    """
    binary_file = "os-version-binary.json"
    component_file = "os-version-binary-component.json"
    source_file = "os-version-source.json"
    package_source_file = "os-version-source-package.json"

    def setUp(self):
        super(TestSelfdepGraph, self).setUp()

    def test_selfdep_info(self):
        """
        Self dependent data testing
        """
        request_param, edges = self.get_depend_result(
            path=FILES["selfdep-info"])
        self._comparison_results(edges=edges, request_param=request_param)

    def test_selfdep_info_binary(self):
        """
        Self dependent binary packet data testing
        """
        request_param, edges = self.get_depend_result(
            path=FILES["selfdep-info-binary"])
        self._comparison_results(edges=edges, request_param=request_param)

    def test_selfdep_info_self_build(self):
        """
        Self dependent selfbuild to true data test
        """
        request_param, edges = self.get_depend_result(
            path=FILES["selfdep-info-self-build"])
        self._comparison_results(edges=edges, request_param=request_param)

    def test_selfdep_info_subpack(self):
        """
        Self dependent subpack to true data test
        """
        request_param, edges = self.get_depend_result(
            path=FILES["selfdep-info-subpack"])
        self._comparison_results(edges=edges, request_param=request_param)

    def test_selfdep_info_subpack_binary(self):
        """
        Self dependent binary package data test with selfbuild being true
        """
        request_param, edges = self.get_depend_result(
            path=FILES["selfdep-info-subpack-binary"])
        self._comparison_results(edges=edges, request_param=request_param)

    def test_selfdep_info_self_build_packtype(self):
        """
        Self dependent binary package data test with selfbuild being true
        """
        request_param, edges = self.get_depend_result(
            path=FILES["selfdep-info-self-build-packtype"])
        self._comparison_results(edges=edges, request_param=request_param)

    def test_selfdep_info_self_build_subpack(self):
        """
        Self dependent binary package data test with selfbuild being true
        """
        request_param, edges = self.get_depend_result(
            path=FILES["selfdep-info-self-build-subpack"])
        self._comparison_results(edges=edges, request_param=request_param)


class TestBedepGraph(DependTestBase, BaseGraph):
    """
    The dependent base class method
    """
    binary_file = "os-version-bedepend.json"
    source_file = "os-version-source-bedepend.json"

    def setUp(self):
        super(TestBedepGraph, self).setUp()

    def test_bedep_packtype(self):
        """
        Dependent graph tests
        """
        request_param, edges = self.get_depend_result(
            path=FILES["bedep-packtype"])
        self._comparison_results(edges=edges, request_param=request_param)

    def test_bedep_subpack(self):
        """
        Dependent graph tests
        """
        request_param, edges = self.get_depend_result(
            path=FILES["bedep-subpack"])
        self._comparison_results(edges=edges, request_param=request_param)

    def test_bedep_search_type(self):
        """
        Dependent graph tests
        """
        request_param, edges = self.get_depend_result(
            path=FILES["bedep-search-type"])
        self._comparison_results(edges=edges, request_param=request_param)

    def test_bedep_search_type_packtype(self):
        """
        Dependent graph tests
        """
        request_param, edges = self.get_depend_result(
            path=FILES["bedep-search-type-packtype"])
        self._comparison_results(edges=edges, request_param=request_param)

    def test_bedep_search_type_subpack(self):
        """
        Dependent graph tests
        """
        request_param, edges = self.get_depend_result(
            path=FILES["bedep-search-type-subpack"])
        self._comparison_results(edges=edges, request_param=request_param)

    def test_bedep_search_type_supack_packtype(self):
        """
        Dependent graph tests
        """
        request_param, edges = self.get_depend_result(
            path=FILES["bedep-search-type-supack-packtype"])
        self._comparison_results(edges=edges, request_param=request_param)
