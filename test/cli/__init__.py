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
test_pkgship_cmd
"""
import os
import sys
import unittest
import json
from pathlib import Path
from flask.wrappers import Response
from packageship import BASE_PATH


mock_data_folder = str(Path(Path(__file__).parent, "mock_data"))
with open(str(Path(mock_data_folder, "databaseinfo.json")), "r", encoding="utf-8") as f:
    data_base_info = json.loads(f.read())

correct_data_folder = str(Path(mock_data_folder, "correct_print"))


class Redirect:
    """
    Class for redirect print to class Attr :_content
    """

    _content = ""

    def write(self, s):
        """add stdout result string to _content 

        Args:
            s (str): [description]
        """
        self._content += s

    def flush(self):
        """flush _content
        """
        self._content = ""

    def getvalue(self):
        """get content value

        Returns:
            str: _content string value
        """
        return self._content


class BaseTest(unittest.TestCase):
    """
    class for Test Base
    """

    cmd_class = None

    def setUp(self) -> None:
        """
        setUp Test Environment
        """
        self.command_params = []
        self.excepted_str = ""
        self.r = Redirect()
        sys.stdout = self.r

    @staticmethod
    def read_mock_data_json(file_name: str, is_json=True):
        """

        Args:
            file_name: file name in mock_data folder or in correct_print folder
            is_json: return data is json load to dict or not json

        Returns:
            file's content:if is_json is True return dict else return str

        """

        curr_p = Path(mock_data_folder, file_name)
        if not curr_p.exists():
            curr_p = Path(correct_data_folder, file_name)

        with open(str(curr_p), "r", encoding="utf-8") as f_p:
            if is_json:
                return json.loads(f_p.read())
            else:
                return f_p.read()

    def _execute_command(self):
        """
        To Simulated execution command line
        Returns:
            None
        """
        if self.cmd_class is None:
            raise ValueError(
                f"please check cmd_class variable in your {self},"
                f"assignment current do command class name"
            )

        ins = self.cmd_class()
        ins.register()
        args = ins.parse.parse_args(self.command_params)
        ins.do_command(args)

    @property
    def print_result(self):
        """
        execute cmd and return print redirect content
        Returns:
            print redirect result
        """
        self._execute_command()
        return self.r.getvalue().strip()

    def assert_result(self):
        """
        to assert command lines result as same sa excepted str
        Returns:
            None
        """
        self.assertEqual(
            self.excepted_str.strip().strip("\r\n").strip("\n"), self.print_result
        )

    @classmethod
    def tearDownClass(cls) -> None:
        """
        tearDown to restore stdout redirect
        Returns:
            None
        """
        sys.stdout = sys.__stdout__


class ClientTest(BaseTest):
    def setUp(self) -> None:
        """
        Client Test setup
        Set Environment variable "SETTINGS_FILE_PATH" to project pacjage.ini path
        """
        os.environ["SETTINGS_FILE_PATH"] = str(Path(BASE_PATH, "package.ini"))
        from packageship.selfpkg import app

        super(ClientTest, self).setUp()
        self.client = app.test_client()
        Response.text = Response.data
        Response.content = Response.data

    def tearDown(self) -> None:
        """
        to restore Environment variable "SETTINGS_FILE_PATH"

        Returns:
            None
        """
        os.environ["SETTINGS_FILE_PATH"] = "/etc/pkgship/package.ini"
        return super().tearDown()