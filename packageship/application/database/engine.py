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
Get the corresponding database class through the database type string
"""
import importlib

from packageship.libs.log import LOGGER


def create_engine(db_engine, **kwargs):
    """
    Get database class by engines name
    """
    try:
        module = importlib.import_module("packageship.application.database.engines.%s" % db_engine)
    except ModuleNotFoundError:
        # Log here, the caller throws an exception
        LOGGER.error("DataBase engine module not exist")
        return None
    cls = getattr(module, db_engine)
    return cls(**kwargs)
