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
"""Use redis to store dependent data"""
import time
import json
import random
import hashlib
import threading
from redis.exceptions import RedisError
from packageship.application.common import constant
from packageship.libs.log import LOGGER


class BufferCache:
    """
    Data in redis cache,check cache data in redis database

    Attributes:
        _depend: Instances that depend on the query
        _func: The method of being decorated
    """
    _lock = threading.Condition()
    _active_thread = dict()

    def __init__(self, depend):
        self._depend = depend
        self._func = None
        self._args = None
        self._kwargs = None

    def _hash_key(self):
        """
        Description: After sorting the values of the dictionary type
                     calculate the md5 encrypted hash value

        Args:
            encrypt_obj: Dictionaries that need to be computed by hash values
        """
        if not self._args and not self._kwargs:
            return None

        kwargs = {key: self._kwargs[key]
                  for key in sorted(self._kwargs)}
        kwargs["args"] = ",".join(self._args)

        hash_str = "".join(sorted(str(kwargs))).encode('utf-8')

        return hashlib.sha256(hash_str).hexdigest()

    def _set_cache(self, key):
        """
        Description: Set the cache value for Redis

        Args:
            key: cached key
        """
        self._lock.acquire()
        if key not in self._active_thread:
            self._active_thread[key] = threading.currentThread().ident
        self._lock.release()

        while threading.currentThread().ident != self._active_thread.get(key):
            if constant.REDIS_CONN.exists(key):
                self._set_val(key)
                if key in self._active_thread:
                    del self._active_thread[key]
                return
            time.sleep(round(random.random(), 3))

        self._func(*self._args, **self._kwargs)
        constant.REDIS_CONN.hmset(key, dict(source_dict=json.dumps(self._depend.source_dict),
                                            binary_dict=json.dumps(self._depend.binary_dict)))

    def _set_val(self, key):
        """
        Description: Gets the cached hash value and assigns it to
                     the corresponding dependent instance

        Args:
            key: cached key
        """
        dpenends = constant.REDIS_CONN.hgetall(key)
        self._depend.source_dict = json.loads(dpenends["source_dict"])
        self._depend.binary_dict = json.loads(dpenends["binary_dict"])

    def _cache(self):
        """
        Description: Gets the dependency value in the cache or executes
                     the method to get the dependency data

        """
        key = self._hash_key()
        if not key:
            return
        key = "pkgship_" + key

        try:
            if constant.REDIS_CONN.exists(key):
                self._set_val(key)
                return
            self._set_cache(key)

        except RedisError as error:
            LOGGER.warning(error)
            self._func(*self._args, **self._kwargs)

    def __call__(self, func):
        self._func = func

        def wrapper(*args, **kwargs):
            self._args, self._kwargs = args, kwargs
            self._cache()

        return wrapper


buffer_cache = BufferCache

__all__ = ["buffer_cache"]
