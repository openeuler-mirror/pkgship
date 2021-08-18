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
import os
import re
from lxml import etree
from packageship.application.initialize.base import ESJson

MAP = {
    "pkgKey": None,
    "pkgId": ".//default:checksum[@pkgid='YES']/text()",
    "name": ".//default:name/text()",
    "arch": ".//default:arch/text()",
    "version": ".//default:version/@ver",
    "epoch": ".//default:version/@epoch",
    "release": ".//default:version/@rel",
    "summary": ".//default:summary/text()",
    "description": ".//default:description/text()",
    "url": ".//default:url/text()",
    "time_file": ".//default:time/@file",
    "time_build": ".//default:time/@build",
    "rpm_license": ".//default:format/rpm:license/text()",
    "rpm_vendor": ".//default:format/rpm:vendor/text()",
    "rpm_group": ".//default:format/rpm:group/text()",
    "rpm_buildhost": ".//default:format/rpm:buildhost/text()",
    "rpm_sourcerpm": ".//default:format/rpm:sourcerpm/text()",
    "rpm_header_start": ".//default:format/rpm:header-range/@start",
    "rpm_header_end": ".//default:format/rpm:header-range/@end",
    "rpm_packager": ".//default:packager/text()",
    "size_package": ".//default:size/@package",
    "size_installed": ".//default:size/@installed",
    "size_archive": ".//default:size/@archive",
    "location_href": ".//default:location/@href",
    "location_base": ".//default:location/@base",
    "checksum_type": ".//default:checksum/@type",
}


class XmlPackage:
    """
    When the Repo source in Mainline is in XML format, the data
    is initialized by parsing the contents of the XML
    """

    def __init__(self, xml, filelist) -> None:
        if not xml or not filelist:
            raise ValueError("Pass in the path to the real, valid XML file .")

        if isinstance(xml, str):
            self._xml = [(xml, False)]
        else:
            self._xml = [(_xml, False) for _xml in xml]
        self._xml.append((filelist, True))

        self._element = None
        self._default_xmlns = "default"
        self._spkg_key = 0
        self._bpkg_key = 0
        self.xml_data = ESJson()
        self._bprovides = ESJson()
        self._brequires = ESJson()
        self._bfiles = ESJson()
        self._srequires = ESJson()
        self._filelist = ESJson()
