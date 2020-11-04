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
Description: Interception before request
"""
from flask import request
from packageship import application
from packageship.application.apps.package.url import urls as package_urls
from packageship.application.apps.lifecycle.url import urls as lifecycle_urls
from packageship.application.apps.dependinfo.url import urls as dependinfo_urls


__all__ = ['identity_verification']

URLS = package_urls + lifecycle_urls + dependinfo_urls


def identity_verification():
    """
    Description: Requested authentication
    Args:
    Returns:
    Raises:
    """
    if request.url_rule:
        url_rule = request.url_rule.rule
        for _view, url, authentication in URLS:
            if url.lower() == url_rule.lower() and application.OPERATION in authentication.keys():
                if request.method not in authentication.get(application.OPERATION):
                    return False
                break
        return True

    return False
