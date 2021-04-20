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
Download the CSV unit test base class
"""
import csv
import os
import shutil
import unittest
from packageship.application.serialize import validate
from packageship.application.serialize.dependinfo import DownSchema
from packageship.libs.conf import configuration
from test.cli.depend_commands import DependTestBase

from test.cli.package_command import PackageTestBase


class DownloadTestBase(unittest.TestCase):
    """
    DownloadTestBase
    """
    temporary_csv_path = os.path.join(
        os.path.dirname(__file__), "csv_data", "tmp")
    local_csv_path = os.path.join(os.path.dirname(__file__), "csv_data")

    def delete_folder_path(self):
        """
        Delete the query folder
        Args:
            folder_path: Folder path

        Returns:
            None
        """
        try:
            if self.temporary_csv_path and os.path.exists(
                    self.temporary_csv_path):
                shutil.rmtree(self.temporary_csv_path)
        except (OSError, IOError) as error:
            return

    def get_csv_file_path(self, depend_path):
        """
        Gets the path of the local CSV query folder
        Args:
            depend_path: Dependent folder path

        Returns:
            None
        """

        csv_folder_path = os.path.join(self.local_csv_path, depend_path)
        return csv_folder_path

    def _compare_the_data(self, column_actual, column_expected):
        """
        Compare data from a CSV file
        Args:
            column_actual: Actual data
            column_expected: expected data

        Returns:
            True or False
        """
        result_one = list(set([i[0] for i in column_actual]).difference(
            set([i[0] for i in column_expected])))
        if result_one:
            return False
        return True

    def comparison_data(self, csv_folder_path, folder_path):
        """
        Read the data from the CSV file and call a function to compare the data
        Args:
            csv_folder_path: The correct address to store the data
            folder_path: The address of the generated data

        Returns:
            None
        """
        for file in os.listdir(folder_path):
            with open(os.path.join(folder_path, file), "r", encoding="utf-8") as csv_content:
                cvs_reader = csv.reader(csv_content)
                column_actual = [row for row in cvs_reader]
            with open(os.path.join(self.temporary_csv_path, csv_folder_path, file), "r",
                      encoding="utf-8") as csv_content:
                cvs_reader = csv.reader(csv_content)
                column_expected = [row for row in cvs_reader]
            result = self._compare_the_data(column_actual, column_expected)
            self.assertEqual(result, True)

    def validate_data(self, parameter):
        """
        Validate parameter
        Args:
            parameter: parameter

        Returns:
            result: The data after validation
            error: The error information
        """
        result, error = validate(DownSchema, parameter, load=True)
        return result, error


class DownloadDeppendTestBase(DependTestBase, DownloadTestBase):
    """
    DownloadDeppendTestBase
    """

    def setUp(self):
        super(DownloadDeppendTestBase, self).setUp()
        configuration.TEMPORARY_DIRECTORY = self.temporary_csv_path

    def tearDown(self) -> None:
        configuration.TEMPORARY_DIRECTORY = "/opt/pkgship/tmp/"
        self.delete_folder_path()


class DownloadPackageTestBase(PackageTestBase, DownloadTestBase):
    """
    DownloadPackageTestBase
    """

    def setUp(self):
        super(DownloadPackageTestBase, self).setUp()
        configuration.TEMPORARY_DIRECTORY = self.temporary_csv_path

    def tearDown(self) -> None:
        configuration.TEMPORARY_DIRECTORY = "/opt/pkgship/tmp/"
        self.delete_folder_path()
