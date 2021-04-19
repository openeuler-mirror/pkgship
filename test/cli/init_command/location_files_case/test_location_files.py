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
from test.cli.init_command import InitTestBase
from packageship.application.initialize.integration import del_temporary_file
from packageship.application.initialize.repo import RepoFile


class LocationFiles(InitTestBase):
    """Test the local configuration file"""
    _dirname = os.path.dirname(__file__)

    def setUp(self):
        super(LocationFiles, self).setUp()
        self.repo_file = RepoFile(temporary_directory=os.path.join(
            self._dirname, "tmp"))
        self._location_path = os.path.join(self._dirname, "sqlites")

    def _get_repo_file_path(self, repo):
        _src_db_file = self.repo_file.location_file(path=repo["src_db_file"])
        _bin_db_file = self.repo_file.location_file(path=repo["bin_db_file"])
        _file_list = self.repo_file.location_file(
            path=repo["bin_db_file"], file_type="filelists")

        return (_src_db_file, _bin_db_file, _file_list)

    def test_normal_location_files(self):
        """
        Normal zip package file
        """
        _repo_conf = {
            "dbname": "openeuler",
            "src_db_file": "file://" + os.path.join(self._location_path, "src"),
            "bin_db_file": "file://" + os.path.join(self._location_path, "bin"),
            "priority": 1
        }
        self.assertEqual(True, all(self._get_repo_file_path(
            repo=_repo_conf)))

    def test_not_exists_location(self):
        """
        The location file does not exist
        """
        _repo_conf = {
            "dbname": "openeuler",
            "src_db_file": "file:///home/test-openeuler/src",
            "bin_db_file": "file:///home/test-openeuler/bin",
            "priority": 1
        }
        self.assertEqual(False, all(self._get_repo_file_path(
            repo=_repo_conf)))

    def tearDown(self) -> None:
        folder = os.path.join(self._dirname, "tmp")
        del_temporary_file(path=folder, folder=True)
