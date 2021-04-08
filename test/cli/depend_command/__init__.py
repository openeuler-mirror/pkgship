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
import re
from itertools import zip_longest
from collections import defaultdict
from requests.exceptions import RequestException
from test.cli import ClientTest, DATA_BASE_INFO
from packageship.application.common.remote import RemoteService
from redis import RedisError


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
        cls.data_base_info_dict = DATA_BASE_INFO
        if hasattr(cls, "binary_file"):
            cls.binary_data = cls.read_file_content(cls.binary_file)
        if hasattr(cls, "source_file"):
            cls.source_data = cls.read_file_content(cls.source_file)
        if hasattr(cls, "package_source_file"):
            cls.package_source_data = cls.read_file_content(cls.package_source_file)
        if hasattr(cls, "component_file"):
            cls.component_data = cls.read_file_content(cls.component_file)
            cls.component_provides_process_data = defaultdict(set)
            cls.component_files_process_data = defaultdict(set)
            for k, v in cls.component_data.items():
                for pro in v["_source"]["provides"]:
                    cls.component_provides_process_data[pro["name"]].add(k)
                for fs in v["_source"]["files"]:
                    cls.component_files_process_data[fs["name"]].add(k)

    def setUp(self) -> None:
        """
        set up depend Test environment
        Returns:None

        """
        super(DependTestBase, self).setUp()
        RemoteService.request = request
        self.mock_requests_post(side_effect=self.client.post)
        self.mock_es_search()
        self.mock_redis_exists_raise_error()

    def mock_redis_exists_raise_error(self):
        """mock_redis_exists_side_effect"""
        self._to_update_kw_and_make_mock(
            "packageship.application.common.constant.REDIS_CONN.exists", RedisError
        )

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
                    if isinstance(value, str):
                        ret = [value]
                    else:
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
    def make_newline_split_res(ln, lines, idx):
        """return newline list use split rule

        Match the position after the string breaks
            e.g.
            command lines:
                binary-name-help-   src-name-help    os-version-orc-
                1.1                                  123
            the first row split result is ["binary-name-help-","src-name-help","os-version-orc-"]
            The expected sharding data for the second row is ["1.1","","123"].
            And then return it to the upper layer for merge.
        The function implements is the processing and return of this expected value.

        Args:
            ln (str): line of command lines
            lines(list):command splitlines result
            idx (int): index of command lines


        Raises:
            IndexError: index must be gte 1

        Returns:
            list: ["str"*n]
        """
        pattern = re.compile("\S+")
        if idx < 1:
            raise IndexError("index must be gte 1")
        last_str_col_pos = [
            (m.start(), m.end() + 1) for m in pattern.finditer(lines[idx - 1])
        ]

        ret_line_pos = ["" for _ in last_str_col_pos]
        curr_ln_col_pos = [(m.start(), m.end() + 1) for m in pattern.finditer(ln)]
        for curr_range in curr_ln_col_pos:
            curr_pos_set = set(range(*curr_range))
            for ids, last_range in enumerate(last_str_col_pos):
                last_pos_set = set(range(*last_range))
                if curr_pos_set.intersection(last_pos_set):
                    ret_line_pos[ids] = ln[slice(*curr_range)]
                    break

        return ret_line_pos

    def _process_depend_command_value(self, command_res: str):
        """Processing the output of execute command

        Args:
            command_res (str): execute command res

        Returns:
            binary_lines: binary packages lines
            source_lines: source packages lines
        """
        binary_lines = []
        source_lines = []
        is_binary = False
        is_source = False
        command_lines = command_res.splitlines()

        def handle_tolong_name_in_newline(ln, target_lst, idx):
            """to handle tolong col in newline

            Args:
                ln (str): line of command lines
                target_lst (list): to update list
                idx (int): index of command lines

            Returns:
                bool: midfy or no modify
            """
            try:
                lst = target_lst[-1]
                if len(ln.split()) < len(lst):

                    ln_split = self.make_newline_split_res(ln, command_lines, idx)
                    target_lst[-1] = [
                        pre.strip() + suf.strip() for pre, suf in zip_longest(lst, ln_split, fillvalue="")
                    ]
                    return True
                else:
                    return False
            except IndexError:
                return False

        for idx, ln in enumerate(command_lines):
            line = ln.strip().strip("\r\n").strip("\n")
            if line.startswith("Statistics"):
                break
            if line.startswith("Binary"):
                is_binary = True
                continue
            elif line.startswith("Source"):
                is_source = True
                is_binary = False
                continue

            split_ln = line.strip().split()
            if is_binary and not line.startswith("===="):
                if handle_tolong_name_in_newline(ln, binary_lines, idx):
                    continue

                binary_lines.append(split_ln)

            if is_source and not line.startswith("===="):
                if handle_tolong_name_in_newline(ln, source_lines, idx):
                    continue
                source_lines.append(split_ln)

        return binary_lines, source_lines

    def assert_result(self):
        """
        to execute and assert result
        Returns:
            None
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

        ret_dict = {"hits": {"hits": []}}
        if index == "databaseinfo":
            return DATA_BASE_INFO
        elif "binary" in index:
            if "provides.name" in str(body):
                self._get_components_info(body, ret_dict, "provides.name", self.component_provides_process_data)
            elif "files.name" in str(body):
                self._get_components_info(body, ret_dict, "files.name", self.component_files_process_data)
            else:
                self._update_ret_dict(body["query"], ["name"], ret_dict, self.binary_data)
            return ret_dict
        elif "source" in index:
            if "subpacks" in str(body):
                self._update_ret_dict(body["query"], ["name"], ret_dict, self.package_source_data)
            else:
                self._update_ret_dict(body["query"], ["name"], ret_dict, self.source_data)
            return ret_dict
        else:
            self._update_ret_dict(body["query"], ["binary_name"], ret_dict, self.binary_data)
            return ret_dict

    def _get_components_info(self, body, ret_dict, component_location, components_dict):
        bin_name_set = set()
        pro_lst = self._to_find_value_by_key(body["query"], component_location)
        for pro_name in pro_lst:
            for bin_name in components_dict[pro_name]:
                if bin_name not in bin_name_set:
                    ret_dict["hits"]["hits"].append(self.component_data[bin_name])
                    bin_name_set.add(bin_name)
