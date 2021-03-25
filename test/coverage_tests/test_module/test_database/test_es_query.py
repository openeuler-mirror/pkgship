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
import os
from unittest import TestCase, mock
from unittest.mock import MagicMock

from elasticsearch import Elasticsearch, helpers
from elasticsearch.client.indices import IndicesClient
from elasticsearch.exceptions import ElasticsearchException, TransportError

from packageship.application.common.exc import ElasticSearchQueryException, DatabaseConfigException
from packageship.application.database.engines.elastic import ElasticSearch

MOCK_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/mapping.json")


class TestEsQuery(TestCase):

    @mock.patch.object(Elasticsearch, "search")
    def test_normal_es_search(self, mock_search):
        """
        Test elasticsearch search operation
        Args:
            mock_search: mock elasticsearch search operation
        Returns:
        """
        data = {"hits": {"hits": {}}}
        mock_search.return_value = data

        es = self._es_init()
        result = es.query(index='test', body="test")

        self.assertEqual(result, data)

    def test_search_failed(self):
        """
        Test elasticsearch search failed
        Returns:
        """
        es = self._es_init()

        with self.assertRaises(ElasticSearchQueryException):
            es.query(index='test', body='test')

    @mock.patch.object(helpers, "scan")
    def test_normal_es_scan(self, mock_scan):
        """
        Test elasticsearch scan operation
        Args:
            mock_scan: mock elasticsearch scan operation
        Returns:
        """
        data = [{"hits": {"hits": {}}}]
        mock_scan.return_value = data

        es = self._es_init()
        result = es.scan(index='test', body="test")

        self.assertEqual(result, data)

    def test_scan_failed(self):
        """
        Test elasticsearch scan failed
        Returns:
        """
        es = self._es_init()

        with self.assertRaises(ElasticSearchQueryException):
            es.scan(index='test', body={"query": {"match_all": {}}})

    def test_no_host(self):
        """
        Test config elasticsearch's host is empty
        Returns:
        """
        with self.assertRaises(DatabaseConfigException):
            ElasticSearch(host="", port="9200")

    @mock.patch.object(Elasticsearch, "count")
    def test_get_count(self, mock_count):
        """
        Test obtain data volume
        Returns:
        """
        es = self._es_init()
        mock_count.return_value = 5

        result = es.count(index="test", body="test")
        self.assertEqual(result, 5)

    def test_get_count_fail(self):
        """
        Test obtain data volume failed
        Returns:
        """
        es = self._es_init()

        with self.assertRaises(ElasticSearchQueryException):
            es.count(index='test', body={"query": {"match_all": {}}})

    def test_single_instance(self):
        """
        Test signal instance of database class
        Returns:

        """
        es1 = ElasticSearch(host="127.0.0.1", port=None)
        es2 = ElasticSearch(host="127.0.0.1")
        self.assertIs(es1, es2)

    def test_create_index_success(self):
        """
        Test create indices success
        Returns:
        """
        IndicesClient.exists = MagicMock(side_effect=[False, False])
        IndicesClient.create = MagicMock(side_effect=[True, True])

        es_instance = self._es_init()
        indices = [dict(file=MOCK_DATA_FILE, name="test1"), dict(file=MOCK_DATA_FILE, name="test2")]
        result = es_instance.create_index(indices)
        self.assertEqual(result, [])

    def test_create_index_fail(self):
        """
        Test create indices failed
        Returns:
        """
        IndicesClient.exists = MagicMock(side_effect=[False])
        IndicesClient.create = MagicMock(side_effect=[ElasticsearchException])

        es_instance = self._es_init()
        indices = [dict(file=MOCK_DATA_FILE, name="test1")]
        result = es_instance.create_index(indices)
        self.assertEqual(result, ["test1"])

    def test_delete_index_fail(self):
        """
        Test delete indices success
        Returns:
        """
        IndicesClient.exists = MagicMock(side_effect=[True])
        IndicesClient.delete = MagicMock(side_effect=[TransportError])

        es_instance = self._es_init()
        indices = [dict(file=MOCK_DATA_FILE, name="test1")]
        result = es_instance.create_index(indices)
        self.assertEqual(result, ["test1"])

    def test_load_mapping_fail(self):
        """
        Test load mapping success
        Returns:
        """
        es_instance = self._es_init()
        indices = dict(file=MOCK_DATA_FILE + "1", name="test1")
        result = es_instance.create_index(indices)
        self.assertEqual(result, ["test1"])

    def test_insert_fail(self):
        """
        Test insert indices success
        Returns:
        """
        es_instance = self._es_init()
        with self.assertRaises(ElasticSearchQueryException):
            es_instance.insert(index="test", body={})

    def test_delete_index_none(self):
        """
        Test delete indices is none
        Returns:
        """
        es_instance = self._es_init()
        result = es_instance.delete_index(index="")
        self.assertIsNone(result)

    def test_delete_many_indices_fail(self):
        """
        Test delete indices failed
        Returns:
        """
        IndicesClient.delete = MagicMock(side_effect=[TransportError])

        es_instance = self._es_init()
        indices = ['test1', 'test2']
        result = es_instance.delete_index(indices)
        self.assertEqual(result, "test1,test2")

    @staticmethod
    def _es_init():
        return ElasticSearch(host="127.0.0.1", port="9200")
