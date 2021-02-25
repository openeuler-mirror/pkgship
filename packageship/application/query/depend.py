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
Module of query require relation
"""
import gevent
from gevent import monkey

monkey.patch_all()

from packageship.application.common.constant import PROVIDES_NAME, FILES_NAME
from packageship.application.query import Query
from packageship.application.query.query_body import QueryBody


class RequireBase(Query):
    """
    Base class query require relation
    """

    def __init__(self):
        super(RequireBase, self).__init__()
        self.db_list = None
        self._source_data = ['name', 'version', 'src_name',
                             'src_version', 'provides', 'files']

    def _process_requires(self, query_rpm_infos):
        """
        Process binary package install requires' info or source packages' build info
        Args:
            query_rpm_infos:  response of pending add requires' info

        Returns: response of added requires' info

        """
        # Get all the components that the binary package depends on,unified search
        component_list = list(set([requires for rpm_info in query_rpm_infos for requires in rpm_info["requires"]]))
        if not component_list:
            return
        # Used to record the package information of all found components
        # key: component name; value: package information of provide component
        all_components_info_dict = dict()
        for databse in self.db_list:
            # First query all components of not found by "provides.name"
            component_batch_list = [component_list[i:i + 200] for i in range(0, len(component_list), 200)]
            next_query_rpms = []
            works = [
                gevent.spawn(self._gevent_component_job, databse, components, all_components_info_dict,
                             PROVIDES_NAME) for components in component_batch_list]
            gevent.joinall(works)
            for work in works:
                next_query_rpms.extend(work.value if work.value else [])
            if not next_query_rpms:
                break

            # if not found by "provides.name",query components by "files.name"
            query_files_rpms = [next_query_rpms[i:i + 100]
                                for i in range(0, len(next_query_rpms), 100) if next_query_rpms[i:i + 100]]
            works = [
                gevent.spawn(self._gevent_component_job, databse, components, all_components_info_dict, FILES_NAME)
                for components in query_files_rpms]
            gevent.joinall(works)
            component_list = []
            for work in works:
                component_list.extend(work.value if work.value else [])

            # if all components found,stop query
            # if not found by "provides.name" and "files.name",query to the next database
            if not component_list:
                break

        # update info of components
        self._update_requires(all_components_info_dict, query_rpm_infos)

    def _gevent_component_job(self, database, components, all_components_info_dict, query_content_name):
        """
        multi-ctrip of query component info
        Args:
            database: database
            components: components of need query
            all_components_info_dict: dict of components found
            query_content_name: query field

        Returns: components not found

        """
        # First filter from the queried dict
        query_all_components_name_set = set(list(all_components_info_dict.keys()))
        no_query_components = set(components)
        if query_all_components_name_set:
            no_query_components.difference_update(query_all_components_name_set)
        if not no_query_components:
            return []
        # Then query by query field(provides.name or files.name)
        components = list(no_query_components)
        _query_body = self._format_terms_index_and_body(database=database,
                                                        query_content={query_content_name: components},
                                                        source=self._source_data)
        result = self.session.query(index=self.binary_index, body=_query_body)
        pending_query_components = self._query_complete(components, database, result,
                                                        all_components_info_dict, query_content_name)

        return pending_query_components

    def _update_requires(self, all_component_info_dict, query_rpm_infos):
        """
        update info of components
        Args:
            all_component_info_dict:  Information of previously assembled components
            query_rpm_infos:  components that needs to be updated

        Returns:

        """
        for rpm_info in query_rpm_infos:
            if rpm_info.get('requires'):
                new_requires_list = []
                component_bin_count_dict = dict()
                multi_binary_component_list = []
                for component_name in rpm_info.get('requires'):
                    self._convert_multi_binary_components(all_component_info_dict, component_bin_count_dict,
                                                          component_name,
                                                          multi_binary_component_list, new_requires_list)

                self._filter_multi_binary_components(component_bin_count_dict, multi_binary_component_list,
                                                     new_requires_list)
                rpm_info['requires'] = new_requires_list
            else:
                rpm_info['requires'] = []

    @staticmethod
    def _convert_multi_binary_components(all_component_info_dict, component_bin_count_dict, component_name,
                                         multi_binary_component_list, new_requires_list):
        """
        Add the uniquely determined binary package info to the result list
        Construct a dictionary of occurrences of binary packages and list of repeated binary packages
        Args:
            all_component_info_dict: all components dict
            component_bin_count_dict: The number of times the binary package of the component is provided
            component_name: component name
            multi_binary_component_list: list of repeated binary packages
            new_requires_list: result list

        Returns: None

        """
        component_info = all_component_info_dict.get(component_name)
        if component_info:
            # If the component is provided by the only binary package, directly add the result list
            if len(component_info) <= 1:
                new_requires_list.extend(component_info)
                return
            # If the component is provided by multiple binary packages, record first and then filter
            # Construct a dictionary of occurrences of binary packages
            multi_binary_component_list.append(component_info)
            for component in component_info:
                try:
                    com_bin_name_count = component_bin_count_dict[component.get('com_bin_name')]
                    component_bin_count_dict[component.get('com_bin_name')] = com_bin_name_count + 1
                except KeyError:
                    component_bin_count_dict[component.get('com_bin_name')] = 1
        else:
            new_requires_list.append(dict(component=component_name))
            return

    @staticmethod
    def _filter_multi_binary_components(component_bin_count_dict, multi_binary_component_list, new_requires_list):
        """
        Filter results based on component name and number of occurrences of binary packages
        Args:
            component_bin_count_dict: The number of times the binary package of the component is provided
            multi_binary_component_list: list of repeated binary packages
            new_requires_list: result list

        Returns: None

        """
        for component_list in multi_binary_component_list:
            max_count = 0
            final_component_info = dict()
            # Sort by name first, then filter the results according to the number of occurrences of binary packages
            component_list.sort(key=lambda x: x.get('component'))
            for component in component_list:
                if component_bin_count_dict.get(component.get('com_bin_name')) > max_count:
                    final_component_info = component
                    max_count = component_bin_count_dict.get(component.get('com_bin_name'))

            new_requires_list.append(final_component_info)

    @staticmethod
    def _query_complete(component_list, database, query_result, all_components_info_dict, component_source_type):
        """
        Query the binary packages information according to the component
        Args:
            database: database
            query_result: binary packages
            all_components_info_dict: component info dict, first query from this dict,if query no result,
                                      next query by database
        Returns: is or not query all result

        """
        try:
            for data_source in query_result['hits']['hits']:
                data_rpm = data_source['_source']
                _component_list = []
                if component_source_type == PROVIDES_NAME:
                    _component_list = data_rpm.get('provides')
                elif component_source_type == FILES_NAME:
                    _component_list = data_rpm.get('files')
                # Add the components provided by the found binary package to the dictionary
                if not _component_list:
                    return component_list

                for provide_info in _component_list:
                    _key = provide_info.get('name')
                    _component_info = RequireBase._process_component_info(_key, data_rpm, database)
                    try:
                        all_components_info_dict[_key].append(_component_info)
                    except KeyError:
                        all_components_info_dict[_key] = [_component_info]
            # Filter the components that have been found
            query_data_set = set(list(all_components_info_dict.keys()))
            pending_query_set = set(component_list)
            if query_data_set:
                pending_query_set.difference_update(query_data_set)
            return list(pending_query_set)
        except KeyError:
            return component_list

    @staticmethod
    def _process_component_info(component, data_rpm, database):
        """
        Process binary packages' requires field or source packages' requires field
        Args:
            component: component name
            data_rpm: binary package's info
            database: database

        Returns: component info

        """
        component_info = dict(
            component=component,
            com_bin_name=data_rpm.get('name'),
            com_bin_version=data_rpm.get('version'),
            com_src_name=data_rpm.get('src_name'),
            com_src_version=data_rpm.get('src_version'),
            com_database=database
        )
        return component_info

    def _format_terms_index_and_body(self, database, query_content, source):
        """
        Format query term body
        Args:
            database: index of es
            query_content: query condition
            source: query fields

        Returns: query body

        """
        self.set_index(index=database)
        query_body = QueryBody()
        query_body.query_terms = dict(name=query_content,
                                      _source=source,
                                      page_num=0,
                                      page_size=300)
        return query_body.query_terms


class BuildRequires(RequireBase):
    """
    Query source packages' build requires
    """

    def __init__(self, database_list):
        super(BuildRequires, self).__init__()
        self.db_list = database_list

    def get_build_req(self, source_list, specify_db=None):
        """
        Get one or more source packages build requires,
        If no database is specified, it will be searched according to the priority of the database
        Args:
            source_list: source packages
            specify_db: specify database
        Returns: source packages build requires info
        Raises: DatabaseConfigException,ElasticSearchQueryException

        """
        response = []
        if not self.db_list or not source_list:
            return response
        # Use multi-ctrip query
        source_rpm_batch_list = [source_list[i:i + 100] for i in range(0, len(source_list), 100)]
        # If specify database, query requires according to database
        if specify_db:
            works = [gevent.spawn(self._query_build_requires, source_batch_rpms, specify_db) for source_batch_rpms in
                     source_rpm_batch_list]
            gevent.joinall(works)
            for work in works:
                response.extend(work.value if work.value else [])
        else:
            # If not specify, query requires according to database priority
            for database in self.db_list:
                works = [gevent.spawn(self._gevent_source_job, source_batch_rpms, database) for source_batch_rpms in
                         source_rpm_batch_list]
                gevent.joinall(works)

                next_query_binary_rpms = []
                for work in works:
                    query_binary_rpms, no_query_binary_rpms = work.value
                    response.extend(query_binary_rpms)
                    next_query_binary_rpms.extend(no_query_binary_rpms)
                # All binary packages found,stop query
                if not next_query_binary_rpms:
                    break
                # Continue to search for packages not found
                source_rpm_batch_list = [next_query_binary_rpms[i:i + 50] for i in
                                         range(0, len(next_query_binary_rpms), 50)]

        self._process_requires(response)
        return response

    def _gevent_source_job(self, source_rpms, database):
        """
        multi-ctrip of query sources packages' build requires
        Args:
            source_rpms: source packages
            database: database

        Returns: source packages found and source packages not found

        """
        no_query_source_rpms = set(source_rpms)
        query_source_rpms = self._query_build_requires(source_rpms, database)
        if query_source_rpms:
            no_query_source_rpms.difference_update(
                set([source_info.get('source_name') for source_info in query_source_rpms]))

        return query_source_rpms, list(no_query_source_rpms)

    def _query_build_requires(self, source_rpms, data_base):
        """
        Query build requires of one database
        Args:
            source_rpms: source packages
            data_base: database

        Returns: query result

        """
        query_content = dict(name=source_rpms)
        source = ['name', 'version', 'requires']
        query_body = self._format_terms_index_and_body(data_base, query_content, source)
        query_src_result = self.session.query(index=self.source_index, body=query_body)
        source_rpm_info_list = []
        # Processing the result of the query, at this time the component information only has the names
        if query_src_result and query_src_result['hits']['hits']:
            for source_info in query_src_result['hits']['hits']:
                source_data = source_info['_source']
                source_rpm_info_list.append(dict(source_name=source_data.get('name'),
                                                 src_version=source_data.get('version'),
                                                 database=data_base,
                                                 requires=[require["name"] for require in source_data["requires"]
                                                           if require["requires_type"] == "build"]))

        return source_rpm_info_list


class InstallRequires(RequireBase):
    """
    Query binary packages' install requires
    """

    def __init__(self, database_list):
        super(InstallRequires, self).__init__()
        self.db_list = database_list

    def get_install_req(self, binary_list, specify_db=None):
        """
        Get one or more binary packages install requires,
        If no database is specified, it will be searched according to the priority of the database
        Args:
            binary_list: binary packages
            specify_db: specify database
        Returns: binary packages install requires info
        Raises: DatabaseConfigException,ElasticSearchQueryException

        """
        response = []
        if not self.db_list or not binary_list:
            return response
        # Use multi-ctrip query
        batch_binary_list = [binary_list[i:i + 100] for i in range(0, len(binary_list), 100)]
        # If specify database, query requires according to database
        if specify_db:
            works = [gevent.spawn(self._query_install_requires, binary_rpms, specify_db)
                     for binary_rpms in batch_binary_list]
            gevent.joinall(works)
            for work in works:
                response.extend(work.value)
        else:
            # If not specify, query requires according to database priority
            for _db in self.db_list:
                next_query_rpms = []
                works = [gevent.spawn(self._gevent_binary_job, binary_rpms, _db) for binary_rpms in batch_binary_list]
                gevent.joinall(works)
                for work in works:
                    install_requires, binary_rpms = work.value
                    response.extend(install_requires)
                    if binary_rpms:
                        next_query_rpms.extend(binary_rpms)
                # All binary packages found,stop query
                if not next_query_rpms:
                    break
                # Continue to search for packages not found
                batch_binary_list = [next_query_rpms[i:i + 50] for i in range(0, len(next_query_rpms), 50)]

        self._process_requires(response)

        return response

    def _gevent_binary_job(self, binary_rpms, database):
        """
        multi_ctrip of query binary install requires
        Args:
            binary_rpms: binary packages
            database: database

        Returns: binary packages found and binary packages not found

        """
        binary_rpm_set = set(binary_rpms)
        install_requires = self._query_install_requires(binary_rpms, database)
        if install_requires:
            binary_rpm_set.difference_update(set([binary_info['binary_name'] for binary_info in install_requires]))
        # binary packages found and binary packages not found
        return install_requires, list(binary_rpm_set)

    def _query_install_requires(self, binary_list, data_base):
        """
        Query install requires of one database
        Args:
            binary_list: binary package
            data_base: database

        Returns: query result

        """
        _source = ['name', 'version', 'src_name', 'src_version', 'requires']
        _query_body = self._format_terms_index_and_body(
            database=data_base, query_content=dict(name=binary_list), source=_source)
        query_bin_result = self.session.query(index=self.binary_index, body=_query_body)

        # Processing the result of the query, at this time the component information only has the names
        binary_rpm_info_list = []
        if query_bin_result and query_bin_result['hits']['hits']:
            for binary_info in query_bin_result['hits']['hits']:
                _source = binary_info['_source']
                binary_rpm_info_list.append(
                    dict(binary_name=_source.get('name'),
                         bin_version=_source.get('version'),
                         database=data_base,
                         src_name=_source.get('src_name'),
                         src_version=_source.get('src_version'),
                         requires=[require["name"] for require in _source["requires"] if
                                   require["requires_type"] == "install"]))

        return binary_rpm_info_list


class BeDependRequires(Query):
    """query bedepend infos"""

    def get_be_req(self, binary_list, database):
        """

        Args:
            binary_list: Binary package
            database: Database name

        Returns: bedepend infos

        Raises: DatabaseConfigException,ElasticSearchQueryException

        """
        self.set_index(index=database)

        def job(binarys):
            query_body = QueryBody()
            query_body.query_terms = dict(
                name=dict(binary_name=binarys), page_num=0, page_size=1000)
            result = self.session.query(
                index=self.bedepend_index, body=query_body.query_terms)
            try:
                _depend = [depend["_source"]
                           for depend in result["hits"]["hits"]
                           if result and result['hits']['hits']
                           ]
            except KeyError:
                _depend = []
            return _depend

        binary_list = list(binary_list)

        binary_names = [binary_list[i:i + 300]
                        for i in range(0, len(binary_list), 300)]
        works = [gevent.spawn(job, binarys) for binarys in binary_names]
        gevent.joinall(works)
        bedepends = [value for work in works
                     for value in work.value]

        return bedepends
