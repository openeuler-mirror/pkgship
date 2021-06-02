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
get database list according to priority
"""
from elasticsearch import NotFoundError
from packageship.application.common.constant import DB_INFO_INDEX
from packageship.application.common.exc import DatabaseConfigException, ElasticSearchQueryException
from packageship.application.database.session import DatabaseSession
from packageship.application.query.query_body import QueryBody
from packageship.libs.log import LOGGER

db_client = DatabaseSession().connection()


def get_db_priority():
    """
    get database list according to priority
    Returns:
        database_list
    """
    db_infos = {}
    try:
        result = db_client.query(index=DB_INFO_INDEX, body=QueryBody.QUERY_ALL_NO_PAGING)
        for _db in result["hits"]["hits"]:
            db_info = _db.get("_source")
            db_infos[db_info.get("database_name")] = db_info.get("priority")
        db_order = sorted(db_infos.items(), key=lambda x: (x[1], x[0]))
        database_list = [key for key, value in db_order]
        return database_list
    except (NotFoundError, KeyError, ConnectionRefusedError,
            DatabaseConfigException, ElasticSearchQueryException):
        LOGGER.warn("Error in getting db priority info.")
        return []
