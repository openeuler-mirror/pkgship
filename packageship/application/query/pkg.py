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
Module of query packages' info
"""
import gevent
from gevent import monkey

monkey.patch_all()

from packageship.application.common.constant import UNDERLINE, BINARY_DB_TYPE, SOURCE_DB_TYPE
from packageship.application.database.session import DatabaseSession
from packageship.application.query.query_body import QueryBody


class QueryPackage(object):
    """
    Class of query packages' info,include:
    query binary packages' detail,
    query source packages' detail,
    query binary packages' source package
    query source packages' binary packages
    """
    # database connection
    _db_session = DatabaseSession().connection()

    def __init__(self, database_list=None):
        self.db_list = [] if database_list is None else database_list
        self.rpm_type = None
        self.index = None

    def get_src_name(self, binary_list, specify_db=None):
        """
        Get binary packages' source name and version,support multiple databases
        Args:
            binary_list: need to query binary packages
            specify_db: specify database used for speed up queries
        Returns: binary packages' name/version and their source packages' name/version
        """
        response = []
        if not self.db_list or not binary_list:
            return response

        response = self._query_src_bin_rpm(binary_list, BINARY_DB_TYPE, specify_db)
        return response

    def get_bin_name(self, source_list, specify_db=None):
        """
        Get source packages' subpackages' name and version,support multiple databases
        Args:
            source_list: need to query source packages
            specify_db: specify database used for speed up queries
        Returns: source packages' name/version and their  subpackages' name/version
        """
        response = []
        if not self.db_list or not source_list:
            return response

        response = self._query_src_bin_rpm(source_list, SOURCE_DB_TYPE, specify_db)
        return response

    def get_src_info(self, src_list, database, page_num, page_size, command_line=False):
        """
        Query source packages' details
        Args:
            src_list: source_rpm list
            database: database
            page_num: Paging query index
            page_size: Paging query size
            command_line: Whether to query all,default false,used fro command line
        Returns: source_rpm info list
        """
        pass

    def get_bin_info(self, binary_list, database, page_num, page_size, command_line=False):
        """
        Query binary packages' details
        Args:
            binary_list: binary_rpm list
            database: database
            page_num: Paging query index
            page_size: Paging query size
            command_line: Whether to query all,default false,used fro command line
        Returns: binary_rpm info list
        """
        pass

    def _query_src_bin_rpm(self, rpm_list, query_db_type, specify_db):
        """
        Query binary package's source package or source package's binary packages
        Args:
            rpm_list: binary packages or source packages
            query_db_type: package type (binary or source)
            specify_db: specify database for speed up queries
        Returns: query result
        """
        response = []

        def job(rpm):
            """
            Multi-ctrip task
            Args:
                rpm: binary package or source package

            Returns: response

            """
            if specify_db:
                return self._query_current_database(rpm, specify_db, query_db_type)
            else:
                for database in self.db_list:
                    result = self._query_current_database(rpm, database, query_db_type)
                    if result:
                        return result

        works = [gevent.spawn(job, rpm) for rpm in rpm_list]
        gevent.joinall(works)
        response.extend([work.value for work in works if work.value])

        return response

    def _query_current_database(self, rpm, database, query_db_type):
        self.index = UNDERLINE.join((database, query_db_type))
        query_body = self._format_term_query(rpm)
        query_result = self._db_session.query(index=self.index, body=query_body)

        if not query_result or not query_result['hits']['hits']:
            return None

        hits_data = query_result['hits']['hits']
        rpm_info = self._process_bin_response(database, hits_data) \
            if query_db_type == BINARY_DB_TYPE \
            else self._process_src_response(database, hits_data)

        return rpm_info

    @staticmethod
    def _process_src_response(database, data):
        """
        Process query source package's binary packages result
        Args:
            database: database
            data: pending result

        Returns: format result

        """
        src_info = dict()
        source = data[0]['_source']
        src_info['source_name'] = source.get('name')
        src_info['src_version'] = source.get('version')
        src_info['database'] = database
        src_info['binary_infos'] = []
        subpackage_list = source.get('subpacks')
        if subpackage_list:
            src_info['binary_infos'].extend([{
                "bin_name": binary_rpm.get('name'),
                "bin_version": binary_rpm.get('version'),
            } for binary_rpm in subpackage_list])

        return src_info

    @staticmethod
    def _format_term_query(rpm_name):
        """
        Format query term body
        Args:
            rpm_name: packages list

        Returns: query body

        """
        query_body = QueryBody()
        source = ['name', 'version', 'src_name', 'src_version', 'subpacks']
        query_body.query_term = dict(name=dict(name=rpm_name), _source=source)
        return query_body.query_term

    @staticmethod
    def _process_bin_response(database, data):
        """
        Format result of query binary packages' source packages
        Args:
            database: database
            data: pending result

        Returns: format result

        """
        binary = data[0]['_source']
        binary_info = {
            "binary_name": binary.get('name'),
            "bin_version": binary.get('version'),
            "database": database,
            "src_name": binary.get('src_name'),
            "src_version": binary.get('src_version')
        }

        return binary_info
