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
from .be_depend import BeDepend
from .build_depend import BuildDepend
from .install_depend import InstallDepend
from .self_depend import SelfDepend


class DispatchDepend:
    """
        Factory method, distributing operations of different depend search
    """

    def __init__(self):
        self._kwargs = dict()

    def _selfdep(self):

        _self_depend = SelfDepend(
            db_list=self._kwargs["parameter"]["db_priority"])
        _self_depend(**self._kwargs)
        return _self_depend

    def _installdep(self):
        _install_depend = InstallDepend(
            db_list=self._kwargs["parameter"]["db_priority"])
        _install_depend(**self._kwargs)
        return _install_depend

    def _builddep(self):
        _build_depend = BuildDepend(
            db_list=self._kwargs["parameter"]["db_priority"])
        _build_depend(**self._kwargs)
        return _build_depend

    def _bedep(self):
        _be_depend = BeDepend(**self._kwargs)
        _be_depend(**self._kwargs)
        return _be_depend

    @classmethod
    def execute(cls, **kwargs):
        """Execute the map to return the dependent instance
        """
        
        def dispatch():
            depend_type = kwargs["depend_type"]
            method = getattr(dispatch_cls, "_" + depend_type, None)
            if not method:
                raise AttributeError(
                    "Queries that do not support dependencies are not supported")

            return method()
        if "depend_type" not in kwargs:
            raise ValueError(
                "Missing the necessary query parameter 'depend_type' .")
        dispatch_cls = cls()

        setattr(dispatch_cls, "_kwargs", kwargs)

        return dispatch()
