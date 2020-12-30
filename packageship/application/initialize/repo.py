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


class RepoFile:

    def remote_file(self, path, name, file_type="primary", full_path=False):
        """
            get remote files, download and decompress those files
            :param path: remote files path
            :param name: file's name after unzip
            :param file_type: files type, source/binary
            :full_path: absolute path
            :return: the path for saving tmp file after unzip
        """
        pass

    def location_file(self, path, name, file_type="primary"):
        """
            get unzip file in local
            :param path: local path
            :param name: file's name after unzip
            :param file_type: files type, source/binary
            :return: the path for saving tmp file after unzip
        """
        pass

    def _unzip_file(self, path, name):
        """
            upzip file
            :param path: zip file's path
            :param name: new name after unzip
        """
        pass

    def extract_file_path(self, url):
        """
            get download path
            :param url: remote file url path
            :return: download path
        """
        pass
