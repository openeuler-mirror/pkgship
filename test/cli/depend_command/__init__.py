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
from collections import defaultdict
from unittest.mock import Mock
from requests.exceptions import RequestException
from test.cli import ClientTest, data_base_info
from packageship.application.common.remote import RemoteService
from redis import RedisError
from packageship.application.common.constant import REDIS_CONN


# Redirect RemoteService request function to the current function
# Because the flask app client post method requires a data keyword variable,
# update it to kwargs inside the current function
def request(self, url, method, body=None, max_retry=3, **kwargs):
    if not isinstance(max_retry, int):
        max_retry = 3
    kwargs["data"] = body
    self._retry = max_retry
    self._body = body
    try:
        self._dispatch(method=method, url=url, **kwargs)
    except RequestException as error:
        self._request_error = str(error)


class DependTestBase(ClientTest):
    """
    Depend Test  Base
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Start once when the class is loaded
        Returns:

        """
        cls.data_base_info_dict = data_base_info
        if hasattr(cls, "binary_file"):
            cls.binary_data = cls.read_file_content(cls.binary_file)
        if hasattr(cls, "source_file"):
            cls.source_data = cls.read_file_content(cls.source_file)
        if hasattr(cls, "component_file"):
            cls.component_data = cls.read_file_content(cls.component_file)
            cls.component_process_data = defaultdict(set)
            for k, v in cls.component_data.items():
                for pro in v["_source"]["provides"]:
                    cls.component_process_data[pro["name"]].add(k)
                for fs in v["_source"]["files"]:
                    cls.component_process_data[fs["name"]].add(k)

    def setUp(self) -> None:
        """
        set up depend Test environment
        Returns:None

        """
        super(DependTestBase, self).setUp()
        RemoteService.post = self.client.post
        RemoteService.request = request
        self.mock_redis_exists_raise_error()

    def mock_redis_exists_raise_error(self):
        """mock_redis_exists_side_effect"""
        REDIS_CONN.exists = Mock()
        REDIS_CONN.exists.side_effect = RedisError

    @staticmethod
    def _to_find_value_by_key(dic: dict, find_k_lst: list):
        """
        Look for the specified key in a nested dictionary
        specified key in find_k_lst
        Args:
            dic(dict):es query body
            find_k_lst(list): specified keys list

        Returns:
            ret(list):The value corresponding to the specified key in dic
        """
        ret = []

        def inner(dc):
            nonlocal ret
            for k, value in dc.items():
                if k in find_k_lst:
                    ret = value
                elif isinstance(value, dict):
                    inner(value)

        inner(dic)
        return ret

    def _update_ret_dict(
        self, query_body: dict, k_lst: list, ret_dict_p: dict, data_origin: dict
    ):
        """
        Assemble the acquired data into es return values that can be parsed by the project
        Args:
            query_body: es query body
            k_lst: specified keys list
            ret_dict_p: to update dict
            data_origin:to get info data

        Returns:
            None
        """
        pkg_lst = self._to_find_value_by_key(query_body, k_lst)
        for pkg_name in pkg_lst:
            pkg_info = data_origin.get(pkg_name)
            if not pkg_info:
                continue
            ret_dict_p["hits"]["hits"].append(pkg_info)

    @staticmethod
    def _process_depend_command_value(command_res: str):
        """Processing the output of execute command

        Args:
            command_res (str): execute command res

        Returns:
            binary_lines: binary packages lines
            source_lines: source packages lines
        """
        binary_lines = []
        source_lines = []
        # logic
        return binary_lines, source_lines

    def assert_result(self):
        """
        to execute and assert result
        Returns:

        """
        excepted_bin, excepted_src = self._process_depend_command_value(
            self.excepted_str
        )
        current_bin, current_src = self._process_depend_command_value(self.print_result)
        self.assertListEqual(sorted(excepted_bin), sorted(current_bin))
        self.assertListEqual(sorted(excepted_src), sorted(current_src))

    def _es_search_result(self, index: str, body: dict):
        """
        Get different return values through different call parameters
        Args:
            index(str):es index
            body(dict): es query_body

        Returns:
            ret_dict(dict):Parsable es-like data for the project
        """
        pass
