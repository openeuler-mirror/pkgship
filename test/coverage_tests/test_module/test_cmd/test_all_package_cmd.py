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
test_all_package
"""
import os
import json
import sys
import unittest
import argparse
from unittest import mock
from requests.exceptions import ConnectionError as ConnErr
from test.coverage_tests.base_code.common_test_code import mock_get_response
from packageship.application.cli.commands.allpkg import AllPackageCommand
from test.coverage_tests.base_code.read_mock_data import MockData

MOCK_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mock_data")
ALL_SRC_PACKAGES_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "all_bin_package.json"))
ALL_BIN_PACKAGES_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "all_src_package.json"))
EMPTY_BIN_PACKAGES_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "empty_all_bin_package.json"))
EMPTY_SRC_PACKAGES_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "empty_all_src_package.json"))


class Redirect:
    _content = ""

    def write(self, s):
        self._content += s

    def flush(self):
        self._content = ""

    def getvalue(self):
        return self._content


class TestAllPackages(unittest.TestCase):
    """
    class for test all packages
    """
    def setUp(self) -> None:
        self.r = Redirect()
        sys.stdout = self.r

    @mock.patch("packageship.application.common.remote.RemoteService.get")
    def test_true_bin_params(self, mock_get):
        """
        test true binary params
        """
        parser = argparse.ArgumentParser()
        all_package = AllPackageCommand()
        data = json.dumps(ALL_BIN_PACKAGES_INFO)
        mock_get.return_value = mock_get_response(200, data)
        parser.add_argument('database')
        parser.add_argument('-packagename')
        parser.add_argument('-s')
        parser.add_argument('-remote')
        args = parser.parse_args(['os_version_1', '-packagename=Judy'])
        all_package.do_command(args)
        c = self.r.getvalue().strip()
        s = """
===================================================================================================
  Package Name       Database    Version    License            URL                    Source Name  
===================================================================================================
  389-ds-base        os_version_1   1.4.0.31   GPLv3+             https://www.port389.                
                                                               org                                 
  BareBonesBrowser   os_version_1   3.1        Public Domain      http://www.centerkey                
  Launch                                                       .com/java/browser/                  
  CUnit              os_version_1   2.1.3      LGPLv2+            http://cunit.sourcef                
                                                               orge.net/                           
  ComputeLibrary     os_version_1   20.02.1    MIT                https://developer.ar                
                                                               m.com/technologies/c                
                                                               ompute-library                      
  CreateImage        os_version_1   0.0.5      Huawei Software                                        
                                            License                                                
  Cython             os_version_1   0.29.14    Apache 2.0         https://cython.org/                 
  GConf2             os_version_1   3.2.6      LGPLv2+ and        http://projects.gnom                
                                            GPLv2+             e.org/gconf/                        
  GeoIP              os_version_1   1.6.12     LGPLv2+            http://www.maxmind.c                
                                                               om/app/c                            
  GeoIP-GeoLite-     os_version_1   2018.06    CC-BY-SA           http://dev.maxmind.c                
  data                                                         om/geoip/legacy/geol                
                                                               ite/                                
  GraphicsMagick     os_version_1   1.3.30     MIT                http://www.graphicsm                
                                                               agick.org/                          
===================================================================================================
        """.strip()
        self.assertEqual(c, s)

    @mock.patch("packageship.application.common.remote.RemoteService.get")
    def test_true_src_params(self, mock_get):
        """
        test true source params
        """
        parser = argparse.ArgumentParser()
        all_package = AllPackageCommand()
        data = json.dumps(ALL_SRC_PACKAGES_INFO)
        mock_get.return_value = mock_get_response(200, data)
        parser.add_argument('database')
        parser.add_argument('-packagename')
        parser.add_argument('-s')
        parser.add_argument('-remote')
        args = parser.parse_args(['os_version_1', '-packagename=Judy', '-ss'])
        all_package.do_command(args)
        c = self.r.getvalue().strip()
        s = """
====================================================================================================
  Package Name                Database    Version    License         URL                            
====================================================================================================
  389-ds-base                 os_version_1   1.4.0.31   GPLv3+          https://www.port389.org        
  389-ds-base-devel           os_version_1   1.4.0.31   GPLv3+          https://www.port389.org        
  389-ds-base-help            os_version_1   1.4.0.31   GPLv3+          https://www.port389.org        
  389-ds-base-legacy-tools    os_version_1   1.4.0.31   GPLv3+          https://www.port389.org        
  389-ds-base-snmp            os_version_1   1.4.0.31   GPLv3+          https://www.port389.org        
  BareBonesBrowserLaunch      os_version_1   3.1        Public Domain   http://www.centerkey.com/java  
                                                                     /browser/                      
  BareBonesBrowserLaunch-     os_version_1   3.1        Public Domain   http://www.centerkey.com/java  
  javadoc                                                            /browser/                      
  CUnit                       os_version_1   2.1.3      LGPLv2+         http://cunit.sourceforge.net/  
====================================================================================================
                """.strip()
        self.assertEqual(c, s)

    @mock.patch("packageship.application.common.remote.RemoteService.get")
    def test_wrong_status_code(self, mock_get):
        """
        test wrong status code
        """
        parser = argparse.ArgumentParser()
        all_package = AllPackageCommand()
        data = ''
        mock_get.return_value = mock_get_response(400, data)
        parser.add_argument('database')
        parser.add_argument('-packagename')
        parser.add_argument('-s')
        parser.add_argument('-remote')
        args = parser.parse_args(['os_version_1', '-packagename=Judy'])
        all_package.do_command(args)
        c = self.r.getvalue().strip()
        s = """
Request failed
400 Client Error: None for url: None
                        """.strip()
        self.assertEqual(c, s)

    @mock.patch("packageship.application.common.remote.RemoteService.get")
    def test_wrong_resp_code(self, mock_get):
        """
        test wrong resp code
        """
        parser = argparse.ArgumentParser()
        all_package = AllPackageCommand()
        data = json.dumps({'code': '4001'})
        mock_get.return_value = mock_get_response(200, data)
        parser.add_argument('database')
        parser.add_argument('-packagename')
        parser.add_argument('-s')
        parser.add_argument('-remote')
        args = parser.parse_args(['os_version_1', '-packagename=Judy'])
        all_package.do_command(args)
        c = self.r.getvalue().strip()
        s = """
ERROR_CONTENT  :
HINT           :Please check the parameter is valid and query again
Failed to get packages
                                """.strip()
        self.assertEqual(c, s)

    @mock.patch("packageship.application.common.remote.RemoteService.get")
    def test_wrong_resp_text(self, mock_get):
        """
        test wrong resp text
        """
        parser = argparse.ArgumentParser()
        all_package = AllPackageCommand()
        data = ''
        mock_get.return_value = mock_get_response(200, data)
        parser.add_argument('database')
        parser.add_argument('-packagename')
        parser.add_argument('-s')
        parser.add_argument('-remote')
        args = parser.parse_args(['os_version_1', '-packagename=Judy'])
        all_package.do_command(args)
        c = self.r.getvalue().strip()
        s = """
ERROR_CONTENT  :
HINT           :The content is not a legal json format,please check the parameters is valid
                                        """.strip()
        self.assertEqual(c, s)

    @mock.patch("packageship.application.common.remote.RemoteService.get", side_effect=ConnErr)
    def test_bad_request(self, mock_get):
        """
        test bad request
        """
        parser = argparse.ArgumentParser()
        all_package = AllPackageCommand()
        mock_get.return_value = None
        parser.add_argument('database')
        parser.add_argument('-packagename')
        parser.add_argument('-s')
        parser.add_argument('-remote')
        args = parser.parse_args(['os_version_1', '-packagename=Judy'])
        all_package.do_command(args)
        c = self.r.getvalue().strip()
        s = """
ERROR_CONTENT  :
HINT           :Please check the connection and try again
                                                """.strip()
        self.assertEqual(c, s)

    @mock.patch("packageship.application.common.remote.RemoteService.get")
    def test_empty_bin_resp(self, mock_get):
        """
        test empty binary resp
        """
        parser = argparse.ArgumentParser()
        all_package = AllPackageCommand()
        data = json.dumps(EMPTY_BIN_PACKAGES_INFO)
        mock_get.return_value = mock_get_response(200, data)
        parser.add_argument('database')
        parser.add_argument('-packagename')
        parser.add_argument('-s')
        parser.add_argument('-remote')
        args = parser.parse_args(['os_version_1', '-packagename=Judy'])
        all_package.do_command(args)
        c = self.r.getvalue().strip()
        self.assertEqual(c, "Sorry, no relevant information has been found yet\n".strip())

    @mock.patch("packageship.application.common.remote.RemoteService.get")
    def test_empty_src_resp(self, mock_get):
        """
        test empty source resp
        """
        parser = argparse.ArgumentParser()
        all_package = AllPackageCommand()
        data = json.dumps(EMPTY_SRC_PACKAGES_INFO)
        mock_get.return_value = mock_get_response(200, data)
        parser.add_argument('database')
        parser.add_argument('-packagename')
        parser.add_argument('-s')
        parser.add_argument('-remote')
        args = parser.parse_args(['os_version_1', '-packagename=Judy', '-ss'])
        all_package.do_command(args)
        c = self.r.getvalue().strip()
        self.assertEqual(c, "Sorry, no relevant information has been found yet\n".strip())
