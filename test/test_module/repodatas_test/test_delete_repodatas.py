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
test delete repodatas
"""

import os
import shutil
from test.base_code.operate_data_base import OperateTestBase
from packageship.libs.conf import configuration

from packageship.libs.exception import Error


from packageship.application.apps.package.function.constants import ResponseCode


class TestDeleteRepodatas(OperateTestBase):
    """
    test delete repodata
    """
    BASE_URL = "/repodatas?dbName="
    REQUESTS_KWARGS = {
        "url": "",
        "method": "DELETE"
    }

    def test_init_wrong(self):
        """
        Initialization failed. No database was generated. Database information could not be found
        Returns:

        """

        self.REQUESTS_KWARGS["url"] = self.BASE_URL + "test"
        self.without_dbs_folder(
            self.REQUESTS_KWARGS,
            met=self,
            code=ResponseCode.FILE_NOT_FOUND, test_type='operate')

    def test_miss_dbname(self):
        """The pass parameter is parameters"""

        # Scenario 1: the value passed by dbname is empty
        self.REQUESTS_KWARGS["url"] = self.BASE_URL
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)
        self.response_json_error_judge(
            resp_dict, resp_code=ResponseCode.PARAM_ERROR, method=self)

    def test_wrong_db_name(self):
        """
        Database name error
        Returns:

        """
        self.REQUESTS_KWARGS["url"] = self.BASE_URL + "test"
        resp_dict = self.client_request(**self.REQUESTS_KWARGS)

        self.response_json_error_judge(
            resp_dict, resp_code=ResponseCode.DB_NAME_ERROR, method=self)

    def test_ture_dbname(self):
        """
        database name
        Returns:

        """
        try:
            if os.path.exists(configuration.DATABASE_FOLDER_PATH):
                shutil.copytree(
                    configuration.DATABASE_FOLDER_PATH,
                    configuration.DATABASE_FOLDER_PATH + '.bak')
            self.REQUESTS_KWARGS["url"] = self.BASE_URL + "mainline"
            resp_dict = self.client_request(**self.REQUESTS_KWARGS)
            self.response_json_error_judge(
                resp_dict, resp_code=ResponseCode.SUCCESS, method=self)
        except Error:
            return
        finally:
            if os.path.exists(
                    configuration.DATABASE_FOLDER_PATH) and \
                    os.path.exists(configuration.DATABASE_FOLDER_PATH + '.bak'):
                shutil.rmtree(configuration.DATABASE_FOLDER_PATH)
                os.rename(
                    configuration.DATABASE_FOLDER_PATH + '.bak',
                    configuration.DATABASE_FOLDER_PATH)
