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

from . import view

urls = [
    # get SelfDepend
    (view.SelfDependInfo, '/dependInfo/selfDepend', {'query': ('POST')}),
    # get BeDepend
    (view.BeDependInfo, '/dependInfo/beDepend', {'query': ('POST')}),
    # get all database name
    (view.DataBaseInfo, '/dependInfo/databases', {'query': ('GET')}),

    # Download install or build or self or bedepend excel
    (view.Downloadzip, '/dependInfo/download/<file_type>', {'query': ('POST')}),
    # get InstallDepend
    (view.InstallDependInfo, '/dependInfo/installDepend', {'query': ('POST')}),
    # get BuildDepend
    (view.BuildDependInfo, '/dependInfo/buildDepend', {'query': ('POST')}),
    # get SingleGraph
    (view.SingleGraph, '/dependInfo/result/singleGraph', {'query': ('POST')}),
]
