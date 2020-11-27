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
test_get_single_packages
"""
from io import BytesIO

import unittest
from test.base_code.read_data_base import ReadTestBase
import pandas as pd

from packageship.application.apps.package.function.constants import ResponseCode


class TestDownloadExcelFile(ReadTestBase):
    """
    Download test of excel file
    """
    BASE_URL = "/lifeCycle/download/"
    REQUESTS_KWARGS = {
        "url": "",
        "method": "GET"
    }

    def test_file_type_error(self):
        """
            The file type to be downloaded for the test is incorrect
        """
        self.REQUESTS_KWARGS["url"] = self.BASE_URL + "xxx"
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)
        self.response_json_error_judge(
            resp_dict, resp_code=ResponseCode.PARAM_ERROR, method=self)

    def test_issue_file(self):
        """
            Issue file download test
        """
        self.REQUESTS_KWARGS["url"] = self.BASE_URL + "issues"
        resp_dict = self.client.get(self.REQUESTS_KWARGS["url"])
        data_frame = pd.read_excel(
            BytesIO(resp_dict.data), sheet_name='Summary', engine='xlrd')
        datas = data_frame.values.tolist()
        self.assertEqual(
            14, len(datas), msg="An error occurred in the downloaded data")
        data_dict = dict(zip(data_frame.columns.tolist(), datas[0]))
        data = {
            'issue_id': 'I1OQW8',
            'issue_url': 'https://gitee.com/openeuler/openEuler-Advisor/issues/I1PGWQ',
            'issue_content': 'def get_yaml(self, pkg):',
            'issue_title': '【CI加固】对识别修改对周边组件和升级影响',
            'issue_status': 'open',
            'pkg_name': 'dnf',
            'issue_type': 'defect',
            'related_release': 'hahaxx'}
        self.assertEqual(data, data_dict,
                         msg='An error occurred in the downloaded data')

    def test_package_file(self):
        """
            download packages file
        """

        self.REQUESTS_KWARGS["url"] = self.BASE_URL + \
                                      "packages" + "?table_name=mainline"

        response = self.client.get(self.REQUESTS_KWARGS["url"])
        data_frame = pd.read_excel(
            BytesIO(response.data), sheet_name='Summary', engine='xlrd')
        datas = data_frame.values.tolist()
        self.assertEqual(
            5, len(datas), msg="An error occurred in the downloaded data")
        data_dict = dict(zip(data_frame.columns.tolist(), datas[0]))
        data = {
            'name': 'CUnit',
            'url': 'http://cunit.sourceforge.net/',
            'rpm_license': 'LGPLv2+',
            'version': '2.1.3',
            'release': '21.oe1',
            'release_time': 1.0,
            'used_time': 2.0,
            'latest_version': 3.0,
            'latest_version_time': 4.0,
            'feature': 5,
            'cve': 0,
            'defect': 0,
            'maintainer': 'userA',
            'maintainlevel': 6.0,
        }
        self.assertEqual(data, data_dict,
                         msg='An error occurred in the downloaded data')

    def test_package_file_no_table_name(self):
        """
            download packages file
        """
        self.REQUESTS_KWARGS["url"] = self.BASE_URL + "packages"
        response = self.client_request(self.REQUESTS_KWARGS["url"])
        self.response_json_format(response)
        self.assertEqual(ResponseCode.SERVICE_ERROR, response.get(
            'code'), msg='Error in status code return')


if __name__ == '__main__':
    unittest.main()
