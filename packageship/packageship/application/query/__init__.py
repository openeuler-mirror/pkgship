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
import time

from packageship.application.common.constant import DB_INFO_INDEX, SOURCE_DB_TYPE, BINARY_DB_TYPE, BE_DEPEND_TYPE
from packageship.application.database.session import DatabaseSession
from packageship.application.query.query_body import QueryBody


class Query(object):
    """
        common function used for query depend
    """
    session = DatabaseSession().connection()

    def __init__(self):
        self._index = ""

    @property
    def db_info(self):
        """database priority index"""
        return DB_INFO_INDEX

    @property
    def source_index(self):
        """source package index"""
        return self._index + '-' + SOURCE_DB_TYPE

    @property
    def binary_index(self):
        """binary package index"""
        return self._index + "-" + BINARY_DB_TYPE

    @property
    def bedepend_index(self):
        """bedepend index"""
        return self._index + "-" + BE_DEPEND_TYPE

    def set_index(self, index):
        """Sets the ES index to be queried"""
        self._index = index

    @staticmethod
    def search_result_format(search_result):
        """
        Parse the result of an ES query
        :param search_result: old result of an ES query
        :return: source data
        """
        if search_result is None:
            return []
        try:
            format_result = search_result['hits']['hits']
            return format_result
        except KeyError:
            return []

    @staticmethod
    def count_result_format(count_result):
        """
        Parse the data of the number of es queries
        :param count_result: query result
        :return: count
        """
        if count_result is None:
            return 0
        try:
            count = count_result['count']
            return count
        except KeyError:
            return 0
