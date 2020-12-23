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
import threading
try:
    import xml.parsers.expat.errors as parse_errors
    import xml.etree.cElementTree as et
except ImportError:
    import xml.etree.ElementTree as et


class XmlParse:
    """
        loading msg in xml based on the diff code
    """
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if not hasattr(cls, "__instance"):
                cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        self.xml = None

    def _load_xml(self, xml_path):
        """
            loading content in xml
            :param xml_path: xml path
            :param tag: parse the node
        """
        if not xml_path:
            self.xml = None
            raise FileNotFoundError("The XML file does not exist")
        xml_path = os.path.join(os.path.dirname(__file__), xml_path)
        try:
            self.xml = et.parse(xml_path)
        except parse_errors as e:
            pass

    def clear_xml(self):
        self.xml = None

    @property
    def root(self):
        return self.xml.getroot()

    def _todict(self, tag):
        msg = {}
        for child in tag.findall("*"):
            msg[child.tag] = child.text
        return msg

    def content(self, label):
        if not self.xml:
            self._load_xml("mapping.xml")
        tag = self.root.find("./code/[@label='%s']" % label)
        if tag is None:
            return tag

        return self._todict(tag)


xml = XmlParse()
