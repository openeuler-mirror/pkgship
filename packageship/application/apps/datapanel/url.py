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
    (view.ObsInfoList, '/infoBoard/obs', {'query': ('GET')}),
    (view.PkgSuggestView,
     '/infoBoard/obs/package/suggest', {'query': ('GET')}),
    (view.BranchSuggestView,
     '/infoBoard/obs/branch/suggest', {'query': ('GET')}),
    (view.ExportObsInfo, '/infoBoard/obs/export', {'query': ('POST')}),
    (view.SigInfoList, '/infoBoard/sig', {'query': ('GET')}),
    (view.ExportSiginfo, '/infoBoard/sig/export', {'query': ('POST')}),
    (view.PrInfoList, '/infoBoard/pr', {'query': ('POST')}),
]
