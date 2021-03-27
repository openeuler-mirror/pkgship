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
The request class that reads the interface in the unit test
"""
import os
from packageship.application.common.exc import Error
from .basetest import TestBase


try:

    from packageship import BASE_PATH
    from packageship.libs.conf import configuration
    from test.coverage_tests.base_code.init_config_path import init_config

    configuration.DATABASE_FOLDER_PATH = os.path.join(
        os.path.dirname(BASE_PATH), 'test', 'common_files', 'dbs')

    from packageship.selfpkg import app

except Error:
    raise Error


class ReadTestBase(TestBase):
    """
    ReadTestBase
    """

    def setUp(self):
        """
        Initial preparation of unit tests
        """
        self.client = app.test_client()
