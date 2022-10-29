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
import sys
import copy
import shutil
from unittest.mock import Mock
from test.cli.init_command import InitTestBase
from packageship.application.initialize.integration import InitializeService
from elasticsearch.exceptions import ElasticsearchException
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

LOCATION_XML_CONFIG = """
- dbname: openeuler
  db_file: {dbfile}
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
        if "gevent.monkey" in sys.modules:
            del sys.modules["gevent.monkey"]

        self._location_config = self.create_file(
            write_content=LOCATION_CONFIG.format(
                src="file://" + os.path.join(_location_path, "src"),
                bin="file://" + os.path.join(_location_path, "bin"),
            ),
            path=self._create_file_path,
        )

        self._remote_config = self.create_file(
            write_content=REMOTE_CONFIG, path=self._create_file_path
        )

        self._base_return_value = {
            "hits": {
                "hits": [
                    {
                        "_source": {
                            "database_name": "openeuler",
                            "priority": 1,
                            "hash_addr": "b666b1641a76846444840995b91bc63a",
                            "src_dbfile_hash": "65ed012f89d64e0e686667f726a5f00c",
                            "bin_dbfile_hash": "bbb7a0ba486fe71c9560287e098877e4",
                            "db_file_hash": None,
                            "file_list_hash": "1e044c506011db2ed0144aa28c8db3b1",
                        }
                    }
                ]
            }
        }

        configuration.TEMPORARY_DIRECTORY = os.path.join(self._dirname, "tmp")
        self._mock()

    def _mock(self):
        self.mock_es_exists(return_value=False)
        self.mock_es_delete(return_value=None)
        self.mock_es_create(return_value=None)
        self._mock_bulk()
        self.mock_es_insert(return_value=None)

    @property
    def search_value(self):
        return copy.deepcopy(self._base_return_value)

    def comparsion_result(self, client, actions, stats_only=False, *args, **kwargs):
        pass

    def test_import_location_repo(self):
        """
        Import data relationships as local files
        """
        self.mock_es_search(return_value=dict(hits={"hits": []}))
        init_service = InitializeService()
        init_service.import_depend(path=self._location_config)
        self.assertEqual(True, init_service.success)

    def test_addr_hash_change(self):
        self.mock_es_search(return_value=self.search_value)
        init_service = InitializeService()
        init_service.import_depend(path=self._location_config)
        self.assertEqual(True, init_service.success)

    def test_sqlite_file_change(self):
        return_value = copy.deepcopy(self._base_return_value)
        return_value["hits"]["hits"][0]["_source"][
            "hash_addr"
        ] = "84f24da3ec202dc455a119f44e8f483d"
        self.mock_es_search(return_value=return_value)
        init_service = InitializeService()
        init_service.import_depend(path=self._location_config)
        self.assertEqual(True, init_service.success)

    def test_file_and_dbname_change(self):
        return_value = copy.deepcopy(self._base_return_value)
        return_value["hits"]["hits"][0]["_source"][
            "hash_addr"
        ] = "84f24da3ec202dc455a119f44e8f483d"
        return_value["hits"]["hits"][0]["_source"]["database_name"] = "openeuler-test"
        self.mock_es_search(return_value=return_value)
        init_service = InitializeService()
        init_service.import_depend(path=self._location_config)
        self.assertEqual(True, init_service.success)

    def test_file_and_dbname_consistent(self):
        return_value = copy.deepcopy(self._base_return_value)
        return_value["hits"]["hits"][0]["_source"] = {
            "database_name": "openeuler",
            "priority": 1,
            "hash_addr": "84f24da3ec202dc455a119f44e8f483d",
            "src_dbfile_hash": "4e99be1dc02031388447f6bd4fcf40d7",
            "bin_dbfile_hash": "64e6a247348cc2bacbb9b76320962b3e",
            "db_file_hash": None,
            "file_list_hash": "6ddcc79a557472e285ed598697728891",
        }
        self.mock_es_search(return_value=return_value)
        init_service = InitializeService()
        init_service.import_depend(path=self._location_config)
        self.assertEqual(True, init_service.success)

    def test_xml_file(self):
        config_file = self.create_file(
            write_content=LOCATION_XML_CONFIG.format(
                dbfile="file://" + os.path.join(self._dirname, "sqlites", "xml"),
            ),
            path=self._create_file_path,
        )
        self.mock_es_search(return_value=self.search_value)
        init_service = InitializeService()
        init_service.import_depend(path=config_file)
        self.assertEqual(True, init_service.success)

    def test_dbname_addr_change(self):
        return_value = copy.deepcopy(self._base_return_value)
        return_value["hits"]["hits"][0]["_source"]["database_name"] = "openeuler-test"
        self.mock_es_search(return_value=return_value)
        init_service = InitializeService()
        init_service.import_depend(path=self._location_config)
        self.assertEqual(True, init_service.success)

    def test_content_consistent_reindex(self):
        return_value = copy.deepcopy(self._base_return_value)
        return_value["hits"]["hits"][0]["_source"] = {
            "database_name": "openeuler-test",
            "priority": 1,
            "hash_addr": "84f24da3ec202dc455a119f44e8f483d",
            "src_dbfile_hash": "4e99be1dc02031388447f6bd4fcf40d7",
            "bin_dbfile_hash": "64e6a247348cc2bacbb9b76320962b3e",
            "db_file_hash": None,
            "file_list_hash": "6ddcc79a557472e285ed598697728891",
        }
        self.mock_es_search(return_value=return_value)
        self.mock_es_reindex(return_value=None)
        init_service = InitializeService()
        init_service.import_depend(path=self._location_config)
        self.assertEqual(True, init_service.success)

    def test_import_relation_error_tips(self):
        self.mock_es_search(return_value=self.search_value)
        init_service = InitializeService()
        init_service._source_depend = Mock()
        init_service._source_depend.side_effect = ElasticsearchException
        init_service.import_depend(path=self._location_config)
        self.assertEqual(False, init_service.success)

    def test_save_exception(self):
        self.mock_es_search(return_value=self.search_value)
        init_service = InitializeService()
        init_service._save = Mock()
        init_service._save.side_effect = ElasticsearchException
        init_service.import_depend(path=self._location_config)
        self.assertEqual(False, init_service.success)

    def tearDown(self) -> None:
        if os.path.exists(os.path.join(self._dirname, "tmp")):
            shutil.rmtree(os.path.join(self._dirname, "tmp"))
        configuration.TEMPORARY_DIRECTORY = "/opt/pkgship/tmp/"
