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
# -*- coding:utf-8 -*-
"""
test_get_pkgship_cmd
"""
from pathlib import Path
from requests import Response
from unittest.mock import PropertyMock
from requests import RequestException
from packageship.application.cli.commands.db import DbPriorityCommand
from packageship.application.common.exc import ElasticSearchQueryException
from test.cli import DATA_BASE_INFO
from test.cli.dbs_command import DbsTest

DATA_FOLDER = Path(Path(__file__).parent, "mock_data")


class TestDB(DbsTest):
    """
    class for test DB priority
    """
    cmd_class = DbPriorityCommand

    def test_true_params(self):
        """
        test true params
        """
        self.mock_es_search(return_value=DATA_BASE_INFO)
        self.excepted_str = """
DB priority
['os-version']
        """
        self.assert_result()


    def test_different_db_priority(self):
        """
        test different db priority
        """
        self.excepted_str = """
DB priority
['os-version-1', 'os-version-2', 'os-version-3']
        """
        self.mock_es_search(return_value=self.read_file_content(
            "different_priority_dbs.json",
            folder=DATA_FOLDER))
        self.assert_result()

    def test_same_db_priority(self):
        """
        test same db priority
        """
        self.excepted_str = """
DB priority
['os-version-1', 'aa', 'bbb', 'test']
        """
        self.mock_es_search(return_value=self.read_file_content(
            "same_priority_dbs.json",
            folder=DATA_FOLDER))
        self.assert_result()

    def test_wrong_db_data(self):
        """
        test wrong dbs data
        """
        self.excepted_str = """
ERROR_CONTENT  :Unable to get the generated database information
HINT           :Make sure the generated database information is valid
        """
        self.mock_es_search(return_value={})
        self.assert_result()

    def test_raise_es_error(self):
        """test_raise_es_error"""

        self.excepted_str = """
ERROR_CONTENT  :Unable to get the generated database information
HINT           :Make sure the generated database information is valid
"""
        self.mock_es_search(side_effect=ElasticSearchQueryException)
        self.assert_result()

    def test_request_raise_requestexception(self):
        """test_request_raise_requestexception"""

        self.excepted_str = """
ERROR_CONTENT  :
HINT           :The remote connection is abnormal, please check the 'remote_host' parameter value to ensure the connectivity of the remote address
"""
        self.mock_requests_get(side_effect=[RequestException])
        self.assert_result()

    def test_request_text_raise_jsonerror(self):
        """test_request_text_raise_jsonerror"""

        class Resp:
            text = """{"test":\'123\',}"""
            status_code = 200

        self.excepted_str = """
ERROR_CONTENT  :{"test":\'123\',}
HINT           :The content is not a legal json format,please check the parameters is valid
"""
        self.mock_requests_get(return_value=Resp())
        self.assert_result()

    def test_request_status_429(self):
        """test_request_status_429"""

        self.excepted_str = """
Too many requests in a short time, please request again later
"""
        r = Response()
        r.status_code = 429
        self.mock_requests_get(return_value=r)
        self.assert_result()

    def test_request_status_500(self):
        """test_request_status_500"""
        self.excepted_str = """
ERROR_CONTENT  :500 Server Error: None for url: None
HINT           :The remote connection is abnormal, please check the 'remote_host' parameter value to ensure the connectivity of the remote address
"""
        r = Response()
        r.status_code = 500
        self.mock_requests_get(return_value=r)
        self.assert_result()
