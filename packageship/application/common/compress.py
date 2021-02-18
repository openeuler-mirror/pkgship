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
import os
import lzma
import bz2
import gzip
import tarfile
import zipfile
from packageship.libs.conf import configuration
from packageship.application.common.exc import UnpackError


class Unpack:
    """
    Decompression of documents

    Attributes:
        file_path:Compressed package file
        save_file:The saved file after unzipping
    """

    def __init__(self, file_path, save_file):
        self.file_path = file_path
        self.save_file = save_file

    @classmethod
    def dispatch(cls, extend, *args, **kwargs):
        """
        Description: Specific decompression methods are adopted for different compression packages

        Args:
            extend: Suffixes for compression packs (representing compression mode)
            kwargs.file_path: path to the zip file
            kwargs.save_file: path to the file saved after unzipping
        """
        if "file_path" not in kwargs or "save_file" not in kwargs:
            raise TypeError(
                "missing 2 required positional arguments: 'file_path' and 'save_file' .")

        self = cls(*args, **kwargs)
        meth = getattr(self, "_" + extend[1:].lower(), None)
        if meth is None:
            raise UnpackError(
                "Unzipping files in the current format is not supported：%s" % extend)
        if not all([self.file_path, self.save_file]):
            raise ValueError(
                "'file_path' and 'save_file' values cannot be empty")
        meth()

    def _write(self, file, handle):
        """
        Description: Read the file and write

        Args:
            file:Handle to the saved file
            handle:Compress the file handle
        """
        for data in iter(lambda: handle.read(100 * 1024), b''):
            file.write(data)

    def _bz2(self):
        """
        Description: Unzip the bZ2 form of the compression package

        """
        try:
            with open(self.save_file, 'wb') as file, bz2.BZ2File(self.file_path, 'rb') as bz_file:
                self._write(file, bz_file)
        except OSError as error:
            raise UnpackError(
                "Invalid data stream, %s file is not properly formatted ." %
                self.file_path) from error

    def _gz(self):
        """
        Description: Unzip the compressed package in GZIP format

        """
        try:
            with open(self.save_file, 'wb') as file, gzip.GzipFile(self.file_path) as gzip_file:
                self._write(file, gzip_file)
        except gzip.BadGzipFile as error:
            raise UnpackError("Not a gzipped file :%s" %
                              self.file_path) from error

    def _tar(self):
        """
        Description: Unzip the tar package

        """
        try:
            tar_file = tarfile.open(self.file_path)
        except tarfile.ReadError as error:
            raise IOError("The file '%s'  is not a proper tar file ." %
                          self.file_path) from error

        with open(self.save_file, 'wb') as file:
            file_names = tar_file.getnames()
            if len(file_names) != 1:
                raise IOError(
                    "Too many files in the zip file, do not"
                    " conform to the form of a single file：%s" % self.file_path)
            self._write(file, tar_file.extractfile(file_names[0]))

        tar_file.close()

    def _zip(self):
        """
        Description: Unzip the zip package

        """
        if not zipfile.is_zipfile(self.file_path):
            raise IOError(
                "The file '%s' is not a correct ZIP packet ." % self.file_path)

        with open(self.save_file, 'wb') as file, zipfile.ZipFile(self.file_path) as zip_file:
            file_names = zip_file.namelist()
            if len(file_names) != 1:
                raise IOError("Too many files in the zip file, do not"
                              " conform to the form of a single file：%s" % self.file_path)
            try:
                if not os.path.exists(configuration.TEMPORARY_DIRECTORY):
                    os.makedirs(configuration.TEMPORARY_DIRECTORY)
            except IOError as error:
                raise IOError("Failed to create temporary folder %s ." %
                              configuration.TEMPORARY_DIRECTORY) from error
            else:

                temporary_extract_file = os.path.join(
                    configuration.TEMPORARY_DIRECTORY, file_names[0])
                zip_file.extract(
                    file_names[0], configuration.TEMPORARY_DIRECTORY)
                _zip_handle = open(temporary_extract_file, 'rb')
                self._write(file, _zip_handle)
                _zip_handle.close()
                os.remove(temporary_extract_file)

    def _xz(self):
        """
        Description: Decompression of xz type files

        """
        try:
            with open(self.save_file, 'wb') as file, lzma.open(self.file_path) as xz_file:
                self._write(file, xz_file)
        except lzma.LZMAError as error:
            raise UnpackError("The file '%s' is not a correct xz format ." %
                              self.file_path) from error
