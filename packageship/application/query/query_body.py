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

    # Query all data
    QUERY_ALL = {
        "query": {
            "match_all": {}
        }
    }

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
        self.__dict__.update(dict(_query_term={
            "query": {
                "bool": {
                    "filter": {
                        "term": {
                        }
                    }
                }
            }
        }))
        if isinstance(param, dict):
            self._query_term["query"]["bool"]["filter"]["term"] = param.get('name')
        if param.get('_source'):
            self._query_term['_source'] = param.get('_source')
