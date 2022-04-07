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
import shutil
from test.cli.init_command import InitTestBase
from packageship.application.initialize.repo import RepoFile


class RemoteFiles(InitTestBase):
    """Exception testing for database priority"""
    _dirname = os.path.dirname(__file__)

    def setUp(self):
        super(RemoteFiles, self).setUp()
        self.repo_file = RepoFile(temporary_directory=os.path.join(
            self._dirname, "tmp"))
        if "gevent.monkey" in sys.modules:
            del sys.modules["gevent.monkey"]

    def _get_repo_file_path(self, repo):
        _src_db_file = self.repo_file.remote_file(path=repo["src_db_file"])
        _bin_db_file = self.repo_file.remote_file(path=repo["bin_db_file"])
        _file_list = self.repo_file.remote_file(
            path=repo["bin_db_file"], file_type="filelists")

        return (_src_db_file, _bin_db_file, _file_list)

    # def test_normal_files(self):
    #     """
    #     Normal zip package file
    #     """
    #     _repo_conf = {
    #         "dbname": "openeuler",
    #         "src_db_file": "https://repo.openeuler.org/openEuler-20.09/source",
    #         "bin_db_file": "https://repo.openeuler.org/openEuler-20.09/everything/aarch64",
    #         "priority": 1
    #     }
    #     self.assertEqual(True, all(self._get_repo_file_path(
    #         repo=_repo_conf)))

    # def test_not_exists_remote(self):
    #     """
    #     The remote address does not exist
    #     """
    #     _repo_conf = {
    #         "dbname": "openeuler",
    #         "src_db_file": "https://www.baidu.com/sources",
    #         "bin_db_file": "https://www.baidu.com/binary",
    #         "priority": 1
    #     }
    #     with self.assertRaises(FileNotFoundError):
    #         self._get_repo_file_path(repo=_repo_conf)

    def tearDown(self) -> None:
        folder = os.path.join(self._dirname, "tmp")
        shutil.rmtree(folder)
