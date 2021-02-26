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
Send file stream
"""

import os
import shutil
import zipfile
from io import BytesIO
from packageship.libs.log import LOGGER


class CompressIo():
    """
    Public methods for sending and deleting files
    """

    def _delete_file_path(self, folder_path):
        """
        Delete folder
        Args:
            folder_path: Folder path

        Returns:
            None
        """
        try:
            if folder_path and os.path.exists(folder_path):
                shutil.rmtree(folder_path)
        except (IOError, OSError) as error:
            LOGGER.error(error)
            raise IOError("Failed to delete folder")

    def _send_bytes_io(self, folder_path):
        """
        Send a compressed file
        Args:
            folder_path: The file path
        Returns:
            memory_file: File stream
        """
        file_list = os.listdir(folder_path)
        memory_file = BytesIO()
        with zipfile.ZipFile(memory_file, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for _file in file_list:
                with open(os.path.join(folder_path, _file), 'rb') as file_content:
                    zip_file.writestr(_file, file_content.read())
        memory_file.seek(0)
        return memory_file

    def send_memory_file(self, folder_path):
        """
        Main method of sending files
        Args:
            folder_path: The file path
        Returns:
            zip_file: File stream

        Raises:
            IOError: IOError
        """
        try:
            memory_file = self._send_bytes_io(folder_path)
            return memory_file
        except (OSError, IOError) as error:
            LOGGER.error(error)
            raise IOError("File sending failed")
        finally:
            self._delete_file_path(folder_path)
