#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""
OperateTestBase
"""
import os
from packageship.libs.exception import Error
from .basetest import TestBase



try:
    from packageship import BASE_PATH
    from packageship.libs.conf import configuration
    from test.base_code.init_config_path import init_config

    configuration.DATABASE_FOLDER_PATH = os.path.join(os.path.dirname(BASE_PATH),
                                                      'test',
                                                      'common_files',
                                                      'operate_dbs')

    from packageship.manage import app
except Error:
    raise Error


class OperateTestBase(TestBase):
    """
    OperateTestBase
    """

    def setUp(self):
        """
        Initial preparation of unit tests
        """
        self.client = app.test_client()
