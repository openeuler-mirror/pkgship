# !/usr/bin/python3
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
File export base class
"""
import csv
import os
import shutil
import uuid
from packageship.libs.conf import configuration


class ExportBase:
    """
    File export base class
    """

    def __init__(self):
        """
        initialization class
        """
        # temporary folder path
        self.folder_path = ""
        self.csv_list = list()

    @staticmethod
    def ternary_comparison(content):
        """
        returns the original content if the ternary expression
        exists or returns an empty string if it does not exist
        Args:
            content: data to be judged

        Returns:
            content: data after judgment
        """
        return content if content else ""

    @staticmethod
    def copy_file(template_path, csv_path):
        """
        Copy the template file to the specified path
        Args:
            template_path: csv template file path
            csv_path: specify the location path
        """
        shutil.copy(template_path, csv_path)

    @staticmethod
    def _template_csv_path(template_csv_name):
        """
        temporary folder path
        Args:
            template_csv_name: csv template file name

        Returns:
            absolute path to the csv template file
        """

        return os.path.join(os.path.abspath(os.path.dirname(__file__)),
                            template_csv_name)

    def parse_owners_maintainers(self, contents):
        """

        Args:
            contents (_type_): _description_

        Returns:
            _type_: _description_
        """
        infos = list()
        for content in contents:
            infos.append(self.ternary_comparison(content.get("id")))
            infos.append(self.ternary_comparison(content.get("email")))
            infos.append(self.ternary_comparison(content.get("orgnization")))
            infos.append("\n")
        return " ".join(infos) if infos else ""

    def create_folder_path(self):
        """
        Create a temporary folder
        """
        self.folder_path = os.path.join(configuration.TEMPORARY_DIRECTORY,
                                        str(uuid.uuid1().hex))
        if not os.path.exists(self.folder_path):
            os.makedirs(self.folder_path)

    def cve_content_list(self, filename):
        """
        Read csv file data, convert to list
        Args:
            filename: csv file name

        Returns:
            csv_list: csv file data
        """
        with open(filename, "r", encoding="utf-8") as fp:
            self.csv_list = list(csv.reader(fp))
        return self.csv_list

    def list_save_csv(self, file_path):
        """
        save data to csv
        Args:
            file_path: file path
        """
        with open(file_path, "w", newline="", encoding="utf-8") as sig_csv:
            sig_csv_writer = csv.writer(sig_csv)
            for sig_info in self.csv_list:
                sig_csv_writer.writerow(sig_info)

    def modify_content_list(self, row, column, info):
        """
        Change the data in a cell
        Args:
            row: the row of the cell
            column: the column of the cell
            info: info
        """
        self.csv_list[row - 1][column - 1] = info

    def insert_row(self, row):
        """
        Insert data into the row of the cell
        Args:
            row: the row of the cell
        """
        self.csv_list.insert(row - 1, [])

    def insert_col(self, row, column, value):
        """
        Insert into cell at row N and column M
        Args:
            row: the row of the cell
            column: the column of the cell
            value: value
        """
        # If the cell to the left of the cell is empty,
        # write a space to the cell to the left first
        if len(self.csv_list[row - 1]) < column:
            for _ in range(len(self.csv_list[row - 1]), column - 1):
                self.csv_list[row - 1].append("")
            self.csv_list[row - 1].append(value)
        else:
            self.modify_content_list(row, column, value)
