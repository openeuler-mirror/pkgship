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
Singleton pattern decorator
"""
import inspect
from functools import wraps


def singleton(cls):
    """
    Singleton pattern decorator
    Use for create database instance
    Args:
        cls: class name

    Returns: class instance
    """
    __instance = {}

    @wraps(cls)
    def __single(*args, **kwargs):
        __key = [cls.__name__]
        __sig = inspect.signature(cls.__init__)

        for key, value in __sig.parameters.items():
            if key in kwargs:
                __key.append(kwargs[key])
            else:
                __key.append(value.default)
        __instance_key = str(__key)

        if __instance_key not in __instance:
            __instance[__instance_key] = cls(*args, **kwargs)
        return __instance[__instance_key]

    return __single
