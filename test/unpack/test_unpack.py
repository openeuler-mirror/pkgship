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
from unittest import mock, TestCase
from packageship.application.common.compress import Unpack
from packageship.application.common.exc import UnpackError
from packageship.libs.conf import configuration


class TestUnpack(TestCase):
    """File decompression test"""

    def setUp(self):
        self.path = os.path.join(os.path.dirname(__file__), "compress_files")
        configuration.TEMPORARY_DIRECTORY = self.path

    def test_bz2_unpack(self):
        """unpack bz2 file"""
        with self.assertRaises(UnpackError):
            Unpack.dispatch(".bz2", file_path=os.path.join(self.path, "bz2_error.txt"),
                            save_file=os.path.join(self.path, "bz2_unpack.sqlite"))

    def test_gz_unpack(self):
        """unpack gz file"""
        with self.assertRaises(UnpackError):
            Unpack.dispatch(".gz", file_path=os.path.join(self.path, "gz_error.txt"),
                            save_file=os.path.join(self.path, "bz2_unpack.sqlite"))

    def test_error_tar(self):
        """error tar file"""
        with self.assertRaises(IOError):
            Unpack.dispatch(".tar", file_path=os.path.join(self.path, "tar_error.txt"),
                            save_file=os.path.join(self.path, "bz2_unpack.sqlite"))

    def test_tar_unpack(self):
        """unpack tar file"""
        Unpack.dispatch(".tar", file_path=os.path.join(self.path, "test_tar.tar.gz"),
                        save_file=os.path.join(self.path, "bz2_unpack.sqlite"))

    def test_error_zip_unpack(self):
        """unpack error zip file"""
        file = os.path.join(self.path, "zip_error.txt")
        with open(file, "w", encoding="utf-8") as f:
            f.write("error zip file")
        with self.assertRaises(IOError):
            Unpack.dispatch(".zip", file_path=file,
                            save_file=os.path.join(self.path, "zip_file.sqlite"))
        if os.path.exists(file):
            os.remove(file)

    def test_zip_unpack(self):
        """unpack zip file"""

        self.assertEqual(None,
                         Unpack.dispatch(".zip", file_path=os.path.join(self.path, "zip_file.zip"),
                                         save_file=os.path.join(self.path, "zip_file.sqlite")))

    def test_xz_unpack(self):
        """unpack xz file"""
        with self.assertRaises(UnpackError):
            Unpack.dispatch(".xz", file_path=os.path.join(self.path, "xz_error.txt"),
                            save_file=os.path.join(self.path, "xz.sqlite"))

    def test_file_path_none(self):
        """unpack xz file"""

        with self.assertRaises(ValueError):
            Unpack.dispatch(".xz", file_path=None,
                            save_file=os.path.join(self.path, "xz.sqlite"))
        with self.assertRaises(ValueError):
            Unpack.dispatch(".xz", file_path=None, save_file=None)

    def test_dispatch_not_params(self):
        """not params"""
        with self.assertRaises(TypeError):
            Unpack.dispatch(".xz")

    def test_not_support(self):
        """Unsupported compression format"""
        with self.assertRaises(UnpackError):
            Unpack.dispatch(".rar", file_path=None, save_file=None)

    def test_unpack_file_is_none(self):
        """file path is empty"""
        with self.assertRaises(ValueError):
            Unpack.dispatch(".xz", file_path=None, save_file=None)

    @mock.patch.object(os.path, "exists")
    @mock.patch.object(os, "makedirs")
    def test_mkdir_error(self, mock_makedirs, mock_exists):
        """Folder creation error"""
        mock_exists.return_value = False
        mock_makedirs.side_effect = IOError("")
        with self.assertRaises(IOError):
            Unpack.dispatch(".zip", file_path=os.path.join(self.path, "zip_file.zip"),
                            save_file=os.path.join(self.path, "zip_file.sqlite"))

    def test_many_zip_file(self):
        """Multiple compressed files"""
        with self.assertRaises(IOError):
            Unpack.dispatch(".zip", file_path=os.path.join(self.path, "many-error.zip"),
                            save_file=os.path.join(self.path, "zip_file.sqlite"))

    def test_many_tar_file(self):
        """many tar file"""
        with self.assertRaises(IOError):
            Unpack.dispatch(".tar", file_path=os.path.join(self.path, "many-tar.tar.gz"),
                            save_file=os.path.join(self.path, "zip_file.sqlite"))

        with self.assertRaises(IOError):
            Unpack.dispatch(".tar", file_path=os.path.join(self.path, "many-tar.tar.gz"),
                            save_file=os.path.join(self.path, "zip_file.sqlite"))
