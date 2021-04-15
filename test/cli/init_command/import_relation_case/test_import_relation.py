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
import shutil
from test.cli.init_command import InitTestBase
from packageship.application.initialize.integration import InitializeService
from packageship.libs.conf import configuration


LOCATION_CONFIG = """
- dbname: openeuler
  src_db_file: {src}
  bin_db_file: {bin}
  priority: 1
"""

REMOTE_CONFIG = """
- dbname: openeuler
  src_db_file: https://repo.openeuler.org/openEuler-20.09/source
  bin_db_file: https://repo.openeuler.org/openEuler-20.09/everything/aarch64
  priority: 1
"""


class TestImportRelation(InitTestBase):
    """
    Initialize the data import test case
    """
    _dirname = os.path.dirname(__file__)

    def setUp(self):
        super(TestImportRelation, self).setUp()
        _location_path = os.path.join(self._dirname, "sqlites")

        self._location_config = self.create_file(
            write_content=LOCATION_CONFIG.format(src="file://" + os.path.join(_location_path, "src"),
                                                 bin="file://" + os.path.join(_location_path, "bin")),
            path=self._create_file_path)

        self._remote_config = self.create_file(
            write_content=REMOTE_CONFIG,
            path=self._create_file_path)

        configuration.TEMPORARY_DIRECTORY = os.path.join(self._dirname, "tmp")
        self.mock_es_exists(return_value=False)
        self.mock_es_delete(return_value=None)
        self.mock_es_search(return_value=dict(hits={"hits": []}))
        self.mock_es_create(return_value=None)
        self._mock_bulk()
        self.mock_es_insert(return_value=None)

    def comparsion_result(self, client, actions, stats_only=False, *args, **kwargs):
        pass

    def test_import_location_repo(self):
        """
        Import data relationships as local files
        """
        init_service = InitializeService()
        init_service.import_depend(path=self._location_config)
        self.assertEqual(True, init_service.success)

    def test_import_remote_repo(self):
        """
        Import data relationships as remote files
        """
        init_service = InitializeService()
        init_service.import_depend(path=self._remote_config)
        self.assertEqual(True, init_service.success)

    def tearDown(self) -> None:
        shutil.rmtree(os.path.join(
            self._dirname, "tmp"))
        configuration.TEMPORARY_DIRECTORY = "/opt/pkgship/tmp/"
