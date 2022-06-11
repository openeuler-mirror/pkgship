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
import os

try:
    from packageship_panel.application import init_app

    if not os.path.exists(os.environ.get("SETTINGS_FILE_PATH")):
        raise RuntimeError(
            "System configuration file:%s" % os.environ.get("SETTINGS_FILE_PATH"),
            "does not exist, software service cannot be started",
        )

    app = init_app("query")
except ImportError as error:
    raise RuntimeError(
        "The package management software service failed to start : %s" % error
    ) from error
else:
    from packageship_panel.application.appglobal import permissions
    from packageship.libs.conf import configuration


@app.before_request
def before_request():
    """
    Description: Global request interception
    """
    if not permissions():
        return "No right to perform operation"
