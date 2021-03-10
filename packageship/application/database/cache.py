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
from copy import deepcopy
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
        kwargs = deepcopy(self._kwargs)
        kwargs["args"] = ",".join(self._args)

        ret_dict = {}

        def spear_kwargs(old_dict):
            """to spear kwargs
            if key is 'db_priority' and the value is list,
                do not sort list content,and merge to string
                because need to keep the order of the database.

            Other list cases need to be sorted first,then merge to string
            
            There is no strict order requirement for the remaining keys and values, 
                and can be directly converted to strings.
            
            Args:
                old_dict (dict): the input kwargs
               
                e.g:
                input kwargs:
                {'depend_type': 'installdep',
                'packagename': ['Judy','Judy1'],
                'parameter': {'db_priority': ['fedora30', 'openeuler'], 'level': 0}}
                    
                To:
                
                {'depend_type': 'installdep',
                'packagename': 'Judy,Judy1',  # be sorted first then merge to string
                'db_priority':'fedora30,openeuler'  # do not sorted, can merge to string
                'level':'0'
                }
            """
            for k, v in old_dict.items():
                if isinstance(v, dict):
                    spear_kwargs(v)
                else:
                    if k == "db_priority" and isinstance(v, list):
                        v = ",".join(v)
                    elif isinstance(v, list):
                        v = ",".join(sorted(v))
                    else:
                        v = str(v)
                    ret_dict.update({k: v})

        spear_kwargs(kwargs)
        kw_str = "key"

        for key, val in sorted(ret_dict.items(), key=lambda x: x[0]):
            kw_str += "," + key + ":" + val

        return hashlib.sha256(kw_str.encode("utf8")).hexdigest()

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
        constant.REDIS_CONN.hmset(
            key,
            dict(
                source_dict=json.dumps(self._depend.source_dict),
                binary_dict=json.dumps(self._depend.binary_dict),
                log_msg=self._depend.log_msg,
            ),
        )

    def _set_val(self, key):
        """
        Description: Gets the cached hash value and assigns it to
                     the corresponding dependent instance

        Args:
            key: cached key
        """
        # dpenends = constant.REDIS_CONN.hgetall(key)
        self._depend.source_dict = json.loads(
            constant.REDIS_CONN.hget(key, "source_dict")
        )
        self._depend.binary_dict = json.loads(
            constant.REDIS_CONN.hget(key, "binary_dict")
        )
        self._depend.log_msg = constant.REDIS_CONN.hget(key, "log_msg")

        if not self._depend.log_msg:
            return

        LOGGER.warning(self._depend.log_msg)

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
