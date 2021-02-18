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
test_single
"""
import json
import os
import sys
import unittest
import argparse
from unittest import mock
from requests.exceptions import ConnectionError as ConnErr
from test.base_code.common_test_code import mock_get_response
from packageship.application.cli.commands.singlepkg import SingleCommand
from test.base_code.read_mock_data import MockData

MOCK_DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mock_data")
SRC_PACKAGES_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "judy_source.json"))
BIN_PACKAGES_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "judy_binary.json"))
EMPTY_PACKAGES_INFO = MockData.read_mock_json_data(os.path.join(MOCK_DATA_FILE, "empty_judy_binary.json"))


class Redirect:
    _content = ""

    def write(self, s):
        self._content += s

    def flush(self):
        self._content = ""

    def getvalue(self):
        return self._content


class TestSinglePackage(unittest.TestCase):
    """
    class for test single package
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
        single = SingleCommand()
        data = json.dumps(BIN_PACKAGES_INFO)
        mock_get.return_value = mock_get_response(200, data)
        parser.add_argument('database')
        parser.add_argument('packagename')
        parser.add_argument('-s')
        parser.add_argument('-remote')
        args = parser.parse_args(['openeuler', 'packagename=Judy'])
        single.do_command(args)
        c = self.r.getvalue().strip()
        s = """
Source Name    :Judy
Version        :1.0.5
Release        :
Url            :http://sourceforge.net/projects/judy/
License        :
Summary        :C library array
Binary Name    :Judy
Description    :The package provides the most advanced core technology, the main advantages are
               :scalability, high performance and memory efficiency.
Build Required :
Provides
====================================================================================================
  Symbol                                          Required by                                       
====================================================================================================
  Judy                                            Judy-devel                                        
  Judy(aarch-64)                                                                                    
  libJudy.so.1()(64bit)                           mariadb-oqgraph-engine                            
====================================================================================================
Requires
====================================================================================================
  Symbol                                                                       Provides by          
====================================================================================================
  /bin/sh                                                                      bash                 
  ld-linux-aarch64.so.1()(64bit)                                               glibc                
  ld-linux-aarch64.so.1(GLIBC_2.17)(64bit)                                     glibc                
  rtld(GNU_HASH)                                                               glibc                
  libc.so.6(GLIBC_2.17)(64bit)                                                 glibc                
====================================================================================================
File List
====================================================================================================
  Symbol   File List                                                                                 
====================================================================================================
  dir     /usr/share/licenses/Judy                                                                  
  file    /usr/share/licenses/Judy/COPYING                                                          
          /etc/ima/digest_lists.tlv/0-metadata_list-compact_tlv-Judy-1.0.5-19.oe1.aarch64           
          /usr/lib64/libJudy.so.1                                                                   
          /usr/lib64/libJudy.so.1.0.3                                                               
          /etc/ima/digest_lists/0-metadata_list-compact-Judy-1.0.5-19.oe1.aarch64                   
  ghost                                                                                             
====================================================================================================
                """.strip()
        self.assertEqual(c, s)

    @mock.patch("packageship.application.common.remote.RemoteService.get")
    def test_true_src_params(self, mock_get):
        """
        test true source params
        """
        parser = argparse.ArgumentParser()
        single = SingleCommand()
        data = json.dumps(SRC_PACKAGES_INFO)
        mock_get.return_value = mock_get_response(200, data)
        parser.add_argument('database')
        parser.add_argument('packagename')
        parser.add_argument('-s')
        parser.add_argument('-remote')
        args = parser.parse_args(['openeuler', 'packagename=Judy', '-ss'])
        single.do_command(args)
        c = self.r.getvalue().strip()
        s = """
Source Name    :Judy
Version        :1.0.5
Release        :19.oe1
Url            :http://sourceforge.net/projects/judy/
License        :LGPLv2+
Summary        :C library array
Binary Name    :
Description    :The package provides the most advanced core technology, the main advantages are
               :scalability, high performance and memory efficiency.
Build Required :coreutils,gawk,gcc,make,sed
--------------------------------------------------
Judy
Provides
====================================================================================================
  Symbol                                          Required by                                       
====================================================================================================
  Judy                                            Judy-devel                                        
  Judy(aarch-64)                                                                                    
  libJudy.so.1()(64bit)                           mariadb-oqgraph-engine                            
====================================================================================================
Requires
====================================================================================================
  Symbol                                                                       Provides by          
====================================================================================================
  /bin/sh                                                                      bash                 
  ld-linux-aarch64.so.1()(64bit)                                               glibc                
  ld-linux-aarch64.so.1(GLIBC_2.17)(64bit)                                     glibc                
  rtld(GNU_HASH)                                                               glibc                
  libc.so.6(GLIBC_2.17)(64bit)                                                 glibc                
====================================================================================================
--------------------------------------------------
Judy-devel
Provides
====================================================================================================
  Symbol                                                          Required by                       
====================================================================================================
  Judy-devel                                                      mariadb                           
  Judy-devel(aarch-64)                                                                              
====================================================================================================
Requires
====================================================================================================
  Symbol                             Provides by                                                    
====================================================================================================
  Judy                               Judy                                                           
====================================================================================================
--------------------------------------------------
Judy-help
Provides
====================================================================================================
  Symbol                                                        Required by                         
====================================================================================================
  Judy-help                                                                                         
  Judy-help(aarch-64)                                                                               
====================================================================================================
Requires
No related components
                """.strip()
        self.assertEqual(c, s)

    @mock.patch("packageship.application.common.remote.RemoteService.get")
    def test_wrong_status_code(self, mock_get):
        """
        test wrong status code
        """
        parser = argparse.ArgumentParser()
        single = SingleCommand()
        data = ''
        mock_get.return_value = mock_get_response(400, data)
        parser.add_argument('database')
        parser.add_argument('packagename')
        parser.add_argument('-s')
        parser.add_argument('-remote')
        args = parser.parse_args(['openeuler', 'packagename=Judy'])
        single.do_command(args)
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
        single = SingleCommand()
        data = json.dumps({'code': '4001'})
        mock_get.return_value = mock_get_response(200, data)
        parser.add_argument('database')
        parser.add_argument('packagename')
        parser.add_argument('-s')
        parser.add_argument('-remote')
        args = parser.parse_args(['openeuler', 'packagename=Judy'])
        single.do_command(args)
        c = self.r.getvalue().strip()
        s = """
ERROR_CONTENT  :
HINT           :Please check the parameter is valid and query again
Failed to get package
                                        """.strip()
        self.assertEqual(c, s)

    @mock.patch("packageship.application.common.remote.RemoteService.get")
    def test_wrong_resp_text(self, mock_get):
        """
        test wrong resp text
        """
        parser = argparse.ArgumentParser()
        single = SingleCommand()
        data = ''
        mock_get.return_value = mock_get_response(200, data)
        parser.add_argument('database')
        parser.add_argument('packagename')
        parser.add_argument('-s')
        parser.add_argument('-remote')
        args = parser.parse_args(['openeuler', 'packagename=Judy'])
        single.do_command(args)
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
        single = SingleCommand()
        mock_get.return_value = None
        parser.add_argument('database')
        parser.add_argument('packagename')
        parser.add_argument('-s')
        parser.add_argument('-remote')
        args = parser.parse_args(['openeuler', 'packagename=Judy'])
        single.do_command(args)
        c = self.r.getvalue().strip()
        s = """
ERROR_CONTENT  :
HINT           :Please check the connection and try again
                                                        """.strip()
        self.assertEqual(c, s)

    @mock.patch("packageship.application.common.remote.RemoteService.get")
    def test_wrong_resp_keyerror(self, mock_get):
        """
        test wrong resp key error
        """
        parser = argparse.ArgumentParser()
        single = SingleCommand()
        data = json.dumps(SRC_PACKAGES_INFO)
        mock_get.return_value = mock_get_response(200, data)
        parser.add_argument('database')
        parser.add_argument('packagename')
        parser.add_argument('-s')
        parser.add_argument('-remote')
        args = parser.parse_args(['openeuler', 'packagename=Judy'])
        single.do_command(args)
        c = self.r.getvalue().strip()
        s = """
Source Name    :Judy
Version        :1.0.5
Release        :19.oe1
Url            :http://sourceforge.net/projects/judy/
License        :LGPLv2+
Summary        :C library array
Binary Name    :
Description    :The package provides the most advanced core technology, the main advantages are
               :scalability, high performance and memory efficiency.
Build Required :coreutils,gawk,gcc,make,sed
No related components
             """.strip()
        self.assertEqual(c, s)

    @mock.patch("packageship.application.common.remote.RemoteService.get")
    def test_wrong_resp_subpacks(self, mock_get):
        """
        test wrong resp subpacks
        """
        parser = argparse.ArgumentParser()
        single = SingleCommand()
        data = json.dumps(BIN_PACKAGES_INFO)
        mock_get.return_value = mock_get_response(200, data)
        parser.add_argument('database')
        parser.add_argument('packagename')
        parser.add_argument('-s')
        parser.add_argument('-remote')
        args = parser.parse_args(['openeuler', 'packagename=Judy', '-ss'])
        single.do_command(args)
        c = self.r.getvalue().strip()
        s = """
Source Name    :Judy
Version        :1.0.5
Release        :
Url            :http://sourceforge.net/projects/judy/
License        :
Summary        :C library array
Binary Name    :Judy
Description    :The package provides the most advanced core technology, the main advantages are
               :scalability, high performance and memory efficiency.
Build Required :
No related components
            """.strip()
        self.assertEqual(c, s)

    @mock.patch("packageship.application.common.remote.RemoteService.get")
    def test_empty_content(self, mock_get):
        """
        test empty content
        """
        parser = argparse.ArgumentParser()
        single = SingleCommand()
        data = json.dumps(EMPTY_PACKAGES_INFO)
        mock_get.return_value = mock_get_response(200, data)
        parser.add_argument('database')
        parser.add_argument('packagename')
        parser.add_argument('-s')
        parser.add_argument('-remote')
        args = parser.parse_args(['openeuler', 'packagename=Judy'])
        single.do_command(args)
        c = self.r.getvalue().strip()
        s = """
Source Name    :Judy
Version        :1.0.5
Release        :
Url            :http://sourceforge.net/projects/judy/
License        :
Summary        :C library array
Binary Name    :Judy
Description    :The package provides the most advanced core technology, the main advantages are
               :scalability, high performance and memory efficiency.
Build Required :
Provides
No relevant dependent data
Requires
====================================================================================================
  Symbol                                                                       Provides by          
====================================================================================================
  /bin/sh                                                                      bash                 
  ld-linux-aarch64.so.1()(64bit)                                               glibc                
  ld-linux-aarch64.so.1(GLIBC_2.17)(64bit)                                     glibc                
  rtld(GNU_HASH)                                                               glibc                
  libc.so.6(GLIBC_2.17)(64bit)                                                 glibc                
====================================================================================================
File List
No related components
        """.strip()
        self.assertEqual(c, s)
