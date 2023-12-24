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
import copy
from packageship.application.common.constant import (
    BUILD_STATES,
    BUILD_TIMES,
    BUILD_TIME_LEVEL,
    MAX_NUM_OF_RESULT,
)
from packageship.application.common.exc import (
    DatabaseConfigException,
    ElasticSearchQueryException,
)
from packageship.application.query import Query, QueryBody
from packageship.libs.log import LOGGER

# Query the iso information of the past 30 days by default
DEFAULT_SUGGESTION_COUNT = 20
DEFAULT_ISO_QUERY_DAYS = 31


class PanelInfo(Query):
    """
    Panel information database query class
    """

    def __init__(self):
        super(PanelInfo, self).__init__()
        self.query_body = QueryBody()

    def query_obs_info(
        self, body: dict, index="obs_info", source=None, page_index=0, page_size=0
    ):
        """
        Query obs page information
        :param index: elasticsearch index
        :param body: query keywords exp:{"repo_name":"gcc","gitee_branch":"openEuler-22.03-LTS"}
        :param source: Query result filter field exp:["repo_name", "gitee_branch"]
        :param page_index: Pagination query page number exp:1
        :param page_size: Paging query the size of each page exp:50
        :return: query result
        """
        orders = list()
        if "orders" in body:
            orders = body.pop("orders")
        format_query_body = {
            "fields": self._construct_term_query_body(body, keyword=True),
            "_source": None,
            "page_num": None,
            "page_size": None,
        }
        if isinstance(source, list):
            format_query_body["_source"] = source

        _query_all = True
        page_from = (page_index - 1) * page_size
        if all([page_from >= 0, page_size > 0]):
            format_query_body["page_num"] = page_from
            format_query_body["page_size"] = page_size
            _query_all = False

        self.query_body.query_and_filters = format_query_body
        if orders:
            sort = [
                {order_item["order"]: dict(order=order_item["sort_mode"])}
                for order_item in orders
            ]
            self.query_body.query_and_filters["sort"] = sort
        query_result_list = self._query_data(
            index=index, body=self.query_body.query_and_filters, query_all=_query_all
        )

        return [query_result.get("_source") for query_result in query_result_list]

    def query_build_states(self, branch, architecture, index="obs_info"):
        """
        Count the number of states of each component of the software package
        :param branch: gitee branch exp:openEuler-22.03-LTS
        :param architecture: architecture of branch
        :param index: es index
        :return: Number of packages in each state
        """
        state_count = dict()
        body = {
            "gitee_branch": branch,
            "architecture": architecture,
            "build_status": None,
        }
        for state in BUILD_STATES:
            body["build_status"] = state
            self.query_body.query_and_filters = {
                "fields": self._construct_term_query_body(body, keyword=True)
            }
            current_state_count = self._query_count(
                index=index, body=self.query_body.query_and_filters
            )
            state_count[state] = current_state_count

        return state_count

    def query_build_times(self, branch, architecture, index="obs_info"):
        """
        Query the number of packages for each level of build time
        :param branch: gitee branch exp:openEuler-22.03-LTS
        :param architecture: architecture of branch
        :param index: es index
        :return: number of packages for each level of build time
        """
        each_time_count = dict()
        branch_term_dict = {"terms": {"gitee_branch.keyword": branch}}
        arch_term_dict = {"terms": {"architecture": architecture}}
        for i in range(len(BUILD_TIMES)):
            if i < len(BUILD_TIMES) - 1:
                range_dict = {
                    "range": {
                        "build_time": {"gt": BUILD_TIMES[i], "lte": BUILD_TIMES[i + 1]}
                    }
                }
            else:
                range_dict = {"range": {"build_time": {"gt": BUILD_TIMES[i]}}}

            combination_dict = {
                "fields": [branch_term_dict, arch_term_dict, range_dict]
            }
            self.query_body.query_and_filters = combination_dict
            current_level_count = self._query_count(
                index=index, body=self.query_body.query_and_filters
            )
            each_time_count[BUILD_TIME_LEVEL[i]] = current_level_count

        return each_time_count

    def query_iso_info(
        self, branch, index="iso_info", recent_days=DEFAULT_ISO_QUERY_DAYS
    ):
        """
        Query iso build information
        :param branch: gitee branch exp:openEuler-22.03-LTS
        :param index: es index
        :param recent_days: Specify to query the information of the past n days exp:10
        :return: iso info list
        """
        term_dict = {"term": {"branch.keyword": branch}}
        range_dict = {"range": {"date": {"gte": f"now-{recent_days}d"}}}
        combination_dict = {
            "fields": [term_dict, range_dict],
            "query_size": MAX_NUM_OF_RESULT,
        }
        self.query_body.query_and_filters = combination_dict

        query_result_list = self._query_data(
            index=index, body=self.query_body.query_and_filters
        )
        return [query_result.get("_source") for query_result in query_result_list]

    def query_sig_package_state(self, branch):
        """
        Query the compilation status of software packages in the sig group
        :param branch: gitee branch
        """
        body = dict(gitee_branch=branch)
        sig_group_collect = dict()
        pkg_state = dict(failed=0, unresolvable=0)
        for obs_info in self.query_obs_info(body):
            if obs_info["build_status"] not in ("failed", "unresolvable"):
                continue
            try:
                sig_name = obs_info.pop("name")
            except KeyError:
                continue
            if sig_name not in sig_group_collect:
                sig_group_collect[sig_name] = {
                    "standard_x86_64": copy.deepcopy(pkg_state),
                    "standard_aarch64": copy.deepcopy(pkg_state),
                }

            sig_group_collect[sig_name][obs_info["architecture"]][
                obs_info["build_status"]
            ] += 1

        return sig_group_collect

    def query_sig_info(self, sig_name, index="sig_info"):
        """
        Querying sig group information
        :param sig_name: sig name exp:application
        :param index: es index
        :return: sig info
        """
        if not sig_name:
            query_result = self._query_data(
                index=index, body=self.query_body.QUERY_ALL, query_all=True
            )
        else:
            self.query_body.query_term = {"fields": {"name.keyword": sig_name}}
            query_result = self._query_data(
                index=index, body=self.query_body.query_term
            )

        return [sig_info.get("_source") for sig_info in query_result]

    def query_suggest_info(self, index, body: dict, query_all=False, source=None):
        """
        Suggested information query, the query mode is fuzzy query
        :param index: es index
        :param body: query body,Only one filter is supported. etc:{"gitee_branch":"openEuler-20.03-LTS-SP1"}
        :param query_all: Whether to query all
        :param source: filter fields
        :return: query result
        """
        query_body = dict()
        if query_all or not body:
            query_body = self.query_body.QUERY_ALL
            query_body["_source"] = source if isinstance(source, list) else []
            query_result = self._query_data(
                index=index, body=query_body, query_all=query_all
            )
        else:
            for key, value in body.items():
                query_body["fields"] = {f"{key}.keyword": f"*{value}*"}
                break

            query_body["_source"] = source if isinstance(source, list) else []
            query_body["query_size"] = DEFAULT_SUGGESTION_COUNT
            self.query_body.fuzzy_query = query_body
            query_result = self._query_data(
                index=index, body=self.query_body.fuzzy_query
            )

        return [branch_info.get("_source") for branch_info in query_result]

    def _query_data(self, index, body, query_all=False):
        """
        Data query entry
        :param index: elasticsearch index
        :param body: query keywords
        :param query_all: Whether to use the scan method to query all data
        :return: query result
        """
        if not index:
            LOGGER.error("index: %s is unavailable", index)
            return []
        try:
            if query_all:
                response = self.session.scan(index=index, body=body)
            else:
                response = self.session.query(index=index, body=body)
        except ElasticSearchQueryException as error:
            LOGGER.error(f"Query data failed, error: {error}")
            response = None
        return self.search_result_format(response, is_scan=query_all)

    def _query_count(self, index, body):
        """
        Query the number of data for the specified condition
        :param index: es index
        :param body: query keywords
        :return: number of query result
        """
        if not index:
            LOGGER.error("index: %s is unavailable", index)
            return 0
        try:
            count = self.session.count(index=index, body=body)
        except ElasticSearchQueryException as error:
            LOGGER.error(f"Query data failed, error: {error}")
            count = None
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
        for key, value in body.items():
            trem = "term" if isinstance(value, str) else "terms"
            if keyword:
                new_body_list.append({trem: {f"{key}.keyword": value}})
            else:
                new_body_list.append({trem: {key: value}})

        return new_body_list

    def delete(self, body, index):
        """Delete data that meets the requirements
        :param body: query conditions
        :param index: es index
        """
        self.query_body.must_match = body
        self.session.delete(index=index, body=self.query_body.must_match)
