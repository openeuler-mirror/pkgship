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
Provide Elasticsearch database instance initialization and operation
"""
import json

from elasticsearch import Elasticsearch, AsyncElasticsearch
from elasticsearch import helpers
from elasticsearch.exceptions import ElasticsearchException, TransportError
from urllib3.exceptions import LocationValueError

from packageship.application.common.constant import MAX_ES_QUERY_NUM
from packageship.application.common.exc import (
    DatabaseConfigException,
    ElasticSearchQueryException,
    ElasticSearchInsertException,
)
from packageship.application.common.singleton import singleton
from packageship.libs.log import LOGGER


@singleton
class ElasticSearch(object):
    """
    Elasticsearch,Use singleton pattern
    """

    def __init__(self, host=None, port=None):
        self._host = host
        self._port = port
        try:
            self.client = Elasticsearch(
                [{"host": self._host, "port": self._port}], timeout=60
            )
            self.async_client = AsyncElasticsearch(
                [{"host": self._host, "port": self._port}],
                timeout=600,
                max_retries=3,
                retry_on_timeout=True,
            )
        except LocationValueError:
            LOGGER.error("The host of database in package.ini is empty")
            raise DatabaseConfigException()

    def query(self, index, body):
        """
        Elasticsearch query function
        Args:
            index: index of elasticsearch
            body: query body of elasticsearch

        Returns: elasticsearch data
        Raises: ElasticSearchQueryException,including connection timeout, server unreachable, index does not exist, etc.
        """
        try:
            result = self.client.search(index=index, body=body)
            return result
        except ElasticsearchException as elastic_err:
            LOGGER.error(str(elastic_err))
            raise ElasticSearchQueryException(index=index)

    def scan(self, index, body):
        """
        Elasticsearch scan function, obtain all data
        Args:
            index: index of elasticsearch
            body: query body of elasticsearch

        Returns: elasticsearch all data
        Raises: ElasticSearchQueryException,including connection timeout, server unreachable, index does not exist, etc.
        """
        try:
            result = helpers.scan(
                client=self.client, index=index, query=body, scroll="3m", timeout="1m"
            )
            result_list = [res for res in result]
            return result_list
        except ElasticsearchException as elastic_err:
            LOGGER.error(str(elastic_err))
            raise ElasticSearchQueryException()

    def count(self, index, body):
        """
        Obtain data volume of specify index
        Args:
            index: index of elasticsearch
            body: query body of elasticsearch

        Returns: data volume
        Raises: ElasticSearchQueryException,including connection timeout, server unreachable, index does not exist, etc.
        """
        try:
            data_count = self.client.count(index=index, body=body)
            return data_count
        except ElasticsearchException as elastic_err:
            LOGGER.error(str(elastic_err))
            raise ElasticSearchQueryException()

    @staticmethod
    def _load_mappings(mappings_file):
        try:
            with open(mappings_file, "r") as file:
                mappings = json.load(file)
        except IOError:
            mappings = None
        return mappings

    def insert(self, index, body, doc_type="_doc"):
        """
        Single insert ES data
        Args:
            index: Index to ES database
            body: inserted data set
            doc_type: document type

        Returns:
        Raises: ElasticSearchQueryException,including connection timeout, server unreachable, index does not exist, etc.
        """
        try:
            self.client.index(index=index, body=body, doc_type=doc_type)
        except ElasticsearchException as elastic_err:
            LOGGER.error(str(elastic_err))
            raise ElasticSearchInsertException()

    def create_index(self, indexs):
        """
        Create a database index for ES
        Args:
            indexs: name of the index and the mapping relationship of the index
                      {
                        "file": "mapings.json",
                        "name": "index name"
                      }
        Returns: index of create failed
        """
        fails = []

        def _create(mapping, index_name):
            mappings = self._load_mappings(mapping)
            if not mappings:
                fails.append(index_name)
                return
            try:
                # Because the data needs to be updated, the existing index must be deleted
                if self.client.indices.exists(index_name):
                    fail_index = self.delete_index(index_name)
                    if fail_index:
                        fails.append(fail_index)
                        return
                self.client.indices.create(index=index_name, body=mappings)
            except ElasticsearchException:
                fails.append(index_name)

        if isinstance(indexs, (list, tuple)):
            for index in indexs:
                _create(index["file"], index["name"])
        else:
            _create(indexs["file"], indexs["name"])
        return fails

    def delete_index(self, index):
        """
        Delete the ES index
        Args:
            index: index name

        Returns: Delete the failed database sets
        """
        fails = None
        if not index:
            return fails
        if isinstance(index, (tuple, list)):
            index = ",".join(index)
        try:
            self.client.indices.delete(index)
        except TransportError:
            fails = index
        return fails

    def update_setting(self):
        """
        Update the ES configuration, currently the maximum number of modified queries
        :return: None
        """
        try:
            self.client.indices.put_settings(
                index="_all", body={"index": {"max_result_window": MAX_ES_QUERY_NUM}}
            )
        except ElasticsearchException:
            LOGGER.error("Set max_result_window of all indies failed")

    async def async_insert(self, index, body):
        """
        Insert a single piece of data asynchronously
        :param index: es index
        :param body: insert data
        :return: insert response
        """
        try:
            await self.async_client.index(index=index, body=body)
        except ElasticsearchException as elastic_err:
            LOGGER.error(
                "Insert to %s failed,data is %s, message is %s"
                % (index, body, elastic_err)
            )

    async def async_bulk(self, body: list):
        """
        Asynchronous batch insert method
        :param body: insert content
        :return: None
        :exception: ElasticSearchInsertException
        """
        try:
            _, filed_count = await helpers.async_bulk(self.async_client, body)
            if filed_count:
                LOGGER.warning(f"The bulk insert part fails: {filed_count}")
        except ElasticsearchException as elastic_err:
            LOGGER.error(f"The bulk insert failed: {elastic_err}")
            raise ElasticSearchInsertException()

    @staticmethod
    def es_insert_struct(index, source, _type="_doc"):
        """
        Description: A JSON document for the ES database

        """
        return {
            "_index": index,
            "_type": _type,
            "_source": source,
        }

    def delete(self, index, body):
        """Delete the data that meets the requirements
        :param index: es index
        :param body: Query conditions
        """
        try:
            self.client.delete_by_query(index=index, body=body)
        except ElasticsearchException as elastic_err:
            LOGGER.error(
                "Delete to %s failed,query is %s,message is %s"
                % (index, body, elastic_err)
            )

    def reindex(self, old_index, new_index):
        try:
            body = {"source": {"index": old_index}, "dest": {"index": new_index}}
            self.client.reindex(body)
        except ElasticsearchException as elastic_err:
            LOGGER.error(
                "Reindex to %s failed, error is %s." % (old_index, elastic_err)
            )
            raise ElasticSearchInsertException()
