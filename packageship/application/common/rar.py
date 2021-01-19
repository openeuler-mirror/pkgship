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
import lzma
import bz2
import gzip
import tarfile
import zipfile


class Unpack:
    """Decompression of documents"""

    def __init__(self, file_path, save_file):
        self.file_path = file_path
        self.save_file = save_file

    @classmethod
    def dispatch(cls, extend, *args, **kwargs):
        """Specific decompression methods are adopted for different compression packages

        :param extend: Suffixes for compression packs (representing compression mode)
        :param kwargs.file_path: path to the zip file
        :param kwargs.save_file: path to the file saved after unzipping
        """
        self = cls(*args, **kwargs)
        meth = getattr(self, extend[1:].lower(), None)
        if meth is None:
            raise IOError(
                "Unzipping files in the current format is not supported：%s" % extend)
        meth()

    def bz2(self):
        """Unzip the bZ2 form of the compression package"""
        with open(self.save_file, 'wb') as file, bz2.BZ2File(self.file_path, 'rb') as bz_file:
            for data in iter(lambda: bz_file.read(100 * 1024), b''):
                file.write(data)

    def gz(self):
        """Unzip the compressed package in GZIP format"""
        with open(self.save_file, 'wb') as file, gzip.GzipFile(self.file_path) as gzip_file:
            for data in iter(lambda: gzip_file.read(100 * 1024), b''):
                file.write(data)

    def tar(self):
        """Unzip the tar package"""
        with open(self.save_file, 'wb') as file, tarfile.open(self.file_path) as tar_file:
            file_names = tar_file.getnames()
            if len(file_names) != 1:
                raise IOError(
                    "Too many files in the zip file, do not"
                    " conform to the form of a single file：%s" % self.file_path)
            _file = tar_file.extractfile(file_names[0])
            for data in iter(lambda: _file.read(100 * 1024), b''):
                file.write(data)

    def zip(self):
        """Unzip the zip package"""
        with open(self.save_file, 'wb') as file, zipfile.open(self.file_path) as zip_file:
            file_names = zip_file.namelist()
            if len(file_names) != 1:
                raise IOError("Too many files in the zip file, do not"
                              " conform to the form of a single file：%s" % self.file_path)
            file.write(zip_file.read())

    def xz(self):
        """Decompression of xz type files"""
        with open(self.save_file, 'wb') as file, lzma.open(self.file_path) as xz_file:
            for data in iter(lambda: xz_file.read(100 * 1024), b''):
                file.write(data)
