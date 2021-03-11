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
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_ipaddr, get_remote_address

from packageship.application.common.constant import MAX_DAY_NUM
from packageship.application.common.constant import MAX_MINUTES_NUM
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

    default_limits = ["{day}/day;{minute}/minute".format(day=MAX_DAY_NUM,
                                                         minute=MAX_MINUTES_NUM)]
    Limiter(app, key_func=get_remote_address, default_limits=default_limits, )
    from packageship.application import apps
    # Register Blueprint
    for blue, api in apps.blue_point:
        api.init_app(app)
        app.register_blueprint(blue)
    return app
