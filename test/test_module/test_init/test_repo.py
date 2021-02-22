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
from unittest import mock
from packageship.application.initialize.repo import RepoFile
from packageship.application.common.compress import Unpack


class TestRepoFile(unittest.TestCase):
    """test repo file"""

    repo_file = RepoFile()

    def test_repo_init(self):
        """Create a temporary directory on initialization"""
        if os.path.exists("/tmp/testrepo"):
            shutil.rmtree("/tmp/testrepo")
        RepoFile(temporary_directory="/tmp/testrepo")
        self.assertEqual(True, os.path.exists("/tmp/testrepo"))
        shutil.rmtree("/tmp/testrepo")

    def test_create_exits_folder(self):
        """Create an existing folder"""
        if not os.path.exists("/tmp/testrepo"):
            os.makedirs("/tmp/testrepo")

        RepoFile(temporary_directory="/tmp/testrepo")
        shutil.rmtree("/tmp/testrepo")

    @mock.patch.object(os, "makedirs")
    def test_create_folder_error(self, mock_makedirs):
        """ test create folder error"""
        if os.path.exists("/tmp/testrepo"):
            shutil.rmtree("/tmp/testrepo")
        mock_makedirs.side_effect = IOError()
        with self.assertRaises(IOError):
            RepoFile(temporary_directory="/tmp/testrepo")

    def test_not_path_param(self):
        """There is no path parameter"""
        with self.assertRaises(KeyError):
            RepoFile.files()

    def test_path_isnone(self):
        """Path value of none"""
        with self.assertRaises(ValueError):
            RepoFile.files(path=None)

    def test_path_not_found(self):
        """The remote file path does not exist"""
        with self.assertRaises(FileNotFoundError):
            RepoFile.files(path="https://127.0.0.1")
        self.assertEqual(None, RepoFile.files(path="/etc/pkgship"))

    @mock.patch.object(RepoFile, "_extract_file_path")
    def test_remote_file_not_found(self, mock__extract_file_path):
        """The remote file does not exist"""
        with self.assertRaises(ValueError):
            self.repo_file.remote_file(path=None)
        mock__extract_file_path.return_value = "http://127.0.0.1"
        with self.assertRaises(FileNotFoundError):
            self.repo_file.remote_file(path="http://127.0.0.1")

    @mock.patch.object(RepoFile, "_extract_file_path")
    def test_save_remote_file_failed(self, mock__extract_file_path):
        """Failed to save the remote file"""
        mock__extract_file_path.return_value = "http://127.0.0.1/repo.sqlite"
        with mock.patch("packageship.application.common.remote.RemoteService.status_code",
                        new_callable=mock.PropertyMock) as mock_status_code:

            mock_status_code.return_value = 200
            with mock.patch("packageship.application.common.remote.RemoteService.content",
                            new_callable=mock.PropertyMock) as mock_content:
                mock_content.return_value = "openeuler".encode("utf-8")
                with self.assertRaises(FileNotFoundError):
                    self.repo_file.remote_file(path="http://127.0.0.1")
            with self.assertRaises(FileNotFoundError):
                self.repo_file.remote_file(path="http://127.0.0.1")

    def test_location_file_not_path(self):
        """The local file path parameter is incorrect"""
        with self.assertRaises(ValueError):
            self.repo_file.location_file(path=None)

    def test_location_file_not_regex(self):
        """Incorrect local file path match"""
        self.assertEqual(None, self.repo_file.location_file(path="openeuler"))

    @mock.patch.object(Unpack, "dispatch")
    @mock.patch.object(shutil, "copyfile")
    @mock.patch("re.match", new_callable=mock.PropertyMock)
    @mock.patch("os.path.isfile", new_callable=mock.PropertyMock)
    @mock.patch.object(os, "listdir")
    def test_unzip_file(self, mock_listdir, mock_isfile, mock_match, mock_copyfile, mock_dispath):
        """unzip file"""
        mock_dispath.return_value = ""
        path = "/etc/test_unzip_file.bz2"
        if not os.path.exists(path):
            fd = open(path, mode="w", encoding="utf-8")
            fd.close()
        mock_listdir.return_value = ["/etc/test_unzip_file.bz2"]
        mock_copyfile.return_value = ""
        mock_isfile.return_value = True
        mock_match.return_value = True

        self.assertNotEqual(None, self.repo_file.location_file(
            path="file:///etc/test_unzip_file.bz2"))

    @mock.patch.object(RepoFile, "_location")
    def test_location_file(self, mock__location):
        """local file"""
        mock__location.return_value = "/openeuler/repo"
        with self.assertRaises(FileNotFoundError):
            self.repo_file.location_file(path="openeuler")
        with mock.patch.object(RepoFile, "_unzip_file") as mock__unzip_file:
            mock__unzip_file.return_value = "/openeuler/repo"
            self.assertEqual("/openeuler/repo",
                             self.repo_file.location_file(path="openeuler"))

    def test_extract_file_path(self):
        """Remote file matching"""
        with mock.patch("packageship.application.common.remote.RemoteService.status_code",
                        new_callable=mock.PropertyMock) as mock_status_code:
            mock_status_code.return_value = 200
            with mock.patch("packageship.application.common.remote.RemoteService.text",
                            new_callable=mock.PropertyMock) as mock_text:
                mock_text.return_value = "openeuler"
                with self.assertRaises(FileNotFoundError):
                    self.repo_file.remote_file(
                        path="openeuler", file_type="primary")
                mock_text.return_value = 'href="https://openeuler/src.primary.sqlite.bz2"'
                mock_status_code.side_effect = [200, 200, 404]
                with self.assertRaises(FileNotFoundError):
                    self.repo_file.remote_file(
                        path="openeuler", file_type="primary")

    @mock.patch.object(shutil, "copyfile")
    @mock.patch("re.match", new_callable=mock.PropertyMock)
    @mock.patch("os.path.isfile", new_callable=mock.PropertyMock)
    @mock.patch.object(os, "listdir")
    def test_find_local_file(self, mock_listdir, mock_isfile, mock_match, mock_copyfile):
        """Local qualified file lookup"""
        mock_listdir.return_value = ["/etc/1.sqlite"]
        mock_copyfile.return_value = ""
        mock_isfile.return_value = True
        mock_match.return_value = True
        with self.assertRaises(FileNotFoundError):
            self.repo_file.location_file(path="file:///etc")
