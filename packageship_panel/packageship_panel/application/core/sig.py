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
Query sig information and write data to csv file
"""
import csv
import os
import stat

from packageship_panel.application.core import ExportBase
from packageship_panel.application.query.panel import PanelInfo

from packageship.application.common.constant import OPENEULER_URL_TEST


class SigInfo(ExportBase):
    """
    Query sig information and write data to csv file
    """

    def __init__(self):
        super().__init__()
        self._panel_info = PanelInfo()

    def sig_infos(self, sig_name=None):
        """
        Get all sig group information
        Args:
            sig_name : sig name  Defaults to None.

        Returns:
           sig_infos : All sig information, or specific sig information
        """
        return self._panel_info.query_sig_info(sig_name=sig_name, index="sig_info")

    def sig_infos_csv(self):
        """
        Write data to local csv file
        Returns:
            folder_path: path to folder
        """
        self.create_folder_path()
        sig_path = os.path.join(self.folder_path, "sig.csv")
        sig_infos = self.sig_infos()
        flags = os.O_RDWR | os.O_CREAT
        modes = stat.S_IWUSR | stat.S_IRUSR
        with os.fdopen(os.open(sig_path, flags, modes), "a+", encoding="utf-8", newline="") as sig_csv:
            sig_csv_writer = csv.writer(sig_csv)
            sig_csv_writer.writerow(["sig名称", "描述", "maintainer", "contributors", "所属软件包"])
            for sig_info in sig_infos:
                sig_csv_writer.writerow(
                    [
                        sig_info.get("name", ""),
                        sig_info.get("description", ""),
                        self.parse_owners_maintainers(sig_info.get("maintainer", [])),
                        self.parse_owners_maintainers(sig_info.get("contributors", [])),
                        "{}sig-detail?sig_name={}".format(OPENEULER_URL_TEST, sig_info.get("name", "")),
                    ]
                )
        return self.folder_path
