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
"""
Depends on the CSV file download
"""
from packageship.application.core.depend import DispatchDepend
from test.cli.download_csv import DownloadDeppendTestBase


class TestSelfdepDownload(DownloadDeppendTestBase):
    binary_file = "os-version-binary.json"
    component_file = "os-version-binary-component.json"
    source_file = "os-version-source.json"
    package_source_file = "os-version-source-package.json"

    def test_selfbuild_download_package(self):
        """
        The selfbep CSV to download the unit tests,No redundant parameters
        """
        parameter = {"packagename": ["Judy"],
                     "depend_type": "selfdep",
                     "parameter": {}
                     }
        result, error = self.validate_data(parameter)
        depend = DispatchDepend.execute(**result)
        folder_path = depend.download_depend_files()
        scv_depend = "selfdep_Judy_package"
        csv_folder_path = self.get_csv_file_path(scv_depend)
        self.comparison_data(csv_folder_path, folder_path)

    def test_selfbuild_download_package_db(self):
        """
        The selfbep CSV to download the unit tests, Specified database
        """
        parameter = {"packagename": ["Judy"],
                     "depend_type": "selfdep",
                     "parameter": {
                         "db_priority": ["os-version"]
                     }
                     }
        result, error = self.validate_data(parameter)
        depend = DispatchDepend.execute(**result)
        folder_path = depend.download_depend_files()
        csv_depend = "selfdep_Judy_package_db"
        csv_folder_path = self.get_csv_file_path(csv_depend)
        self.comparison_data(csv_folder_path, folder_path)

    def test_selfbuild_download_package_source_db(self):
        """
        The selfbep CSV to download the unit tests,
        Specified database
        """
        parameter = {"packagename": ["Judy"],
                     "depend_type": "selfdep",
                     "parameter": {
                         "db_priority": ["os-version"],
                         "packtype": "source"
                     }
                     }
        result, error = self.validate_data(parameter)
        depend = DispatchDepend.execute(**result)
        folder_path = depend.download_depend_files()
        csv_depend = "selfdep_Judy_package_source_db"
        csv_folder_path = self.get_csv_file_path(csv_depend)
        self.comparison_data(csv_folder_path, folder_path)

    def test_selfbuild_download_package_source_db_self(self):
        """
        The selfbep CSV to download the unit tests,
        Specified database
        """
        parameter = {"packagename": ["Judy"],
                     "depend_type": "selfdep",
                     "parameter": {
                         "db_priority": [
                             "os-version"
                         ],
                         "self_build": True
                     }
                     }
        result, error = self.validate_data(parameter)
        depend = DispatchDepend.execute(**result)
        folder_path = depend.download_depend_files()
        csv_depend = "selfdep_Judy_package_source_db_self"
        csv_folder_path = self.get_csv_file_path(csv_depend)
        self.comparison_data(csv_folder_path, folder_path)
