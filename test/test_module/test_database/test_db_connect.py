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
from unittest import TestCase, mock

from packageship.application.common.exc import DatabaseConfigException
from packageship.application.database.engines.elastic import ElasticSearch
from packageship.application.database.session import DatabaseSession


class TestConnect(TestCase):
    def test_get_connection(self):
        """
        Test get a Es connection
        Returns:

        """
        db = DatabaseSession()
        db_session = db.connection()

        es_session = ElasticSearch(host=db._host, port=db._port)

        self.assertIs(db_session, es_session)

    def test_database_not_support(self):
        """
        Test query a not exist database
        Returns:

        """
        with self.assertRaises(DatabaseConfigException):
            DatabaseSession(db_engine="test")

    def test_get_engine_failed(self):
        """
        Test create a engine fail
        Returns:

        """
        with self.assertRaises(DatabaseConfigException):
            DatabaseSession(db_engine='mysql')

    @mock.patch.object(DatabaseSession, "connection")
    def test_get_client(self, mock_connection):
        """
        Test get a es client
        Args:
            mock_connection: mock es instance
        Returns:

        """
        es_instance = ElasticSearch(host="127.0.0.1", port="9200")
        mock_connection.return_value = es_instance

        db = DatabaseSession()
        self.assertIs(db.client, es_instance.client)
