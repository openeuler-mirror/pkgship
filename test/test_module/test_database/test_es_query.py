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

from elasticsearch import Elasticsearch, helpers

from packageship.application.database.engines.elastic import ElasticSearch


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
        result = es.query(index='test', body='test')

        expect_value = dict()
        self.assertEqual(result, expect_value)

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
        result = es.scan(index='test', body={"query": {"match_all": {}}})

        expect_value = []
        self.assertEqual(result, expect_value)

    @staticmethod
    def _es_init():
        return ElasticSearch(host="127.0.0.1", port="9200", user_name=None, password=None)
