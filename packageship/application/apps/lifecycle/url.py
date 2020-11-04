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
Life cycle of url giant whale collection
"""
from . import view

urls = [  # pylint: disable=invalid-name
    # Download package data or iSsue data
    (view.DownloadFile, '/lifeCycle/download/<file_type>', {'query': ('GET')}),
    # Get a collection of maintainers list
    (view.MaintainerView, '/lifeCycle/maintainer', {'query': ('GET')}),
    # Get the columns that need to be displayed by default in the package
    (view.TableColView, '/packages/tablecol', {'query': ('GET')}),
    # View all table names in the package-info database
    (view.LifeTables, '/lifeCycle/tables', {'query': ('GET')}),
    (view.IssueView, '/lifeCycle/issuetrace', {'query': ('GET')}),
    (view.IssueType, '/lifeCycle/issuetype', {'query': ('GET')}),
    (view.IssueStatus, '/lifeCycle/issuestatus', {'query': ('GET')}),
    (view.IssueCatch, '/lifeCycle/issuecatch', {'write': ('POST')}),
# update a package info
    (view.UpdatePackages, '/lifeCycle/updatePkgInfo', {'write': ('PUT')})
]
