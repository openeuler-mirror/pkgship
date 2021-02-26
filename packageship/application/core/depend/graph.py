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
Dependent graph
"""
import random
from packageship.application.common import constant


class GraphInfo:
    """
    generate graph based on depend result
    """

    def __init__(self, depend):
        self._nodes = dict()
        self._edges = list()
        self._depend = depend
        self._up = set()
        self._down = set()

    @property
    def _color(self):
        """
        Description: rgb random color value acquisition
        """
        color = ['#E02020', '#FA6400', '#F78500', '#6DD400', '#44D7B6',
                 '#32C5FF', '#0091FF', '#6236FF', '#B620E0', '#6D7278']
        return color[random.randint(0, 9)]

    @property
    def _quadrant(self):
        """Get the coordinate quadrant at random"""
        quadrant = [1, -1]
        return quadrant[random.randint(0, 1)]

    @property
    def _coordinate(self):
        """
        Description: calculate the random coordinates of each package in the current level

        Returns:
            The coordinate value of the dynamically calculated dependent package
            example : (x, y)
        """
        _x, _y = random.uniform(0, constant.LEVEL_RADIUS) * self._quadrant, random.uniform(
            0, constant.LEVEL_RADIUS) * self._quadrant
        return _x, _y

    @property
    def node_size(self):
        """
        Description: calculate the size of each node
        """
        node_size = random.uniform(1, constant.NODE_SIZE)
        return node_size

    @property
    def edges(self):
        """
        Description: edges values
        """
        return self._edges

    @edges.setter
    def edges(self, node):
        self._edges.append(dict(
            sourceID=node["source"],
            targetID=node["target"]
        ))

    @property
    def nodes(self):
        """
        Description: Regroup node values
        """
        return [node for key, node in self._nodes.items()]

    @nodes.setter
    def nodes(self, package):
        """
        Description: graph node

        Args:
            package_name: Dependent package name
        """
        _x, _y = self._coordinate

        self._nodes[package] = dict(
            color=self._color,
            label=package,
            y=_y,
            x=_x,
            id=package,
            size=self.node_size)

    def _downward(self, downward_node, depend_data):
        """
        Description: Depends on the lower node of the graph

        Args:
            downward_node:node on which the upper layer depends
            depend_data: Dependency data
        Returns:
            node on which the next layer depends
        """
        _downward_node = set()
        for node in downward_node:
            self._down.add(node)
            try:
                for require in depend_data[node]["requires"]:
                    self.edges = {"source": node, "target": require}
                    self.nodes = require
                    _downward_node.add(require)
            except KeyError:
                continue

        return _downward_node

    def _upward(self, upward_node, depend_data):
        """
        Description: Depends on the upper node of the graph

        Args:
            downward_node:upper level depends on several points
            depend_data: Dependency data
        Returns:
            With a layer of dependent nodes
        """
        _upward_node = set()
        for node in upward_node:
            self._up.add(node)
            try:
                for require in depend_data[node]["be_requires"]:
                    self.edges = {"source": require, "target": node}
                    self.nodes = require
                    _upward_node.add(require)
            except KeyError:
                continue

        return _upward_node

    def _graph(self, root_node, depend_data, level):
        _downward = set([root_node])
        _upward = set([root_node])
        while (_downward or _upward) and level != 0:

            if _downward:
                _downward = self._downward(_downward, depend_data)
            if _upward:
                _upward = self._upward(_upward, depend_data)
            _downward = _downward - self._down
            _upward = _upward - self._up
            level -= 1

    def generate_graph(self, root_node, package_type, level=2):
        """
        Description: auto generate coordinates and graph

        Args:
            level:hierarchy of dependencies
        """
        builds = [root_node]
        if package_type == "source":
            _binary, _source_data = self._depend.depend_dict
            try:
                builds = [build for build in _source_data[root_node]["build"]]
            except KeyError:
                self.nodes = root_node
                return dict(edges=self.edges, nodes=self.nodes)

            self.nodes = root_node
            for require in builds:
                self.edges = {"source": root_node, "target": require}
            level = level - 1

        for pkg in builds:
            try:
                depend_data = self._depend.filter_dict(level=level, root=pkg)
            except ValueError:
                continue
            if depend_data:
                self.nodes = pkg
                self._graph(pkg, depend_data, level)
        return dict(edges=self.edges, nodes=self.nodes)
