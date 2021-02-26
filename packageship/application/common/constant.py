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
from redis import Redis, ConnectionPool
from packageship.libs.conf import configuration

REDIS_CONN = Redis(connection_pool=ConnectionPool(
    host=configuration.REDIS_HOST,
    port=configuration.REDIS_PORT,
    max_connections=configuration.REDIS_MAX_CONNECTIONS,
    decode_responses=True))
# es page size max value
MAX_PAGE_SIZE = 10000

# default page num
DEFAULT_PAGE_NUM = 1

# maximum page number allowed
MAXIMUM_PAGE_SIZE = 200

# under line char
UNDERLINE = "-"

# binary database,used for query binary rpm
BINARY_DB_TYPE = "binary"

# source database,used for query source rpm
SOURCE_DB_TYPE = "source"

# index of default databases
DB_INFO_INDEX = "databaseinfo"
