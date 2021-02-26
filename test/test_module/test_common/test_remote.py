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
import unittest
from unittest import mock
import requests
from requests.exceptions import RequestException
from packageship.application.common.remote import RemoteService


class TestRemoteService(unittest.TestCase):
    """remote service test"""

    def setUp(self):
        self.remote = RemoteService(max_delay=None)

    @mock.patch.object(RemoteService, "_dispatch")
    def test_request_func_exception(self, mock__dispatch):
        """Requested method"""
        mock__dispatch.side_effect = RequestException("request error")
        self.remote.request(url=None, method=None, max_retry=None)
        self.assertEqual("request error", getattr(
            self.remote, "_request_error"))

    def test_request_method_error(self):
        """Request mode error"""
        self.remote.request(url="openeuler", method="delete", max_retry=None)
        self.assertNotEqual(None, getattr(
            self.remote, "_request_error"))

    @mock.patch.object(requests, "get")
    def test_request_get(self, mock_get):
        """get request"""
        mock_get.return_value = requests.Response()
        self.remote.request(url="openeuler", method="get", max_retry=None)
        self.assertNotEqual(None, getattr(
            self.remote, "_request_error"))

    @mock.patch.object(requests, "post")
    def test_request_post(self, mock_post):
        """get request"""
        mock_post.return_value = requests.Response()
        self.remote.request(url="openeuler", method="post", max_retry=None)
        self.assertNotEqual(None, getattr(
            self.remote, "_request_error"))

    @mock.patch.object(requests, "post")
    def test_request_success(self, mock_post):
        """request success"""
        response = requests.Response()
        response.status_code = 200
        mock_post.return_value = response
        self.remote.request(url="openeuler", method="post", max_retry=None)
        self.assertEqual(None, getattr(
            self.remote, "_request_error"))

    @mock.patch.object(requests, "post")
    def test_response_status_code(self, mock_post):
        """Content of response"""
        response = requests.Response()
        response.status_code = 200
        mock_post.return_value = response
        self.remote.request(url="openeuler", method="post", max_retry=None)
        self.assertEqual(200, self.remote.status_code)

    def test_response_content(self):
        """Content of response"""
        self.remote.request(method="post", url="openeuler")
        self.assertEqual(None, self.remote.text)
