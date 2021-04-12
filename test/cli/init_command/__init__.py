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
import os
import uuid
import pwd
from unittest.mock import Mock
import requests
import json
from test.cli import BaseTest
from packageship.application.cli.commands.initialize import InitDatabaseCommand, InitServiceThread
from packageship.application.common.exc import InitializeError, ResourceCompetitionError
from elasticsearch import helpers, Elasticsearch
from packageship.application.initialize.integration import InitializeService, RepoConfig
from packageship.application.database.session import DatabaseSession
from packageship.application.database.engines.elastic import ElasticSearch


def _init_(self, func, param, *args, **kwargs):
    super(InitServiceThread, self).__init__(*args, **kwargs)
    self.error = True


class InitTestBase(BaseTest):
    cmd_class = InitDatabaseCommand

    def setUp(self):
        super(InitTestBase, self).setUp()
        self.init_service = InitializeService()

    @property
    def _create_file_path(self):
        path = os.path.join(
            self._dirname, "conf", "{}.yaml".format(uuid.uuid1()))
        return path

    def create_conf_file(self, content, path):
        """
        Creating configuration files
        """
        with open(path, "w", encoding="utf-8") as file:
            file.write(content)
        return path

    def comparsion_than(self):
        self.mock_init_thread()
        self.mock_user()
        self.mock_es_exists(return_value=False)
        self.mock_es_delete(return_value=None)
        self.mock_es_search(return_value=dict(hits={"hits": []}))
        self.mock_es_create(return_value=None)
        self._mock_bulk()
        self.mock_es_insert(return_value=None)

    def init_true(self):
        InitServiceThread.__init__ = _init_

    def thread_start(self):
        try:
            self.init_service.import_depend(path=self._conf)
        except (InitializeError, ResourceCompetitionError) as error:
            print('\r', error)

    def mock_init_thread(self):
        InitServiceThread.start = Mock()
        InitServiceThread.start.side_effect = self.thread_start

    def _mock_bulk(self):
        helpers.bulk = Mock()
        helpers.bulk.side_effect = self.comparsion_result

    def _mock_binary_depend(self):
        InitializeService._binary_depend = Mock()
        InitializeService._binary_depend.return_value = None

    def _mock_source_depend(self):
        InitializeService._source_depend = Mock()
        InitializeService._source_depend.return_value = None

    def mock_user(self):
        pwd.getpwuid = Mock(return_value=["root"])
