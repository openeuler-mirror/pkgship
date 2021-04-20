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
The installdep CSV to download the unit tests
"""
from packageship.application.core.depend import DispatchDepend
from test.cli.download_csv import DownloadDeppendTestBase


class TestInstallDownload(DownloadDeppendTestBase):
    binary_file = "os-version-binary.json"
    component_file = "os-version-binary-component.json"

    def test_install_download_bin_level_0(self):
        """
        The installation depends on the download test,
        The database and query hierarchy are not specified
        """

        parameter = {"packagename": ["Judy"],
                     "depend_type": "installdep",
                     "parameter": {}
                     }
        result, error = self.validate_data(parameter)
        depend = DispatchDepend.execute(**result)
        folder_path = depend.download_depend_files()
        scv_depend = "installdep_Judy_level_0"
        csv_folder_path = self.get_csv_file_path(scv_depend)
        self.comparison_data(csv_folder_path, folder_path)


    def test_install_download_bin_level_2(self):
        """
        The installation depends on the download test,
        level is two
        """

        parameter = {"packagename": ["Judy"],
                     "depend_type": "installdep",
                     "parameter": {
                         "level": 2
        }
        }
        result, error = self.validate_data(parameter)
        depend = DispatchDepend.execute(**result)
        folder_path = depend.download_depend_files()
        scv_depend = "installdep_Judy_level_2"
        csv_folder_path = self.get_csv_file_path(scv_depend)
        self.comparison_data(csv_folder_path, folder_path)


    def test_install_download_bin_db_level_0(self):
        """
        The installation depends on the download test,
        Specify database, do not specify hierarchy
        """

        parameter = {"packagename": ["Judy"],
                     "depend_type": "installdep",
                     "parameter": {
                         "db_priority": ["os-version"]
        }
        }
        result, error = self.validate_data(parameter)
        depend = DispatchDepend.execute(**result)
        folder_path = depend.download_depend_files()
        scv_depend = "installdep_Judy_db_level_0"
        csv_folder_path = self.get_csv_file_path(scv_depend)
        self.comparison_data(csv_folder_path, folder_path)


    def test_install_download_bin_db_level_2(self):
        """
        The installation depends on the download test,
        Specifies the database, level is 2
        """

        parameter = {"packagename": ["Judy"],
                     "depend_type": "installdep",
                     "parameter": {
                         "db_priority": ["os-version"],
                         "level": 2
        }
        }
        result, error = self.validate_data(parameter)
        depend = DispatchDepend.execute(**result)
        folder_path = depend.download_depend_files()
        scv_depend = "installdep_Judy_db_level_2"
        csv_folder_path = self.get_csv_file_path(scv_depend)
        self.comparison_data(csv_folder_path, folder_path)

