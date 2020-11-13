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
Description: url set
"""
from . import view

urls = [
    # Get all packages' info
    (view.Packages, '/packages', {'query': ('GET')}),


    # Query and update a package info
    (view.SinglePack, '/packages/packageInfo',
     {'query': ('GET'), 'write': ('PUT')}),

    # Query a package's install depend(support querying in one or more databases)
    (view.InstallDepend, '/packages/findInstallDepend', {'query': ('POST')}),

    # Query a package's build depend(support querying in one or more databases)

    (view.BuildDepend, '/packages/findBuildDepend', {'query': ('POST')}),

    # Query a package's all dependencies including install and build depend
    # (support quering a binary or source package in one or more databases)
    (view.SelfDepend, '/packages/findSelfDepend', {'query': ('POST')}),

    # Query a package's all be dependencies including be installed and built depend
    (view.BeDepend, '/packages/findBeDepend', {'query': ('POST')}),

    # Get all imported databases, import new databases and update existed databases

    (view.Repodatas, '/repodatas', {'query': ('GET'), 'write': ('DELETE')}),

    # Reload database
    (view.InitSystem, '/initsystem', {'write': ('POST')}),

    # Get filelist Info
    (view.GetFilelistInfo, '/packages/packageInfo/file', {'query': ('GET')})
]
