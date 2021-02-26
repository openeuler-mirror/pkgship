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
import unittest
import shutil
import sqlite3
from unittest import mock
from elasticsearch import helpers, Elasticsearch
from elasticsearch.exceptions import ElasticsearchException
from packageship.application.initialize.integration import ESJson
from packageship.application.initialize.integration import InitializeService, del_temporary_file, RepoConfig
from packageship.application.common.exc import InitializeError
from packageship.application.database.session import DatabaseSession
from packageship.application.database.engines.elastic import ElasticSearch
from packageship.application.initialize.repo import RepoFile
from packageship.application.query import database
import redis
from redis import Redis


class TestImport(unittest.TestCase):
    """test Initialize data import"""

    def setUp(self):
        self._init_service = InitializeService()
        self._path = os.path.dirname(__file__)
        self.src_dbfile = os.path.join(
            self._path, "data", "openeuler-right-source.sqlite")
        self.bin_dbfile = os.path.join(
            self._path, "data", "openeuler-right-binary.sqlite")
        self.filelist_dbfile = os.path.join(
            self._path, "data", "openeuler-right-filelist.sqlite")
        self._repo = dict(dbname="openeuler", src_db_file=self.src_dbfile,
                          bin_db_file=self.bin_dbfile, file_list=self.filelist_dbfile, priority=1)

    def test_delete_file(self):
        """Delete the file"""
        path = "/etc/test_delete"
        if not os.path.exists(path):
            fd = open(path, mode="w", encoding="utf-8")
            fd.close()
        del_temporary_file(path=path)

    def test_delete_not_exists_file(self):
        """Delete files that are not saved"""
        path = "/etc/test_delete"
        del_temporary_file(path)

    def test_delete_empty_folder(self):
        """delete the empty folder"""
        path = "/etc/test_delte"
        if not os.path.exists(path):
            os.mkdir(path)
        del_temporary_file(path=path, folder=True)

    def test_delete_folder(self):
        """delete the folder"""
        path = "/etc/test_delte"
        if os.path.exists(path):
            shutil.rmtree(path)
        os.mkdir(path)
        fd = open(os.path.join(path, "file"), mode="w", encoding="utf-8")
        fd.close()
        os.mkdir(os.path.join(path, "folder"))
        del_temporary_file(path=path, folder=True)

    @mock.patch.object(RepoConfig, "load_config")
    def test_import_depend(self, mock_load_config):
        """Import dependencies"""
        with self.assertRaises(InitializeError):
            self._init_service.import_depend(path="")
        with mock.patch("packageship.application.initialize.integration.RepoConfig.validate",
                        new_callable=mock.PropertyMock) as mock_validate:
            mock_load_config.return_value = ""
            mock_validate.return_value = False
            with self.assertRaises(InitializeError):
                self._init_service.import_depend(path="")

    @mock.patch.object(InitializeService, "_save")
    @mock.patch.object(InitializeService, "_sqlite_file")
    @mock.patch.object(RepoConfig, "__iter__")
    @mock.patch.object(InitializeService, "_clear_all_index")
    @mock.patch.object(RepoConfig, "load_config")
    def test_import_config_repo(self, mock_load_config, mock__clear_all_index,
                                mock___iter__, mock__sqlite_file, mock__save):
        """Import the configuration file repo"""
        with mock.patch("packageship.application.initialize.integration.RepoConfig.validate",
                        new_callable=mock.PropertyMock) as mock_validate:
            mock_load_config.return_value = ""
            mock_validate.return_value = True
            mock__clear_all_index.return_value = None
            mock___iter__.return_value = iter([self._repo])
            mock__sqlite_file.return_value = ""
            mock__save.return_value = ""
            self.assertEqual(None, self._init_service.import_depend(path=""))

    @mock.patch.object(InitializeService, "_sqlite_file")
    @mock.patch.object(RepoConfig, "__iter__")
    @mock.patch.object(InitializeService, "_clear_all_index")
    @mock.patch.object(RepoConfig, "load_config")
    def test_sqlite_file_failed(self, mock_load_config,
                                mock__clear_all_index, mock___iter__, mock__sqlite_file):
        """Import the configuration file repo"""
        with mock.patch("packageship.application.initialize.integration.RepoConfig.validate",
                        new_callable=mock.PropertyMock) as mock_validate:
            mock_load_config.return_value = ""
            mock_validate.return_value = True
            mock__clear_all_index.return_value = None
            mock___iter__.return_value = iter([self._repo])
            init_service = InitializeService()
            mock__sqlite_file.side_effect = FileNotFoundError()
            self.assertEqual(None, init_service.import_depend(path=""))

    @mock.patch.object(InitializeService, "_create_index")
    @mock.patch.object(InitializeService, "_sqlite_file")
    @mock.patch.object(RepoConfig, "__iter__")
    @mock.patch.object(InitializeService, "_clear_all_index")
    @mock.patch.object(RepoConfig, "load_config")
    def test_create_index_failed(self, mock_load_config, mock__clear_all_index,
                                 mock___iter__, mock__sqlite_file, mock__create_index):
        """create index failed"""
        with mock.patch("packageship.application.initialize.integration.RepoConfig.validate",
                        new_callable=mock.PropertyMock) as mock_validate:
            mock_load_config.return_value = ""
            mock_validate.return_value = True
            mock__clear_all_index.return_value = None
            mock___iter__.return_value = iter([self._repo])
            mock__sqlite_file.return_value = None
            mock__create_index.return_value = ["openeuler"]
            init_service = InitializeService()
            setattr(init_service, "_repo", dict(dbname="openeuler"))
            self.assertEqual(None, init_service.import_depend(path=""))

    @mock.patch.object(Elasticsearch, "__init__")
    @mock.patch.object(Elasticsearch, "index")
    @mock.patch.object(DatabaseSession, "connection")
    @mock.patch.object(helpers, "bulk")
    @mock.patch.object(InitializeService, "_create_index")
    @mock.patch.object(InitializeService, "_sqlite_file")
    @mock.patch.object(RepoConfig, "__iter__")
    @mock.patch.object(InitializeService, "_clear_all_index")
    @mock.patch.object(RepoConfig, "load_config")
    def test_dont_bulk(self, mock_load_config, mock__clear_all_index,
                       mock___iter__, mock__sqlite_file, mock__create_index,
                       mock_bulk, mock_connection, mock_index, mock___init__):
        """Bulk insert"""
        with mock.patch("packageship.application.initialize.integration.RepoConfig.validate",
                        new_callable=mock.PropertyMock) as mock_validate:
            mock_load_config.return_value = ""
            mock_validate.return_value = True
            mock__clear_all_index.return_value = None
            mock___iter__.return_value = iter([self._repo])
            mock__sqlite_file.return_value = None
            mock__create_index.return_value = []
            mock_bulk.return_value = ""
            mock___init__.return_value = None
            mock_connection.return_value = ElasticSearch()
            mock_index.return_value = None
            init_service = InitializeService()
            setattr(init_service, "_repo", self._repo)
            setattr(init_service, "_data", ESJson())
            self.assertEqual(None, init_service.import_depend(path=""))
            self.assertEqual(True, init_service.success)
            self.assertEqual([], init_service.fail)

    @mock.patch.object(RepoFile, "files")
    @mock.patch.object(RepoConfig, "__iter__")
    @mock.patch.object(InitializeService, "_clear_all_index")
    @mock.patch.object(RepoConfig, "load_config")
    def test_sqlite_file(self, mock_load_config, mock__clear_all_index,
                         mock___iter__, mock_files):
        """sqlite file path"""
        with mock.patch("packageship.application.initialize.integration.RepoConfig.validate",
                        new_callable=mock.PropertyMock) as mock_validate:
            mock_load_config.return_value = ""
            mock_validate.return_value = True
            mock__clear_all_index.return_value = None
            mock___iter__.return_value = iter([self._repo])
            mock_files.return_value = ""
            init_service = InitializeService()
            setattr(init_service, "_repo", self._repo)
            init_service.import_depend(path="")
            self.assertEqual('', getattr(init_service, "_repo")["src_db_file"])
            self.assertEqual('', getattr(init_service, "_repo")["bin_db_file"])
            self.assertEqual('', getattr(init_service, "_repo")["file_list"])

    @mock.patch.object(Elasticsearch, "__init__")
    @mock.patch.object(DatabaseSession, "connection")
    @mock.patch("packageship.application.query.database.get_db_priority")
    @mock.patch.object(RepoConfig, "__iter__")
    @mock.patch.object(RepoConfig, "load_config")
    def test_clear_all_index(self, mock_load_config, mock___iter__,
                             mock_get_db_priority, mock_connection, mock___init__):
        """clear all index"""
        with mock.patch("packageship.application.initialize.integration.RepoConfig.validate",
                        new_callable=mock.PropertyMock) as mock_validate:
            mock_validate.return_value = True
            mock_get_db_priority.return_value = ["openeuler"]
            mock___init__.return_value = None
            elastic = ElasticSearch()
            elastic.delete_index = lambda x: None
            mock_connection.return_value = elastic
            mock_load_config.return_value = ""
            mock___iter__.return_value = iter([])
            init_service = InitializeService()
            setattr(init_service, "_repo", self._repo)
            self.assertEqual(None, init_service.import_depend(path=""))

    @mock.patch.object(Elasticsearch, "__init__")
    @mock.patch.object(DatabaseSession, "connection")
    @mock.patch.object(InitializeService, "_sqlite_file")
    @mock.patch.object(RepoConfig, "__iter__")
    @mock.patch.object(InitializeService, "_clear_all_index")
    @mock.patch.object(RepoConfig, "load_config")
    def test_create_index(self, mock_load_config, mock__clear_all_index,
                          mock___iter__, mock__sqlite_file,  mock_connection, mock___init__):
        """create index"""
        with mock.patch("packageship.application.initialize.integration.RepoConfig.validate",
                        new_callable=mock.PropertyMock) as mock_validate:
            mock_load_config.return_value = ""
            mock_validate.return_value = True
            mock__clear_all_index.return_value = None
            mock___iter__.return_value = iter([self._repo])
            mock__sqlite_file.return_value = None

            mock___init__.return_value = None
            elastic = ElasticSearch()
            elastic.create_index = lambda x: ["openeuler"]
            elastic.delete_index = lambda x: None
            mock_connection.return_value = elastic
            init_service = InitializeService()
            setattr(init_service, "_repo", self._repo)
            init_service.import_depend(path="")
            self.assertEqual(
                ["openeuler"], getattr(init_service, "_fail"))

    @mock.patch.object(Elasticsearch, "__init__")
    @mock.patch.object(DatabaseSession, "connection")
    @mock.patch.object(InitializeService, "_source_depend")
    @mock.patch.object(InitializeService, "_create_index")
    @mock.patch.object(InitializeService, "_sqlite_file")
    @mock.patch.object(RepoConfig, "__iter__")
    @mock.patch.object(InitializeService, "_clear_all_index")
    @mock.patch.object(RepoConfig, "load_config")
    def test_save_exception(self, mock_load_config, mock__clear_all_index,
                            mock___iter__, mock__sqlite_file, mock__create_index,
                            mock__source_depend, mock_connection, mock___init__):
        """save exception"""
        with mock.patch("packageship.application.initialize.integration.RepoConfig.validate",
                        new_callable=mock.PropertyMock) as mock_validate:
            mock_load_config.return_value = ""
            mock_validate.return_value = True
            mock__clear_all_index.return_value = None
            mock___iter__.return_value = iter([self._repo])
            mock__sqlite_file.return_value = None
            mock__create_index.return_value = []
            mock___init__.return_value = None
            mock__source_depend.side_effect = TypeError()
            mock__create_index.return_value = []
            elastic = ElasticSearch()
            elastic.delete_index = lambda x: ["openeuler"]
            mock_connection.return_value = elastic
            init_service = InitializeService()
            setattr(init_service, "_repo", self._repo)
            init_service.import_depend(path="")
            self.assertEqual(["openeuler"], getattr(init_service, "_fail"))

    def test_query_sqlite(self):
        """query sqlite database"""
        path = os.path.dirname(__file__)
        sql = "select * from packages"
        with self.assertRaises(sqlite3.DatabaseError):
            query = getattr(self._init_service, "_query")
            query(table="src_pack", database=os.path.join(path, "data", "error_config_yaml.txt"),
                  sql=sql, key="name")

    def test_esjson_set_item(self):
        """json set data"""
        es_json = ESJson()
        es_json.database = "openeuler"

    def test_load_config_exception(self):
        """Error loading configuration file"""
        with self.assertRaises(InitializeError):
            self._init_service.import_depend(path=None)

    @mock.patch.object(RepoConfig, "load_config")
    def test_load_config_error(self, mock_load_config):
        """test load config file error"""
        mock_load_config.side_effect = FileNotFoundError()
        with self.assertRaises(InitializeError):
            self._init_service.import_depend(path="")

    @mock.patch.object(RepoConfig, "__iter__")
    @mock.patch.object(Redis, "exists")
    @mock.patch.object(InitializeService, "_clear_all_index")
    @mock.patch.object(RepoConfig, "load_config")
    def test_redis_connection_error(self, mock_load_config, mock__clear_all_index, mock_exists,
                                    mock___iter__):
        """redis connection error"""
        with mock.patch("packageship.application.initialize.integration.RepoConfig.validate",
                        new_callable=mock.PropertyMock) as mock_validate:
            mock_load_config.return_value = ""
            mock_validate.return_value = True
            mock__clear_all_index.return_value = None
            mock___iter__.return_value = iter([])
            mock_exists.side_effect = redis.RedisError
            self.assertEqual(None, self._init_service.import_depend(path=""))

    @mock.patch.object(RepoConfig, "__iter__")
    @mock.patch.object(Redis, "delete")
    @mock.patch.object(Redis, "keys")
    @mock.patch.object(InitializeService, "_clear_all_index")
    @mock.patch.object(RepoConfig, "load_config")
    def test_redis_delete_error(self, mock_load_config, mock__clear_all_index,
                                mock_keys, mock_delete, mock___iter__):
        """redis delete error"""
        with mock.patch("packageship.application.initialize.integration.RepoConfig.validate",
                        new_callable=mock.PropertyMock) as mock_validate:
            mock_load_config.return_value = ""
            mock_validate.return_value = True
            mock__clear_all_index.return_value = None
            mock___iter__.return_value = iter([])
            mock_keys.side_effect = [True, (1, 2)]
            mock_delete.side_effect = redis.RedisError()
            self.assertEqual(None, self._init_service.import_depend(path=""))

    @mock.patch.object(InitializeService, "_delete_depend_index")
    @mock.patch.object(InitializeService, "_save")
    @mock.patch.object(InitializeService, "_sqlite_file")
    @mock.patch.object(RepoConfig, "__iter__")
    @mock.patch.object(InitializeService, "_clear_all_index")
    @mock.patch.object(RepoConfig, "load_config")
    def test_save_es_exception(self, mock_load_config, mock__clear_all_index,
                               mock___iter__, mock__sqlite_file, mock__save,
                               mock__delete_depend_index):
        """save exception"""
        with mock.patch("packageship.application.initialize.integration.RepoConfig.validate",
                        new_callable=mock.PropertyMock) as mock_validate:
            mock_load_config.return_value = ""
            mock_validate.return_value = True
            mock__clear_all_index.return_value = None
            mock___iter__.return_value = iter([self._repo])
            mock__sqlite_file.return_value = None
            mock__save.side_effect = ElasticsearchException()
            mock__delete_depend_index.return_value = None
            init_service = InitializeService()
            setattr(init_service, "_repo", self._repo)
            init_service.import_depend(path="")
            self.assertEqual(["openeuler"], getattr(init_service, "_fail"))
