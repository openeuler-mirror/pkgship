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
from unittest import mock
from packageship.application.initialize.integration import RepoConfig


class TestLoadConfig(unittest.TestCase):
    """Repo source configuration file tests"""
    repo_config = RepoConfig()

    def test_load_not_exists_config(self):
        """The config yaml file does not exist"""
        with self.assertRaises(FileNotFoundError):
            self.repo_config.load_config(
                path="/etc/pkgship/test_config.yaml")

    def test_config_path_none(self):
        """The config file path is none"""
        with self.assertRaises(ValueError):
            self.repo_config.load_config(path=None)

    def test_config_not_yaml(self):
        """Wrong YAML format file"""
        _config_path = os.path.join(os.path.dirname(
            __file__), "data", "error_config_yaml.txt")
        with self.assertRaises(ValueError):
            self.repo_config.load_config(path=_config_path)

    def test_repo_isstr(self):
        """YAML content error, validation failed"""
        setattr(self.repo_config, "_repo", "this is repo content")
        self.assertEqual(False, self.repo_config.validate)

    def test_repo_isnone(self):
        """YAML content is None"""
        setattr(self.repo_config, "_repo", None)
        self.assertEqual(False, self.repo_config.validate)

    def test_repo_database_error(self):
        """Database error in repo source"""
        setattr(self.repo_config, "_repo", ["os_version_1"])
        self.assertEqual(False, self.repo_config.validate)

        setattr(self.repo_config, "_repo", [dict(database="test-database")])
        self.assertEqual(False, self.repo_config.validate)

        setattr(self.repo_config, "_repo", [
            dict(dbname="os_version_1"), dict(dbname="os_version_1")])
        self.assertEqual(False, self.repo_config.validate)

        setattr(self.repo_config, "_repo", [
            dict(dbname="os_version_1"), dict(dbname="")])
        self.assertEqual(False, self.repo_config.validate)

        setattr(self.repo_config, "_repo", [
            dict(dbname="os_version_1"), dict(dbname="openEuler20.09")])
        self.assertEqual(False, self.repo_config.validate)

    @mock.patch.object(RepoConfig, "_validate_priority")
    @mock.patch.object(RepoConfig, "_validate_database")
    def test_repo_file_path_error(self, mock__validate_database, mock__validate_priority):
        """The file path is not configured correctly"""
        mock__validate_database.return_value = None
        mock__validate_priority.return_value = None
        setattr(self.repo_config, "_repo", [""])
        self.assertEqual(False, self.repo_config.validate)

        setattr(self.repo_config, "_repo", [dict()])
        self.assertEqual(False, self.repo_config.validate)

        setattr(self.repo_config, "_repo", [dict(src_db_file="os_version_1-src")])
        self.assertEqual(False, self.repo_config.validate)

        setattr(self.repo_config, "_repo", [dict(src_db_file="http://127.0.0.1:5000/repo",
                                                 bin_db_file="")])
        self.assertEqual(False, self.repo_config.validate)

    @mock.patch.object(RepoConfig, "_validate_database")
    def test_repo_priority_error(self, mock__validate_database):
        """database priority error"""
        mock__validate_database.return_value = None
        setattr(self.repo_config, "_repo", [""])
        self.assertEqual(False, self.repo_config.validate)

        setattr(self.repo_config, "_repo", [dict(dbname="os_version_1")])
        self.assertEqual(False, self.repo_config.validate)

        setattr(self.repo_config, "_repo", [dict(priority="os_version_1")])
        self.assertEqual(False, self.repo_config.validate)

        setattr(self.repo_config, "_repo", [dict(priority=-1)])
        self.assertEqual(False, self.repo_config.validate)

        setattr(self.repo_config, "_repo", [dict(priority=1.5)])
        self.assertEqual(False, self.repo_config.validate)

    def test_validate_failed(self):
        """validate failed"""
        setattr(self.repo_config, "_repo", [
                dict(dbname="os_version_1", priority=1)])
        self.assertEqual(False, self.repo_config.validate)
        self.assertIsNotNone(self.repo_config.message)
        for repo in self.repo_config:
            self.assertIsNotNone(repo)
        setattr(self.repo_config, "_repo", [
                dict(database="os_version_1", priority=1)])
        self.assertEqual(False, self.repo_config.validate)
