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
"""
Initialize the configuration source service
"""
import re
import os
import random
import shutil
import requests
from packageship.libs.conf import configuration
from packageship.application.common.exc import UnpackError
from ..common.rar import Unpack
from ..common.remote import RemoteService


class RepoFile:
    """
    Get and unzip the REPO source file

    Attributes:
        _temporary_directory: temporary directory
    """

    def __init__(self, temporary_directory=None):
        self._temporary_directory = temporary_directory or configuration.TEMPORARY_DIRECTORY
        try:
            if not os.path.exists(self._temporary_directory):
                os.makedirs(self._temporary_directory)
        except IOError as error:
            raise IOError("Failed to create temporary folder %s ." %
                          self._temporary_directory) from error

    def _url(self, path):
        """
        Description: combination of REPo source addresses

        Args:
            path: repo path
        """
        if not path.endswith('/'):
            path += '/'
        return path + 'repodata/'

    @classmethod
    def files(cls, **kwargs):
        """
        Description: Get repo file

        Args:
            repo_type: The types of repr sources are divided into local and remote repo forms
                If it is a local REPO source, the value is location
                If it is a remote REPO source, the value is remote
        """
        def repofile(path):
            if re.match(r"^(ht|f)tp(s?)", path):
                return "remote"
            return "location"
        if "path" not in kwargs:
            raise KeyError("The required path parameter is missing")
        if not kwargs["path"]:
            raise ValueError("The value of path cannot be null")
        repo = cls()
        method = getattr(repo, repofile(kwargs["path"]) + "_file")
        return method(**kwargs)

    def remote_file(self, path, file_type="primary"):
        """
        Description: Get remote files, provide download, unzip

        Args:
            path: remote repo path
            file_type: The suffix type of the file is classified as primary or filelist
        Returns:
            Unzip the new file path
        """
        if not path:
            raise ValueError("The value of path cannot be null")
        remote_url = self._extract_file_path(self._url(path), file_type)
        if not remote_url:
            raise FileNotFoundError("file not fuound")
        request = RemoteService()
        request.request(remote_url, "get")
        if request.status_code != requests.codes["ok"]:
            raise FileNotFoundError("file not fuound")
        try:
            _file_path = os.path.join(
                self._temporary_directory, remote_url.split('/')[-1])
            with open(_file_path, "wb") as file:
                file.write(request.content)
            return self._unzip_file(_file_path)
        except (IOError, TypeError) as error:
            raise FileNotFoundError(error) from error

    def _location(self, url, regex):
        """
        Description: Gets the files that the local REPO source meets and
                     puts them in a temporary folder

        Args:
            url: The file path of the local repo source
            regex: A regular expression for a specific file name
        Returns:
            Files in a temporary directory
        """
        file_path = None
        try:
            list_dir = os.listdir(url)
        except (FileNotFoundError, NotADirectoryError):
            return file_path
        for file in list_dir:
            if os.path.isfile(os.path.join(url, file)) and re.match(regex, file):
                file_path = os.path.join(self._temporary_directory, file)
                shutil.copyfile(os.path.join(url, file), file_path)
                break
        return file_path

    def location_file(self, path, file_type="primary"):
        """
        Description: Unzip the local REPO source file to get the readable file

        Args:
            path: Local repo path
            file_type: The suffix type of the file is classified as primary or filelist
        Returns:
            Unzip the new file path
        """
        # A file that matches the end of a particular character
        if not path:
            raise ValueError("The value of path cannot be null")
        regex = r'.*?%s.sqlite.{3,4}' % file_type
        path = path.split('file://')[-1]
        try:
            file_path = self._location(self._url(path), regex)
            if not file_path:
                return file_path
            file_path = self._unzip_file(file_path)
        except (FileNotFoundError, IOError) as error:
            raise FileNotFoundError(error) from error

        return file_path

    def _unzip_file(self, path):
        """
        Description: Decompression of files

        Args:
            path: The path of the compression package
        """
        name = str(random.getrandbits(128))
        if not os.path.exists(path):
            raise FileNotFoundError("The unzip file does not exist：%s" % path)

        sqlite_file = os.path.join(
            os.path.dirname(path), name + ".sqlite")
        try:
            Unpack.dispatch(os.path.splitext(path)[-1], file_path=path,
                            save_file=sqlite_file)
            return sqlite_file
        except (UnpackError, IOError, ValueError) as error:
            raise IOError("An error occurred extracting the file .") from error
        finally:
            os.remove(path)

    def _extract_file_path(self, url, file_type):
        """
        Description: Extract the path to the remote file download

        Args:
            url: repo source for remote files
            file_type: matching file type
        Returns:
            the actual path to download the file
        """
        file_regex = r'href=\"([^\"]*%s.sqlite.{3,4})\".?' % file_type
        request = RemoteService()
        request.request(url, "get")
        if request.status_code != requests.codes["ok"]:
            return None
        result = re.search(file_regex, request.text)
        if not result:
            return None
        remote_url = url + result.group(1)
        return remote_url
