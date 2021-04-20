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
Unit tests are downloaded by dependent CSV files
"""
from packageship.application.core.depend import DispatchDepend
from test.cli.download_csv import DownloadDeppendTestBase


class TestBedepDownload(DownloadDeppendTestBase):
    """
    TestBedepDownload
    """
    binary_file = "os-version-bedepend.json"
    source_file = "os-version-source-bedepend.json"

    def test_bedep_download_binary(self):
        """
        Test by dependent packages, which are binary packages
        """
        parameter = {"packagename": ["Judy"],
                     "depend_type": "bedep",
                     "parameter": {
                         "db_priority": ["os-version"]
                     }
                     }
        result, error = self.validate_data(parameter)
        depend = DispatchDepend.execute(**result)
        folder_path = depend.download_depend_files()
        scv_depend = "bedep_Judy_binary"
        csv_folder_path = self.get_csv_file_path(scv_depend)
        self.comparison_data(csv_folder_path, folder_path)

    def test_bedep_download_source(self):
        """
        Test by dependent packages, which are source package
        """
        parameter = {"packagename": ["Judy"],
                     "depend_type": "bedep",
                     "parameter": {
                         "db_priority": ["os-version"],
                         "packtype": "source"
                     }
                     }
        result, error = self.validate_data(parameter)
        depend = DispatchDepend.execute(**result)
        folder_path = depend.download_depend_files()
        scv_depend = "bedep_Judy_source"
        csv_folder_path = self.get_csv_file_path(scv_depend)
        self.comparison_data(csv_folder_path, folder_path)

    def test_bedep_download_source_install(self):
        """
        Test by dependent packages, which are source package
        """
        parameter = {"packagename": ["Judy"],
                     "depend_type": "bedep",
                     "parameter": {
                         "db_priority": ["os-version"],
                         "packtype": "source",
                         "search_type": "install"

                     }
                     }
        result, error = self.validate_data(parameter)
        depend = DispatchDepend.execute(**result)
        folder_path = depend.download_depend_files()
        scv_depend = "bedep_Judy_source_install"
        csv_folder_path = self.get_csv_file_path(scv_depend)
        self.comparison_data(csv_folder_path, folder_path)

    def test_bedep_download_source_withsubpack(self):
        """
        Test by dependent packages, which are source package
        """
        parameter = {"packagename": ["Judy"],
                     "depend_type": "bedep",
                     "parameter": {
                         "db_priority": ["os-version"],
                         "packtype": "source",
                         "search_type": "install",
                         "with_subpack": False

                     }
                     }
        result, error = self.validate_data(parameter)
        depend = DispatchDepend.execute(**result)
        folder_path = depend.download_depend_files()
        scv_depend = "bedep_Judy_source_install_with"
        csv_folder_path = self.get_csv_file_path(scv_depend)
        self.comparison_data(csv_folder_path, folder_path)
