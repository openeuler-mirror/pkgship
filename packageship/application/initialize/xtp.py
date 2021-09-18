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
from xml.etree import ElementTree as et
from packageship.application.initialize.base import ESJson


DEFAULT_NSMAP = "http://linux.duke.edu/metadata/common"
RPM_NSMAP = "http://linux.duke.edu/metadata/rpm"
MAP = {
    "pkgKey": None,
    "pkgId": ".//{%s}checksum:text" % DEFAULT_NSMAP,
    "name": ".//{%s}name:text" % DEFAULT_NSMAP,
    "arch": ".//{%s}arch:text" % DEFAULT_NSMAP,
    "version": ".//{%s}version:@ver" % DEFAULT_NSMAP,
    "epoch": ".//{%s}version:@epoch" % DEFAULT_NSMAP,
    "release": ".//{%s}version:@rel" % DEFAULT_NSMAP,
    "summary": ".//{%s}summary:text" % DEFAULT_NSMAP,
    "description": ".//{%s}description:text" % DEFAULT_NSMAP,
    "url": ".//{%s}url:text" % DEFAULT_NSMAP,
    "time_file": ".//{%s}time:@file" % DEFAULT_NSMAP,
    "time_build": ".//{%s}time:@build" % DEFAULT_NSMAP,
    "rpm_license": ".//{%s}license:text" % RPM_NSMAP,
    "rpm_vendor": ".//{%s}vendor:text" % RPM_NSMAP,
    "rpm_group": ".//{%s}group:text" % RPM_NSMAP,
    "rpm_buildhost": ".//{%s}buildhost:text" % RPM_NSMAP,
    "rpm_sourcerpm": ".//{%s}sourcerpm:text" % RPM_NSMAP,
    "rpm_header_start": ".//{%s}header-range:@start" % RPM_NSMAP,
    "rpm_header_end": ".//{%s}header-range:@end" % RPM_NSMAP,
    "rpm_packager": ".//{%s}packager:text" % DEFAULT_NSMAP,
    "size_package": ".//{%s}size:@package" % DEFAULT_NSMAP,
    "size_installed": ".//{%s}size:@installed" % DEFAULT_NSMAP,
    "size_archive": ".//{%s}size:@archive" % DEFAULT_NSMAP,
    "location_href": ".//{%s}location:@href" % DEFAULT_NSMAP,
    "location_base": ".//{%s}location:@base" % DEFAULT_NSMAP,
    "checksum_type": ".//{%s}checksum:@type" % DEFAULT_NSMAP,
}


class XmlPackage:
    """
    When the Repo source in Mainline is in XML format, the data
    is initialized by parsing the contents of the XML
    """
    file_nsmp = "http://linux.duke.edu/metadata/filelists"

    def __init__(self, xml, filelist) -> None:
        if not xml or not filelist:
            raise ValueError("Pass in the path to the real, valid XML file .")

        if isinstance(xml, str):
            self._xml = [(xml, False)]
        else:
            self._xml = [(_xml, False) for _xml in xml]
        self._xml.append((filelist, True))

        self._element = None
        self._spkg_key = 0
        self._bpkg_key = 0
        self.xml_data = ESJson()
        self._bprovides = ESJson()
        self._brequires = ESJson()
        self._bfiles = ESJson()
        self._srequires = ESJson()
        self._filelist = ESJson()

    def _xpath(self, xpath, element=None, first=True):
        if element is None:
            element = self._element
        if not first:
            return element.findall(xpath)

        xpath, attr = xpath.rsplit(":", maxsplit=1)
        select_element = element.find(xpath)
        if attr.startswith("@"):
            value = select_element.attrib.get(
                attr[1:], None)
        else:
            value = getattr(select_element, attr)
        return value

    def _extract_info(self, filelist=False):

        if filelist:
            binary_pkg_name = self._element.attrib.get("name")
            self._filelist[binary_pkg_name] = list()
            for file in self._xpath(".//{%s}file" % self.file_nsmp, first=False):
                pkg_file = dict(file=getattr(file, "text"))
                if file.attrib.get("type") == "dir":
                    pkg_file["filetype"] = "dir"
                else:
                    pkg_file["filetype"] = "file"

                self._filelist[binary_pkg_name].append(pkg_file)

        elif self._xpath(".//{%s}arch:text" % DEFAULT_NSMAP) == "src":
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
        entry["name"] = element.attrib.get("name")
        entry["flags"] = element.attrib.get("flags")
        entry["version"] = element.attrib.get("ver")
        entry["release"] = element.attrib.get("rel")
        entry["epoch"] = element.attrib.get("epoch")
        entry["pre"] = element.attrib.get("pre")
        entry["pkgKey"] = str(pkg_key)
        return entry

    def _requires(self, pkg_key):
        requires = self._xpath(
            xpath=".//{%s}requires/{%s}entry" % (RPM_NSMAP, RPM_NSMAP), first=False
        )
        requires_list = []
        if requires:
            requires_list = [
                self._match_entry(element, pkg_key) for element in requires
            ]
        return requires_list

    def _provides(self):
        provides = self._xpath(
            xpath=".//{%s}provides/{%s}entry" % (RPM_NSMAP, RPM_NSMAP), first=False
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
            xpath=".//{%s}format/{%s}file", first=False)
        if files is None:
            return
        for file_element in files:
            file = dict()
            file["name"] = getattr(file_element, "text")
            file["type"] = file_element.attrib.get("type")
            file["pkgKey"] = str(self._bpkg_key)
            self._bfiles[file["name"]] = file
            self.xml_data["bin_files"][str(self._bpkg_key)] = self._fill_value(
                self.xml_data["bin_files"][str(self._bpkg_key)], file["name"]
            )

    def _parse(self, xml, files=False):
        tree = et.ElementTree(file=xml)
        nsmap = self.file_nsmp if files else DEFAULT_NSMAP
        for element in tree.findall("{%s}package" % nsmap):
            self._element = element
            self._extract_info(filelist=files)

    def _merge_files(self):
        for pkg_name, package in self.xml_data["bin_pack"]["packages"].items():
            self.xml_data["files"][str(package["pkgKey"])] = (
                self._filelist[pkg_name] or []
            )
            del self._filelist[pkg_name]

    def parse(self, xml_data=None):
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
            self._parse(xml, files)

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
