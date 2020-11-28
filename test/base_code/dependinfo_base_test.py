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
# -*- coding:utf-8 -*-
"""
DependInfo view test
"""
import os
from test.base_code.read_data_base import ReadTestBase
from redis import Redis, ConnectionPool
from packageship.libs.conf import configuration


os.system("redis-server &")
os.system("redis-cli")
os.system("config set stop-writes-on-bgsave-error no")
os.system("exit")


class DependInfo(ReadTestBase):
    """
    DependInfo view test
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        setUpClass
        Returns:

        """
        redis_conn = Redis(connection_pool=ConnectionPool(
            host=configuration.REDIS_HOST,
            port=configuration.REDIS_PORT,
            max_connections=configuration.REDIS_MAX_CONNECTIONS,
            decode_responses=True))
        redis_conn.info()
