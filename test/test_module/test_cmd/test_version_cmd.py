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
test_get_pkgship_cmd
"""
import json
import sys
import unittest
import argparse
from unittest import mock
from requests.exceptions import ConnectionError as ConnErr
from test.base_code.common_test_code import mock_get_response
from packageship.application.cli.commands.version import VersionCommand


class Redirect:
    _content = ""

    def write(self, s):
        self._content += s

    def flush(self):
        self._content = ""

    def getvalue(self):
        return self._content


class TestVersion(unittest.TestCase):
    """
    class for test version
    """
    def setUp(self) -> None:
        self.r = Redirect()
        sys.stdout = self.r

    @mock.patch("packageship.application.common.remote.RemoteService.get")
    def test_true_params(self, mock_get):
        """
        test true params
        """
        parser = argparse.ArgumentParser()
        version_command = VersionCommand()
        data = {'code': '200', 'message': 'Successful Operation', 'version': '1.0', 'release': '1.1.0'}
        mock_get.return_value = mock_get_response(200, json.dumps(data))
        parser.add_argument('-remote')
        args = parser.parse_args(['-remote', False])
        version_command.do_command(args)
        c = self.r.getvalue().strip()
        s = """
Version:1.0
Release:1.1.0
            """.strip()
        self.assertEqual(c, s)

    @mock.patch("packageship.application.common.remote.RemoteService.get")
    def test_wrong_status_code(self, mock_get):
        """
        test wrong status code
        """
        parser = argparse.ArgumentParser()
        version_command = VersionCommand()
        data = ''
        mock_get.return_value = mock_get_response(400, data)
        parser.add_argument('-remote')
        args = parser.parse_args(['-remote', False])
        version_command.do_command(args)
        c = self.r.getvalue().strip()
        s = """
Request failed
400 Client Error: None for url: None
                    """.strip()
        self.assertEqual(c, s)

    @mock.patch("packageship.application.common.remote.RemoteService.get")
    def test_wrong_resp_code(self, mock_get):
        """
        test wrong resp code
        """
        parser = argparse.ArgumentParser()
        version_command = VersionCommand()
        data = json.dumps({'code': '4001'})
        mock_get.return_value = mock_get_response(200, data)
        parser.add_argument('-remote')
        args = parser.parse_args(['-remote', False])
        version_command.do_command(args)
        c = self.r.getvalue().strip()
        s = """
ERROR_CONTENT  :
HINT           :Please check the parameter is valid and query again
Failed to get the version
                       """.strip()
        self.assertEqual(c, s)

    @mock.patch("packageship.application.common.remote.RemoteService.get")
    def test_wrong_resp_text(self, mock_get):
        """
        test wrong resp text
        """
        parser = argparse.ArgumentParser()
        version_command = VersionCommand()
        data = ''
        mock_get.return_value = mock_get_response(200, data)
        parser.add_argument('-remote')
        args = parser.parse_args(['-remote', False])
        version_command.do_command(args)
        c = self.r.getvalue().strip()
        s = """
ERROR_CONTENT  :
HINT           :The content is not a legal json format,please check the parameters is valid
                    """.strip()
        self.assertEqual(c, s)

    @mock.patch("packageship.application.common.remote.RemoteService.get", side_effect=ConnErr)
    def test_bad_request(self, mock_get):
        """
        test bad request
        """
        parser = argparse.ArgumentParser()
        version_command = VersionCommand()
        mock_get.return_value = None
        parser.add_argument('-remote')
        args = parser.parse_args(['-remote', False])
        version_command.do_command(args)
        c = self.r.getvalue().strip()
        s = """
ERROR_CONTENT  :
HINT           :Please check the connection and try again
                      """.strip()
        self.assertEqual(c, s)
