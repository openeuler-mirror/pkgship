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

    @property
    def _nsmap(self):
        if self._element is None:
            return {}
        nsmap = self._element.nsmap
        nsmap[self._default_xmlns] = nsmap[None]
        nsmap.pop(None)
        return nsmap

    def _xpath(self, xpath, element=None, first=True):
        if element is None:
            element = self._element
        try:
            node = element.xpath(xpath, namespaces=self._nsmap)
            if first:
                node = node[0]
            return node
        except (IndexError, TypeError):
            return None

    def _extract_info(self, filelist=False):

        if filelist:
            binary_pkg_name = self._xpath("./@name")
            self._filelist[binary_pkg_name] = list()
            for file in self._xpath(".//default:file", first=False):
                pkg_file = dict(file=self._xpath("./text()", element=file))
                if self._xpath("./@type", element=file):
                    pkg_file["filetype"] = "dir"
                else:
                    pkg_file["filetype"] = "file"

                self._filelist[binary_pkg_name].append(pkg_file)

        elif self._xpath(".//default:arch/text()") == "src":
            self._spkg_key += 1
            self._package(pkg_key=self._spkg_key)
        else:
            self._bpkg_key += 1
            self._package(pkg_key=self._bpkg_key, binary=True)

    def _fill_value(self, xml_data, val):
        if isinstance(xml_data, list):
            xml_data.append(val)
        else:
            xml_data = [val]
        return xml_data

    def _package(self, pkg_key, binary=False):
        package = dict()
        for field, xpath in MAP.items():
            if xpath is None:
                package[field] = str(pkg_key)
            else:
                package[field] = self._xpath(xpath)
        if binary:
            package["src_name"] = package.get("rpm_sourcerpm")
            self._binary_pkg(package)
        else:
            self._source_pkg(package)

    def _binary_pkg(self, package):
        self.xml_data["bin_pack"]["packages"][package["name"]] = package
        self.xml_data["bin_pack"]["pkg_key"][str(self._bpkg_key)] = package

        # The source package maps to the binary package
        if package["src_name"]:
            self.xml_data["bin_pack"]["sources"][
                package["src_name"]
            ] = self._fill_value(
                self.xml_data["bin_pack"]["sources"][package["src_name"]], package
            )

        # binary package requires
        for require in self._requires(self._spkg_key):
            self._brequires[require["name"]] = require

            self.xml_data["bin_requires"][str(self._spkg_key)] = self._fill_value(
                self.xml_data["bin_requires"][str(
                    self._spkg_key)], require["name"]
            )
            self.xml_data["bin_requires"][require["name"]] = self._fill_value(
                self.xml_data["bin_requires"][require["name"]], require["name"]
            )

        self._provides()

        self._files()

    def _source_pkg(self, package):
        # source packages
        self.xml_data["src_pack"][package["name"]] = package

        self.xml_data["src_pkgkeys"][str(self._spkg_key)] = package

        for require in self._requires(self._spkg_key):
            self._srequires[require["name"]] = require
            self.xml_data["src_requires"][str(self._spkg_key)] = self._fill_value(
                self.xml_data["src_requires"][str(
                    self._spkg_key)], require["name"]
            )

            self.xml_data["src_requires"][require["name"]] = self._fill_value(
                self.xml_data["src_requires"][require["name"]], require["name"]
            )

    def _match_entry(self, element, pkg_key):
        entry = dict()
        entry["name"] = self._xpath(".//@name", element)
        entry["flags"] = self._xpath(".//@flags", element)
        entry["version"] = self._xpath(".//@ver", element)
        entry["release"] = self._xpath(".//@rel", element)
        entry["epoch"] = self._xpath(".//@epoch", element)
        entry["pre"] = self._xpath(".//@pre", element)
        entry["pkgKey"] = str(pkg_key)
        return entry

    def _requires(self, pkg_key):
        requires = self._xpath(
            xpath=".//default:format/rpm:requires/rpm:entry", first=False
        )
        requires_list = []
        if requires:
            requires_list = [
                self._match_entry(element, pkg_key) for element in requires
            ]
        return requires_list

    def _provides(self):
        provides = self._xpath(
            xpath=".//default:format/rpm:provides/rpm:entry", first=False
        )
        if provides is None:
            return
        for provide_element in provides:
            provide = self._match_entry(provide_element, self._bpkg_key)
            self._bprovides[provide["name"]] = provide

            self.xml_data["bin_provides"][provide["name"]] = self._fill_value(
                self.xml_data["bin_provides"][provide["name"]], provide["name"]
            )

            self.xml_data["bin_provides"][str(self._bpkg_key)] = self._fill_value(
                self.xml_data["bin_provides"][str(
                    self._bpkg_key)], provide["name"]
            )

    def _files(self):
        files = self._xpath(
            xpath=".//default:format/default:file", first=False)
        if files is None:
            return
        for file_element in files:
            file = dict()
            file["name"] = self._xpath(".//text()", file_element)
            file["type"] = self._xpath(".//@type", file_element)
            file["pkgKey"] = str(self._bpkg_key)
            self._bfiles[file["name"]] = file
            self.xml_data["bin_files"][str(self._bpkg_key)] = self._fill_value(
                self.xml_data["bin_files"][str(self._bpkg_key)], file["name"]
            )

    def _parse(
        self,
        xml,
        package,
        files=False,
        namespaces="{http://linux.duke.edu/metadata/common}",
    ):
        for event, element in etree.iterparse(
            xml,
            events=["start", "end"],
            tag="%spackage" % namespaces,
        ):
            if not re.match(".*%s$" % package, element.tag):
                continue
            if event == "end":
                element.clear()
                self._element = None
            else:
                self._element = element
                self._extract_info(files)

    def _merge_files(self):
        for pkg_name, package in self.xml_data["bin_pack"]["packages"].items():
            self.xml_data["files"][str(package["pkgKey"])] = (
                self._filelist[pkg_name] or []
            )
            del self._filelist[pkg_name]

    def parse(self, xml_data=None, package="package"):
        """
        Parse the contents of the XML
        """

        if xml_data:
            self.xml_data = xml_data

        for xml, files in self._xml:
            if not os.path.exists(xml):
                self.xml_data = None
                raise FileNotFoundError(
                    "The specified file does not exist : %s" % xml)

            namespaces = "{http://linux.duke.edu/metadata/common}"
            if files:
                namespaces = "{http://linux.duke.edu/metadata/filelists}"
            self._parse(xml, package, files, namespaces)

        # Remove duplicate dependencies and components
        _map_relation = [
            (self.xml_data["bin_requires"], self._brequires),
            (self.xml_data["bin_provides"], self._bprovides),
            (self.xml_data["bin_files"], self._bfiles),
            (self.xml_data["src_requires"], self._srequires),
        ]

        for xml_data, data_source in _map_relation:
            for key, val in xml_data.items():
                xml_data[key] = [data_source[data] for data in set(val)]
            del data_source

        # fusing filelist mappings
        self._merge_files()
        return self.xml_data
