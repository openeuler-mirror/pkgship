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
Description: query package information
"""
from packageship.application.common.exc import PackageInfoGettingError, \
    DatabaseConfigException, ElasticSearchQueryException
from packageship.application.query import database as db
from packageship.application.query.depend import BeDependRequires, InstallRequires, BuildRequires
from packageship.application.query.pkg import QueryPackage
from packageship.libs.log import LOGGER


class Package:
    """
    Get all source package info and binary package info
    """

    def __parse_pkg_info(self, package_info_dict, pkgname, database):
        """
        Parse the info of the source package or binary package
        Args:
            package_info_dict: source package info or binary package info
            name: package name
            database: database

        Returns:
                pkg_info: parsed package info
        """
        pkg_info = {
            "pkg_name": pkgname,
            "license": package_info_dict.get("license"),
            "version": package_info_dict.get("version"),
            "url": package_info_dict.get("url"),
            "database": database
        }
        return pkg_info

    def all_src_packages(self, database, page_num=1, page_size=20,
                           package_list=None, command_line=False):
        """
        get all source rpm packages base info
        Args:
            database: database
            page_num: paging query index
            page_size: paging query size
            package_list: package list name
            command_line: command_line or UI

        Returns:
            all_src_dict: all parsed source package information dict
            for example:
                {
                "total": "",
                "data": ""
                }
        Attributes:
            AttributeError: Cannot find the attribute of the corresponding object
            KeyError: key not exists
            TypeError: object does not support this property or method
        Raises:
            ElasticSearchQueryException: dataBase connect failed
            DatabaseConfigException: dataBase config error

        """
        try:
            # query all source package info from database
            query_package = QueryPackage()
            all_src_info = query_package.get_src_info(
                package_list, database, page_num, page_size, command_line)

            if not all_src_info:
                _msg = "An error occurred when querying source package info."
                raise PackageInfoGettingError(_msg)
            # parse all source package info
            parsed_all_src_info = []
            total_num = all_src_info.get("total")
            for pkg_info in all_src_info.get("data"):
                parsed_all_src_info.extend(self.__parse_pkg_info(info_values, pkgname, database)
                                           for pkgname, info_values in pkg_info.items())
            all_src_dict = {"total": total_num, "data": parsed_all_src_info}
            return all_src_dict
        except DatabaseConfigException:
            raise DatabaseConfigException()
        except ElasticSearchQueryException:
            raise ElasticSearchQueryException()
        except (AttributeError, KeyError, TypeError) as e:
            LOGGER.error(e)
            return {}

    def all_bin_packages(self, database, page_num=1, page_size=20,
                         package_list=None, command_line=False):
        """
        get all binary package info
        Args:
            database: database
            page_num: paging query index
            page_size: paging query size
            package_list: package list name
            command_line： command_line or UI
        Returns:
            all_bin_dict: all binary package information dict
            for example::
                {
                "total": "",
                "data": ""
                }
        Attributes:
            AttributeError: Cannot find the attribute of the corresponding object
            KeyError: key not exists
            TypeError: object does not support this property or method
        Raises:
            ElasticSearchQueryException: dataBase connect failed
            DatabaseConfigException: dataBase config error

        """
        try:
            # query all binary package info from database
            query_package = QueryPackage()
            all_bin_info = query_package.get_bin_info(
                package_list, database, page_num, page_size, command_line)

            if not all_bin_info:
                _msg = "An error occurred when getting bianry package info."
                raise PackageInfoGettingError(_msg)

            parsed_all_bin_info = []
            total_num = all_bin_info.get("total")
            for pkg_info in all_bin_info.get("data"):
                single_pkg = []
                for pkgname, info_values in pkg_info.items():
                    single_pkg = self.__parse_pkg_info(
                        info_values, pkgname, database)
                    single_pkg["source_name"] = info_values["src_name"]
                parsed_all_bin_info.append(single_pkg)
            all_bin_dict = {"total": total_num, "data": parsed_all_bin_info}
            return all_bin_dict
        except DatabaseConfigException:
            raise DatabaseConfigException()
        except ElasticSearchQueryException:
            raise ElasticSearchQueryException()
        except (AttributeError, KeyError, TypeError) as e:
            LOGGER.error(e)
            return {}


class SinglePackage:
    """
    class for query single package
    """

    def get_provides(self, pkgname, database):
        """
        get provides info from bedepend query result
        Args:
            pkgname: package name
            database: database

        Returns:
            provides_info_res: which include component, required_by_bin, required_by_src
            for example:
                        [{'component': 'comp1',
                        'required_by_bin': ['A1', 'B1'],
                        'required_by_src': ['T', 'R']}]
        """
        try:
            # getting bedend query res
            be_depend_obj = BeDependRequires()
            be_depend_info = be_depend_obj.get_be_req([pkgname], database)

            if not be_depend_info:
                return []
            provides_info_res = []
            depend_info = be_depend_info[0].get("provides")
            for component_info in depend_info:

                # getting required_by_bin
                install_require_info = component_info.get("install_require")
                required_by_bin = []
                for req_info in install_require_info:
                    required_by_bin.append(req_info.get("req_bin_name"))

                # getting required_by_src
                build_require_info = component_info.get("build_require")
                required_by_src = []
                for req_info in build_require_info:
                    required_by_src.append(req_info.get("req_src_name"))

                component_dict = {"component": component_info.get("component"),
                                  "required_by_bin": required_by_bin,
                                  "required_by_src": required_by_src}
                provides_info_res.append(component_dict)
            return provides_info_res
        except (TypeError, IndexError) as e:
            LOGGER.error(e)
            return []

    def get_requires(self, pkgname, database):
        """
        get requires info from install dependency
        Args:
            pkgname: package name
            database: database

        Returns:
            required_by_bin: binary package information that depends on this component
            for example:
            [{'component': 'lib.so', 'provided_by': ['libJudy']},
            {'component': 'lib4.so', 'provided_by': ['libJudy']},
            {'component': 'lib2.so', 'provided_by': ['libJudy2']}]

        Attributes:
            TypeError: object does not support this property or method

        """
        try:
            install_depend_obj = InstallRequires([database])
            install_depend_info = install_depend_obj.get_install_req(
                [pkgname], database)

            if not install_depend_info:
                return []

            depend_info = install_depend_info[0].get("requires")
            required_by_bin = []
            for component_info in depend_info:
                component_dict = {'component': component_info.get("component"),
                                  'provided_by': [component_info.get("com_bin_name")]}
                if component_dict not in required_by_bin:
                    required_by_bin.append(component_dict)
            return required_by_bin
        except TypeError as e:
            LOGGER.error(e)
            return []


class SourcePackage(SinglePackage):
    """
    class for query single source package
    """

    def get_subpack_info(self, pkgname, database, pkgname_info):
        """
            get subpacks info for source package
            Args:
                pkgname: package name
                database: database
                pkgname_info: package info which include subpacks

            Returns:
                subpacks: subpack list

        """
        subpacks_bin_list = pkgname_info[pkgname].get('subpacks')
        if not subpacks_bin_list:
            _msg = "Error in getting subpack info."
            LOGGER.error(_msg)
            return []

        subpacks = []
        for subpack_name in subpacks_bin_list:
            subpack_dict = {"bin_name": subpack_name,
                            "provides": self.get_provides(subpack_name, database),
                            "requires": self.get_requires(subpack_name, database)}
            subpacks.append(subpack_dict)
        return subpacks

    def get_build_info(self, pkgname, database):
        """
        get build dependency info
        Args:
            pkgname: package name
            database: database

        Returns:
            build_depend_info: build dependency for source package

        Attributes:
            TypeError: object does not support this property or method
        """
        try:
            build_obj = BuildRequires([database])
            build_depend = build_obj.get_build_req([pkgname], database)

            if not build_depend:
                return []

            build_depend_info = build_depend[0].get("requires")
            build_package_list = []
            for requires_info in build_depend_info:
                build_package_list.append(requires_info.get("component"))
            return build_package_list
        except (TypeError, AttributeError) as e:
            LOGGER.error(e)
            return []

    def src_package_info(self, src_name_list, database_list=None):
        """
        get a source package info (provides, requires, etc)
        Args:
            src_name_list: source package list
            database_list: database list

        Returns:
            src_package_info_res

        Attributes:
            AttributeError: Cannot find the attribute of the corresponding object
            IndexError: list index out of range
            TypeError: object does not support this property or method

        Raises:
            ElasticSearchQueryException: dataBase connect failed
            DatabaseConfigException: dataBase config error
        """
        try:
            default_db_list = db.get_db_priority()
            if not database_list:
                database_list = default_db_list

            src_package_info_res = {}
            query_package = QueryPackage()
            for database in database_list:
                single_db_src_info = query_package.get_src_info(
                    src_name_list, database, 1, 20).get("data")
                if not single_db_src_info:
                    return {}

                database_src_info_list = []
                for pkg_info in single_db_src_info:
                    pkgname = list(pkg_info.keys())[0]
                    build_package_info = self.get_build_info(pkgname, database)
                    subpacks = self.get_subpack_info(
                        pkgname, database, pkg_info)

                    database_src_info_list.append({
                        "src_name": pkgname,
                        "license": pkg_info[pkgname].get("license"),
                        "version": pkg_info[pkgname].get("version"),
                        "url": pkg_info[pkgname].get("url"),
                        "release": pkg_info[pkgname].get("release"),
                        "summary": pkg_info[pkgname].get("summary"),
                        "description": pkg_info[pkgname].get("description"),
                        "buildrequired": build_package_info,
                        "subpacks": subpacks
                    })
                src_package_info_res[database] = database_src_info_list
            return src_package_info_res
        except DatabaseConfigException:
            raise DatabaseConfigException()
        except ElasticSearchQueryException:
            raise ElasticSearchQueryException()
        except (AttributeError, IndexError, TypeError) as e:
            LOGGER.error(e)
            return {}



class BinaryPackage:

    def bin_package_info(self):
        """
            get a binary package info (provides, requires, etc)
        """
        pass
