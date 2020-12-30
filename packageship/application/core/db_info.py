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


class TableColumn:

    def __init__(self):
        self._columns = None

    @classmethod
    def as_table(cls, table_name, **kwargs):
        """
`        :param table_name:table name
`        """
        pass

    @property
    def columns(self):
        return self._columns

    def query_columns(self, table_name):
        """
            :param table_name: table name
        """
        pass


class DataBase:

    def tables(self, database_name, exclude_table=None):
        """
            get tables name, exclude unneed name
            :param database_name:database name
            :param exclude_table:exclude table's name
        """
        pass

    def table_columns(self, database_name, table_name, **kwargs):
        """
            Gets the columns of a table in the database
            :param database_name: database name
            :param table_name: columns name
            :param kwargs exclude_columns: exclude columns name
        """
        pass

    def db_priority(self):
        """
            get default priority for searching database
        """
        pass
