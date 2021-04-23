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
Package information CSV file download unit test
"""
import json
import zipfile
from io import BytesIO
from pathlib import Path
from packageship.application.core.depend.down_load import Download
from test.cli import DATA_BASE_INFO
from test.cli.download_csv import DownloadPackageTestBase

MOCK_DATA_FOLDER = Path(Path(__file__).parent, "mock_data")


class TestBinPackageDownload(DownloadPackageTestBase):

    def test_all_bin_csv(self):
        """
        All binary package information is downloaded
        """
        parameter = {
            "depend_type": "bin",
            "parameter": {
                "db_priority": ["os-version"]
            }
        }
        self.mock_es_search(return_value=DATA_BASE_INFO)
        self.mock_es_scan(return_value=self.read_file_content("pkg_list.json"),
                          folder=MOCK_DATA_FOLDER)
        folder_path = Download().process_packages(
            parameter["depend_type"], parameter["parameter"]["db_priority"][0])
        bin_package = "bin_package_csv"
        csv_folder_path = self.get_csv_file_path(bin_package)
        self.comparison_data(csv_folder_path, folder_path)

    def test_all_src_csv(self):
        """
        All source package information is downloaded
        """
        parameter = {
            "depend_type": "src",
            "parameter": {
                "db_priority": ["os-version"]
            }
        }
        self.mock_es_search(return_value=DATA_BASE_INFO)
        self.mock_es_scan(return_value=self.read_file_content("pkg_list_s.json"),
                          folder=MOCK_DATA_FOLDER)
        folder_path = Download().process_packages(
            parameter["depend_type"], parameter["parameter"]["db_priority"][0])
        bin_package = "src_package_csv"
        csv_folder_path = self.get_csv_file_path(bin_package)
        self.comparison_data(csv_folder_path, folder_path)

    def test_all_process_package(self):
        """
        Test the overall process
        """
        parameter = {
            "depend_type": "src",
            "parameter": {
                "db_priority": ["os-version"]
            }
        }
        response = self.client.post(
            "/dependinfo/downloadfiles", data=json.dumps(parameter), content_type="application/json")
        self.assertIsInstance(response.content, cls=bytes)
