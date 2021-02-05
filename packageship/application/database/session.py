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
Parse config file, create database engines, obtains a specify database connection
"""
from packageship.application.common.exc import DatabaseConfigException
from packageship.application.database import engine
from packageship.libs.conf import configuration


class DatabaseSession(object):
    """
    Dynamic initialization of the database instance
    Raises: DatabaseConfigException, database is not support
    """
    __DATABASE_ENGINE_TYPE = ['elastic', 'mysql']

    def __init__(self, db_engine=None, host=None, port=None):
        self.db_engine = db_engine or configuration.DATABASE_ENGINE_TYPE
        if self.db_engine not in self.__DATABASE_ENGINE_TYPE:
            raise DatabaseConfigException("DataBase %s is not support" % self.db_engine)
        self._host = host or configuration.DATABASE_HOST
        self._port = port or configuration.DATABASE_PORT
        self.session = None

    def connection(self):
        """
        Returns: specify database connection
        Raises: DatabaseConfigException, database class not found
        """
        self.session = engine.create_engine(db_engine=self.db_engine, host=self._host, port=self._port)
        if self.session is None:
            raise DatabaseConfigException(
                "Failed to create database engine %s, please check database configuration" % self.db_engine)

        return self.session

    @property
    def client(self):
        """
        Get database client
        Returns: database client
        """
        if self.session is None:
            self.session = self.connection()

        return self.session.client
