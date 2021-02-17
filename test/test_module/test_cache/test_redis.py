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
from redis import Redis
from redis.exceptions import RedisError
import threading
from packageship.application.database import cache
from packageship.application.initialize.integration import ESJson


class TestBufferCache(unittest.TestCase):
    """buffer cache test"""

    def setUp(self):
        self.cache = cache.BufferCache(
            depend=ESJson(source_dict="", binary_dict=""))(func=self._func)

    def _func(self):
        return None

    def test_key_none(self):
        """The cached key value does not exist"""
        self.assertEqual(None, self.cache())

    @mock.patch.object(Redis, "delete")
    @mock.patch.object(Redis, "hgetall")
    @mock.patch.object(Redis, "exists")
    def test_exists_key(self, mock_exists, mock_hgetall, mock_delete):
        """A cached key value exists"""
        mock_exists.return_value = True
        mock_hgetall.return_value = dict(
            source_dict=str(dict()), binary_dict=str(dict()))
        mock_delete.return_value = None
        self.assertEqual(None, self.cache(pkgname="openeuler"))

    @mock.patch.object(Redis, "delete")
    @mock.patch.object(Redis, "hmset")
    @mock.patch.object(Redis, "expire")
    @mock.patch.object(Redis, "set")
    @mock.patch.object(Redis, "exists")
    def test_set_cache(self, mock_exists, mock_set, mock_expire, mock_hmset, mock_delete):
        """Set the cache value"""
        mock_exists.side_effect = [
            False,
            False,
            True,
            False
        ]
        mock_set.return_value = None
        mock_expire.return_value = None
        mock_hmset.return_value = None
        mock_delete.return_value = None
        self.assertEqual(None, self.cache(pkgname="openeuler"))

    @mock.patch.object(Redis, "hgetall")
    @mock.patch.object(Redis, "exists")
    def test_sleep_cache(self, mock_exists, mock_hgetall):
        """Wait for the cache Settings"""
        mock_exists.side_effect = [
            False,
            True
        ]
        with mock.patch("threading.currentThread().ident",
                        new_callable=mock.PropertyMock) as mock_ident:
            mock_ident.side_effect = [
                "1",
                "2"
            ]
            mock_hgetall.return_value = dict(
                source_dict=str(dict()), binary_dict=str(dict()))
            self.assertEqual(None, self.cache(pkgname="openeuler"))

    @mock.patch.object(Redis, "exists")
    def test_redis_exception(self, mock_exists):
        mock_exists.side_effect = RedisError()
        self.assertEqual(None, self.cache(pkgname="openeuler"))
