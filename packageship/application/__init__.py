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
   Initial operation and configuration of the flask project
"""
import os
from flask import Flask, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_ipaddr, get_remote_address
from packageship.application.settings import Config
from packageship.libs.log import Log

LIMITER = Limiter(key_func=get_ipaddr)


def init_app(permissions):
    """
        Project initialization function
    """
    app = Flask(__name__)

    os.environ["PERMISSIONS"] = permissions

    # log configuration
    app.logger.addHandler(Log(__name__).file_handler)

    # Load configuration items
    app.config.from_object(Config())
    app.config.from_object(Config())
    DEFAULT_LIMITS = ["500/day;20/minute"]
    app.app_context().push()
    limiter = Limiter(app, key_func=get_remote_address, default_limits=DEFAULT_LIMITS, )
    current_app.my_limiter = limiter
    from packageship.application import apps
    # Register Blueprint
    for blue, api in apps.blue_point:
        api.init_app(app)
        app.register_blueprint(blue)
    return app
