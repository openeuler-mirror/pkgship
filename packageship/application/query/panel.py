#!/usr/bin/python3
# ******************************************************************************
# Copyright (c) Huawei Technologies Co., Ltd. 2021-2021. All rights reserved.
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
Panel information database query class
"""

from packageship.application.common.constant import BUILD_STATES, BUILD_TIMES, BUILD_TIME_LEVEL
from packageship.application.query import Query, QueryBody
from packageship.libs.log import LOGGER

# Query the iso information of the past 11 days by default
DEFAULT_ISO_QUERY_DAYS = 11


class PanelInfo(Query):
    """
    Panel information database query class
    """

    def __init__(self):
        super(PanelInfo, self).__init__()
        self.query_body = QueryBody()

    def query_obs_info(self, body, index="obs_info", source=None, page_index=0, page_size=0):
        """
        Query obs page information
        :param index: elasticsearch index
        :param body: query keywords exp:{"repo_name":"gcc","gitee_branch":"openEuler-22.03-LTS"}
        :param source: Query result filter field exp:["repo_name", "gitee_branch"]
        :param page_index: Pagination query page number exp:1
        :param page_size: Paging query the size of each page exp:50
        :return: query result
        """
        format_query_body = {"fields": self._construct_term_query_body(body, keyword=True),
                             "_source": None,
                             "page_num": None,
                             "page_size": None}
        if isinstance(source, list):
            format_query_body['_source'] = source

        page_from = (page_index - 1) * page_size
        if all([isinstance(page_from, int), isinstance(page_size, int)]) and \
                all([page_from >= 0, page_size > 0]):
            format_query_body['page_num'] = page_from
            format_query_body['page_size'] = page_size

        self.query_body.query_and_filters = format_query_body
        query_result_list = self._query_data(index=index, body=self.query_body.query_and_filters)

        return [query_result.get('_source') for query_result in query_result_list]

    def query_build_states(self, branch, index="obs_info"):
        """
        Count the number of states of each component of the software package
        :param branch: gitee branch exp:openEuler-22.03-LTS
        :param index: es index
        :return: Number of packages in each state
        """
        state_count = dict()
        body = {"gitee_branch": branch, "build_state": None}
        for state in BUILD_STATES:
            body['build_state'] = state
            self.query_body.query_and_filters = \
                {"fields": self._construct_term_query_body(body, keyword=True)}
            current_state_count = \
                self._query_count(index=index, body=self.query_body.query_and_filters)
            state_count[state] = current_state_count

        return state_count

    def query_build_times(self, branch, index="obs_info"):
        """
        Query the number of packages for each level of build time
        :param branch: gitee branch exp:openEuler-22.03-LTS
        :param index: es index
        :return: number of packages for each level of build time
        """
        each_time_count = dict()
        term_dict = {"term": {"gitee_branch.keyword": branch}}
        times_lens = len(BUILD_TIMES)
        for i in range(times_lens):
            if i < times_lens - 1:
                range_dict = {"range": {"build_time": \
                    {"gt": BUILD_TIMES[i], "lte": BUILD_TIMES[i + 1]}}}
            else:
                range_dict = {"range": {"build_time": {"gt": BUILD_TIMES[i]}}}

            combination_dict = {"fields": [term_dict, range_dict]}
            self.query_body.query_and_filters = combination_dict
            current_level_count = self._query_count(
                index=index,
                body=self.query_body.query_and_filters
                )
            each_time_count[BUILD_TIME_LEVEL[i]] = current_level_count

        return each_time_count

    def query_iso_info(self, branch, index="iso_info", recent_days=DEFAULT_ISO_QUERY_DAYS):
        """
        Query iso build information
        :param branch: gitee branch exp:openEuler-22.03-LTS
        :param index: es index
        :param recent_days: Specify to query the information of the past n days exp:10
        :return: iso info list
        """
        term_dict = {"term": {"branch.keyword": branch}}
        range_dict = {"range": {"date": {"gte": f"now-{recent_days}d"}}}
        combination_dict = {"fields": [term_dict, range_dict]}
        self.query_body.query_and_filters = combination_dict

        query_result_list = self._query_data(index=index, body=self.query_body.query_and_filters)
        return [query_result.get('_source') for query_result in query_result_list]

    def query_sig_info(self, sig_name, index="sig_info"):
        """
        Querying sig group information
        :param sig_name: sig name exp:application
        :param index: es index
        :return: sig info
        """
        if not sig_name:
            query_result = self._query_data(index=index, body=self.query_body.QUERY_ALL)
        else:
            self.query_body.query_term = {"name": {"name.keyword": sig_name}}
            query_result = self._query_data(index=index, body=self.query_body.query_term)

        return [sig_info.get('_source') for sig_info in query_result]

    def query_suggest_info(self, index, body, query_all=False, source=None):
        """
        Suggested information query, the query mode is fuzzy query
        :param index: es index
        :param body: query body,Only one filter is supported.
                     etc：{"gitee_branch":"openEuler-20.03-LTS-SP1"}
        :param query_all: Whether to query all
        :param source: filter fields
        :return: query result
        """
        query_body = dict()
        if query_all:
            query_body = self.query_body.QUERY_ALL
            query_body['_source'] = source if isinstance(source, list) else []
            query_result = self._query_data(index=index, body=query_body)
        else:
            for key, value in body.items():
                query_body['fields'] = {f'{key}.keyword': f'*{value}*'}
                break

            query_body['_source'] = source if isinstance(source, list) else []
            self.query_body.fuzzy_query = query_body
            query_result = self._query_data(index=index, body=self.query_body.fuzzy_query)

        return [branch_info.get('_source') for branch_info in query_result]

    def _query_data(self, index, body):
        """
        Data query entry
        :param index: elasticsearch index
        :param body: query keywords
        :return: query result
        """
        if not index or not isinstance(body, dict):
            LOGGER.error('index: %s or query_body: %s unavailable', index, body)
            return []

        response = self.session.query(index=index, body=body)
        return self.search_result_format(response)

    def _query_count(self, index, body):
        """
        Query the number of data for the specified condition
        :param index: es index
        :param body: query keywords
        :return: number of query result
        """
        if not index or not isinstance(body, dict):
            LOGGER.error('index: %s or query_body: %s unavailable', index, body)
            return 0

        count = self.session.count(index=index, body=body)
        return self.count_result_format(count)

    @staticmethod
    def _construct_term_query_body(body, keyword=False):
        """
        Construct a query body for multi-field filtering
        :param body: old query body
        :param keyword: Whether to use keyword as field type
        :return: new query body
        """
        new_body_list = list()
        if not isinstance(body, dict):
            return new_body_list

        for key, value in body.items():
            if keyword:
                new_body_list.append({'term': {f'{key}.keyword': value}})
            else:
                new_body_list.append({'term': {key: value}})

        return new_body_list
