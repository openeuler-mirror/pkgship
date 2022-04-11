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

from packageship.application.common.constant import UNDERLINE, BINARY_DB_TYPE, SOURCE_DB_TYPE, MAX_PAGE_SIZE, \
    DEFAULT_PAGE_NUM
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
        Raises: DatabaseConfigException ElasticSearchQueryException
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
        Raises: DatabaseConfigException ElasticSearchQueryException
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
        Raises: DatabaseConfigException ElasticSearchQueryException
        """
        self.rpm_type = SOURCE_DB_TYPE
        response = self._get_rpm_info(database, page_num, page_size, command_line, rpm_list=src_list)
        return response

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
        Raises: DatabaseConfigException ElasticSearchQueryException
        """
        self.rpm_type = BINARY_DB_TYPE
        response = self._get_rpm_info(database, page_num, page_size, command_line, rpm_list=binary_list)
        return response

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

    def _get_rpm_info(self, database, page_num, page_size, command_line, rpm_list=None):
        """
        General method for obtaining package details
        Args:
            rpm_list: binary rpm_list or source rpm_list
            database: database name
            page_num: page number
            page_size: page size
            command_line: is or not command line scenes

        Returns: result of query package details
        """
        response = dict(total=0, data=[])
        # If the query list is empty, return directly; if the query list is None, it means query all packages.
        if isinstance(rpm_list, list):
            rpm_list = [rpm for rpm in rpm_list if rpm]
            if not rpm_list:
                return response

        self.index = UNDERLINE.join((database, self.rpm_type))
        # Used for Command Line,query all data and no Pagination
        if command_line and rpm_list is None:
            query_result = self._db_session.scan(index=self.index, body=QueryBody.QUERY_ALL)
            total_num = self._db_session.count(index=self.index, body=QueryBody.QUERY_ALL)
            response['total'] = total_num.get('count')
            if self.rpm_type == SOURCE_DB_TYPE:
                self._process_query_src_response(response, query_result)
            elif self.rpm_type == BINARY_DB_TYPE:
                self._process_query_bin_response(response, query_result)

            return response
        # Distinguish query body and query scope according to usage scenarios
        query_body, query_all = self._process_query_body(command_line, page_num, page_size, rpm_list)
        query_result = self._db_session.query(index=self.index, body=query_body)
        if query_result:
            try:
                rpm_info_list = query_result['hits']['hits']
                if self.rpm_type == SOURCE_DB_TYPE:
                    self._process_query_src_response(response, rpm_info_list)
                elif self.rpm_type == BINARY_DB_TYPE:
                    self._process_query_bin_response(response, rpm_info_list)
                # Distinguish the total quantity query method according to the usage scenario
                total_num = self._db_session.count(index=self.index, body=QueryBody.QUERY_ALL)['count'] \
                    if query_all else query_result['hits']['total']['value']
                response['total'] = total_num
            except KeyError:
                response = dict(total=0, data=[])
                return response
        return response

    def _process_query_body(self, command_line, page_num, page_size, rpm_list):
        """
        Splicing query statements through parameters
        Args:
            command_line: is or not command line
            page_num: page number
            page_size: page size
            rpm_list: binary rpm_list or source rpm_list

        Returns: query body

        """
        # is or not query all data,used for get data number
        query_all = False
        if command_line and rpm_list:
            # Query specify rpm_list of Command line mode
            query_body = self._process_query_terms(DEFAULT_PAGE_NUM, MAX_PAGE_SIZE, rpm_list)
        else:
            if rpm_list is None:
                # Query all data and Pagination of UI mode
                query_body = self._format_paging_query_all(page_num, page_size)
                query_all = True
            else:
                # Query specify rpm_list of UI mode
                query_body = self._process_query_terms(page_num, page_size, rpm_list)

        return query_body, query_all

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
    def _process_query_terms(page_num, page_size, rpm_list):
        """
        Format query terms body
        Args:
            page_num:  page num
            page_size:  page size
            rpm_list:  packages

        Returns: query body

        """
        query_body = QueryBody()
        query_body.query_terms = (dict(fields=dict(name=[rpm_info for rpm_info in rpm_list]),
                                       page_num=(page_num - 1) * page_size,
                                       page_size=page_size
                                       ))
        return query_body.query_terms

    @staticmethod
    def _format_paging_query_all(page_num, page_size):
        """
        Format query_body of query all data by page
        Args:
            page_num: page num
            page_size: page size

        Returns: query body

        """
        query_body = QueryBody.PAGING_QUERY_ALL
        query_body['from'] = (page_num - 1) * page_size
        query_body['size'] = page_size
        return query_body

    @staticmethod
    def _process_query_src_response(response, source_list):
        """
        Process return value of query source packages detail
        Args:
            response: return value
            source_list: Pending data

        Returns: response

        """
        src_info_list = []
        for source in source_list:
            src = dict()
            source_info = source['_source']
            src['src_name'] = source_info.get('name')
            src['version'] = source_info.get('version')
            src['release'] = source_info.get('release')
            src['url'] = source_info.get('url')
            src['license'] = source_info.get('rpm_license')
            src['summary'] = source_info.get('summary')
            src['description'] = source_info.get('description')
            src['vendor'] = source_info.get('rpm_vendor')
            src['href'] = source_info.get('location_href')
            src['subpacks'] = [subpackage.get('name') for subpackage in source_info.get('subpacks')] \
                if source_info.get('subpacks') else []
            src_info = {source_info.get('name'): src}
            src_info_list.append(src_info)

        response['data'] = src_info_list
        return response

    @staticmethod
    def _process_query_bin_response(response, binary_list):
        """
        Process return value of query binary packages detail
        Args:
            response: return value
            binary_list: Pending data

        Returns: response

        """
        bin_info_list = []
        for binary in binary_list:
            bin_dict = dict()
            binary_info = binary['_source']
            bin_dict['bin_name'] = binary_info.get('name')
            bin_dict['version'] = binary_info.get('version')
            bin_dict['release'] = binary_info.get('release')
            bin_dict['url'] = binary_info.get('url')
            bin_dict['license'] = binary_info.get('rpm_license')
            bin_dict['summary'] = binary_info.get('summary')
            bin_dict['description'] = binary_info.get('description')
            bin_dict['vendor'] = binary_info.get('rpm_vendor')
            bin_dict['sourcerpm'] = binary_info.get('rpm_sourcerpm')
            bin_dict['src_name'] = binary_info.get('src_name')
            bin_dict['href'] = binary_info.get('location_href')
            bin_dict['file_list'] = QueryPackage._process_file_lists(binary_info.get('filelists'))
            bin_info = {binary_info.get('name'): bin_dict}
            bin_info_list.append(bin_info)

        response['data'] = bin_info_list
        return response

    @staticmethod
    def _process_file_lists(file_lists):
        """
        Process binary packages' file list
        Args:
            file_lists: file list

        Returns: format file_list

        """
        file_list = []
        if file_lists:
            file_list.extend([{
                "filenames": file.get('filenames'),
                "dirname": file.get('dirname'),
                "filetypes": file.get('filetypes')
            } for file in file_lists
            ])
        return file_list

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
        query_body.query_term = dict(fields=dict(name=rpm_name), _source=source)
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
