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
Query body frame
"""


class QueryBody(object):
    """
    Query body structure
    """

    def __init__(self):
        self._query_term = dict()
        self._query_terms = dict()
        self._query_filters = dict()
        self._fuzzy_query = dict()
        self._must_match = dict()

    # Query all data
    QUERY_ALL = {"query": {"match_all": {}}}
    # Paging query all data
    PAGING_QUERY_ALL = {"query": {"match_all": {}}, "from": 0, "size": 20}
    # Query all data no auto paging
    QUERY_ALL_NO_PAGING = {"query": {"match_all": {}}, "from": 0, "size": 1000}

    @property
    def query_terms(self):
        """
        Filter queries for multiple individual data
        Returns: query body

        """
        return self._query_terms

    @query_terms.setter
    def query_terms(self, param):
        """
        The setter of query_terms
        Args:
            param: query content

        Returns: query body

        """
        self.__dict__.update(
            dict(_query_terms={"query": {"bool": {"filter": {"terms": {}}}}})
        )
        self._query_terms["query"]["bool"]["filter"]["terms"] = param.get("fields")
        self._set_other_field(self._query_terms, param)

    @property
    def query_term(self):
        """Filter queries for individual data"""
        return self._query_term

    @query_term.setter
    def query_term(self, param):
        """
        Term query body
        Args:
            param: query content

        Returns: query body

        """
        self.__dict__.update(
            dict(_query_term={"query": {"bool": {"filter": {"term": {}}}}})
        )
        self._query_term["query"]["bool"]["filter"]["term"] = param.get("fields")
        self._set_other_field(self._query_term, param)

    @property
    def query_and_filters(self):
        """
        Range query statement
        :return: query body
        """
        return self._query_filters

    @query_and_filters.setter
    def query_and_filters(self, param):
        """
        Condition combination query
        :param param: query content exp:{"build_state":{"gte":10,"lte":100}}
        :return: query body
        """
        self.__dict__.update(
            dict(_query_filters={"query": {"bool": {"filter": {"bool": {"must": []}}}}})
        )
        self._query_filters["query"]["bool"]["filter"]["bool"]["must"] = param.get(
            "fields", []
        )
        self._set_other_field(self._query_filters, param)

    @property
    def fuzzy_query(self):
        """
        Fuzzy query
        :return: query body
        """
        return self._fuzzy_query

    @fuzzy_query.setter
    def fuzzy_query(self, params):
        """
        Condition fuzzy query
        :param params: input params
        :return: query body
        """
        self.__dict__.update(dict(_fuzzy_query={"query": {"wildcard": {}}}))
        self._fuzzy_query["query"]["wildcard"] = params.get("fields", {})
        self._set_other_field(self._fuzzy_query, params)

    @property
    def must_match(self):
        """Multi condition query"""
        return self._must_match

    @must_match.setter
    def must_match(self, param):
        self.__dict__.update(dict(_must_match={"query": {"bool": {"must": []}}}))
        self._must_match["query"]["bool"]["must"] = [
            {"match": {key + ".keyword": val}} for key, val in param.items()
        ]

    @staticmethod
    def _set_other_field(query_body, param):
        """
        Set other fields of the query statement
        :param query_body: Query body to be filled
        :param param: filter params
        :return: query body
        """
        if param.get("_source"):
            query_body["_source"] = param.get("_source")
        if isinstance(param.get("page_num"), int) and isinstance(
            param.get("page_size"), int
        ):
            query_body["from"] = param.get("page_num")
            query_body["size"] = param.get("page_size")
        if param.get("query_size"):
            query_body["size"] = param.get("query_size")
