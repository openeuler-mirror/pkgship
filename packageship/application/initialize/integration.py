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
System data initialization service
"""
import os
import re
import sqlite3
import shutil
import yaml
import redis
from elasticsearch import helpers
from elasticsearch.exceptions import ElasticsearchException
from packageship.application.common.exc import InitializeError, ResourceCompetitionError
from packageship.libs.log import LOGGER
from packageship.libs.conf import configuration
# from packageship.application.query import database
from packageship.application.database.session import DatabaseSession
from packageship.application.common import constant
from .repo import RepoFile


def del_temporary_file(path, folder=False):
    """
    Description: Delete temporary files or folders

    Args:
        path: temporary files or folders
        folder: file or folder, fsiles are deleted by default
    """
    try:
        if folder:
            for file in os.listdir(path):
                file_path = os.path.join(path, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
        else:
            os.remove(path)
    except IOError as error:
        LOGGER.error(error)


class ESJson(dict):
    """
    Encapsulation of a dictionary
    """

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)

    def __getitem__(self, key):
        try:
            value = dict.__getitem__(self, key)
        except KeyError:
            value = ESJson()
            self.__setitem__(key, value)
        return value

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __getattr__(self, key):
        return self.__getitem__(key)


class InitializeService:
    """
    Data initialization service

    Attributes:
        _config:Repo source configuration file
        _repo: The content of the repo
        _data: Sqlite data
        _fail: Failed to initialize the database
        _success: The result of the initialization
        _session: es databases
    """

    def __init__(self):
        self._config = RepoConfig()
        self._repo = dict()
        self._data = None
        self._fail = []
        self._success = False
        self._session = DatabaseSession().connection()

    @property
    def success(self):
        """
        Description: Successfully initialize the database

        """
        if not self._fail:
            self._success = True
        return self._success

    @property
    def fail(self):
        """
        Description: Failed database initialization

        """
        return self._fail

    def _sqlite_file(self):
        """
        Description: sqlite file

        """
        self._repo["src_db_file"] = RepoFile.files(
            path=self._repo["src_db_file"])
        _files = self._repo["bin_db_file"]
        self._repo["bin_db_file"] = RepoFile.files(path=_files)
        self._repo["file_list"] = RepoFile.files(
            path=_files, file_type="filelists")

    def _clear_all_index(self):
        """
        Description: Clears all indexes associated with initialization

        """
        # databases = database.get_db_priority()
        databases = None
        del_databases = []
        if databases:
            for database_name in databases:
                del_databases.append(database_name + '-binary')
                del_databases.append(database_name + '-source')
                del_databases.append(database_name + '-bedepend')
        del_databases.append("databaseinfo")
        self._session.delete_index(del_databases)

    def import_depend(self, path=None):
        """
        Description: Initializes import dependency data

        Args:
            path: repo source file
        """
        _ps = os.popen(
            "ps -ef | grep -v grep | grep 'pkgship init'").readlines()
        if len(_ps) > 1:
            raise ResourceCompetitionError(
                "Multiple processes are initializing at the same time, Resource contention error .")
        if not path:
            path = configuration.INIT_CONF_PATH
        try:
            self._config.load_config(path)
        except (ValueError, FileNotFoundError) as error:
            raise InitializeError(error) from error
        if not self._config.validate:
            raise InitializeError(self._config.message)

        self._clear_all_index()
        # Clear the cached value for a particular key
        try:
            if constant.REDIS_CONN.keys('pkgship_*'):
                constant.REDIS_CONN.delete(
                    *constant.REDIS_CONN.keys('pkgship_*'))
        except redis.RedisError:
            LOGGER.error("There is an exception in Redis service. Please check it later."
                         " After restart , please check the key value with pkgship_ prefix")

        for repo in self._config:
            self._data = ESJson()
            self._repo = repo
            try:
                self._sqlite_file()
                if not all((self._repo["src_db_file"],
                            self._repo["bin_db_file"],
                            self._repo["file_list"])):
                    continue
                self._save()
            except (FileNotFoundError, ValueError, ElasticsearchException) as error:
                self._fail.append(self._repo["dbname"])
                LOGGER.error(error)
                if isinstance(error, ElasticsearchException):
                    self._delete_depend_index()
            finally:
                # delete temporary directory
                del_temporary_file(
                    configuration.TEMPORARY_DIRECTORY, folder=True)

    def _source_depend(self):
        """
        Description: Source package dependencies

        """
        sources = []
        for src_pack_name, src_pack in self._src_pack.items():
            es_json = ESJson()
            es_json.update(src_pack)
            es_json["requires"] = self._build_requires(
                src_pack['pkgKey'])
            try:
                for bin_pack in self._bin_pack['sources'].pop(src_pack_name):
                    _subpacks = dict(
                        name=bin_pack["name"], version=bin_pack["version"])
                    try:
                        es_json["subpacks"].append(_subpacks)
                    except TypeError:
                        es_json["subpacks"] = [_subpacks]
            except KeyError:
                es_json["subpacks"] = None
            sources.append(self._es_json("-source", es_json))
        helpers.bulk(self._session.client, sources)

    def _binary_depend(self):
        """
        Description: dependencies of binary packages

        """
        binarys = []
        be_depends = []
        for _, bin_pack in self._bin_pack["packages"].items():
            be_depends.append(self._be_depend(bin_pack))
            es_json = ESJson()
            es_json.update(bin_pack)

            es_json["provides"] = self._provides(bin_pack["pkgKey"])
            es_json["files"] = self._binpack_files(bin_pack['pkgKey'])
            es_json['filelists'] = self._files.get(bin_pack['pkgKey'], [])
            es_json["requires"] = []
            src_pack = self._src_pack.get(bin_pack["src_name"])
            if src_pack:
                es_json["src_version"] = src_pack.get(
                    "version") if src_pack.get("version") else None
                es_json["requires"] = self._build_requires(
                    src_pack["pkgKey"])

            es_json["requires"] = es_json["requires"] + \
                self._install_requires(bin_pack)

            binarys.append(self._es_json("-binary", es_json))
        helpers.bulk(self._session.client, binarys)
        helpers.bulk(self._session.client, be_depends)

    def _be_depend(self, bin_pack):
        """
        Description: A layer of dependencies upon which to rely

        Args:
            bin_pack:binary packages
        """

        def _build(component_json, provide):
            component_json["build_require"] = list()
            try:
                for require in self._src_requires.get(provide["name"]):
                    _src_pack = self._src_pkgkey[require["pkgKey"]]
                    component_json["build_require"].append({
                        "req_src_name": _src_pack["name"] or None,
                        "req_src_version": _src_pack["version"] or None
                    })

            except (TypeError, AttributeError):
                pass

        def _install(component_json, provide):
            component_json["install_require"] = list()
            try:
                for require in self._bin_requires.get(provide["name"]):
                    _bin_pack = self._bin_pack["pkg_key"][require["pkgKey"]]
                    _src_pack = self._src_pack[_bin_pack["src_name"]]
                    component_json["install_require"].append({
                        "req_bin_name": _bin_pack["name"],
                        "req_bin_version": _bin_pack["version"],
                        "req_src_name": _src_pack["name"] or None,
                        "req_src_version": _src_pack["version"] or None
                    })
            except (TypeError, AttributeError):
                pass

        es_json = ESJson()
        es_json["binary_name"] = bin_pack["name"]
        es_json["bin_version"] = bin_pack["version"]

        _src_pack = self._src_pack.get(bin_pack["src_name"])
        if _src_pack:
            es_json["src_name"] = _src_pack["name"] or None
            es_json["src_version"] = _src_pack["version"] or None

        es_json["provides"] = list()

        for provide in self._bin_provides.get(bin_pack["pkgKey"]):
            component_json = ESJson()
            component_json['component'] = provide["name"]
            _build(component_json, provide)
            _install(component_json, provide)
            es_json["provides"].append(component_json)

        return self._es_json("-bedepend", es_json)

    def _create_index(self, indexs):
        """
        Description: Initializes the relevant index

        """
        _path = os.path.dirname(__file__)
        _indexs = [
            {
                "file": os.path.join(_path, _index + ".json"),
                "name": self._repo["dbname"] + "-" + _index
            }
            for _index in indexs
        ]

        fails = self._session.create_index(_indexs)
        if fails:
            LOGGER.warning("Failed to create the %s index when initializing the %s database ." % (
                ','.join(fails), self._repo["dbname"]))
            del_index = set([self._repo["dbname"] + "-" +
                             index for index in indexs]).difference(set(fails))
            self._session.delete_index(list(del_index))
        return fails

    def _delete_depend_index(self):
        """
        Description: Delete dependencies related indexes

        """
        fails = self._session.delete_index([self._repo["dbname"] + "-" +
                                            index for index in
                                            ("source",
                                             "binary",
                                             "bedepend")
                                            ])
        return fails

    def _save(self):
        """
        Description: Save dependencies and dependencies between source packages, binary packages

        """
        fails = self._create_index(("source", "binary", "bedepend"))
        if fails:
            self._fail.append(self._repo["dbname"])
            return

        try:
            self._source_depend()
            self._binary_depend()
        except (TypeError, AttributeError, ElasticsearchException, sqlite3.DatabaseError) as error:
            LOGGER.error(error)
            self._fail.append(self._repo["dbname"])
            fails = self._delete_depend_index()
            if fails:
                LOGGER.warning("Delete the failed ES database:%s ." % fails)
        else:
            self._session.insert(index="databaseinfo",
                                 body={"database_name": self._repo["dbname"],
                                       "priority": self._repo["priority"]})

    def _es_json(self, index, source, _type="_doc"):
        """
        Description: A JSON document for the ES database

        """
        return {
            "_index": str(self._repo["dbname"] + index).lower(),
            "_type": _type,
            "_source": source
        }

    def _relation(self, key):
        """
        Description: Dependencies components

        Args:
            key: The key of the dependency dictionary
        """
        try:
            relation = []
            for provide in self._bin_provides.get(key):
                bin_pack = self._bin_pack['pkg_key'][provide['pkgKey']]
                relation.append(dict(
                    bin_name=bin_pack['name'],
                    src_name=bin_pack['src_name'] or None))
        except TypeError:
            relation = None
        return relation

    def _build_requires(self, pkg_key):
        """
        Description: build requires

        Args:
            pkg_key: The key of the dependency dictionary
        """
        build_requires = []
        try:
            requires = self._src_requires[pkg_key]
        except (KeyError, TypeError):
            return build_requires
        for src_require in requires:
            src_require["relation"] = self._relation(src_require['name'])
            src_require["requires_type"] = "build"
            build_requires.append(src_require)
        return build_requires

    def _install_requires(self, bin_pack):
        """
        Description: install requires

        Args:
            bin_pack: The key of the dependency dictionary
        """
        install_requires = list()
        try:
            for bin_require in self._bin_requires.get(bin_pack['pkgKey']):
                bin_require["relation"] = self._relation(bin_require['name'])
                bin_require["requires_type"] = "install"
                install_requires.append(bin_require)

        except TypeError:
            pass
        return install_requires

    def _provides(self, key):
        try:
            _provides = [
                provide for provide in self._bin_provides.get(key)]
        except TypeError:
            _provides = []

        return _provides

    def _binpack_files(self, key):
        try:
            files = [file for file in self._bin_files.get(key)]
        except TypeError:
            files = []
        return files

    @property
    def _src_pack(self):
        """
        Description: SQL to query source package data

        """
        sql = "select * from packages"
        if not self._data.src_pack:
            self._query(
                table="src_pack", database=self._repo["src_db_file"], sql=sql, key="name")
        return self._data.src_pack

    @property
    def _src_pkgkey(self):
        if not self._data.src_pkgkeys:
            for _, src_pack in self._src_pack.items():
                self._data.src_pkgkeys[src_pack["pkgKey"]] = src_pack
        return self._data.src_pkgkeys

    @property
    def _src_requires(self):
        """
        Description: Query source package dependent SQL

        """
        sql = "select * from requires"
        if not self._data.src_requires:
            self._query(table="src_requires",
                        database=self._repo["src_db_file"], sql=sql, key=("pkgKey", "name"))
        return self._data.src_requires

    @property
    def _bin_pack(self):
        """
        Description: SQL to query binary package data

        """
        sql = "select * from packages"
        if not self._data.bin_pack:
            self._query(table="bin_pack",
                        database=self._repo["bin_db_file"], sql=sql, key="name")
        return self._data.bin_pack

    @property
    def _bin_requires(self):
        """
        Description: Query SQL that relies on data for binary packages

        """
        sql = "select * from requires"
        if not self._data.bin_requires:
            self._query(table="bin_requires",
                        database=self._repo["bin_db_file"], sql=sql, key=("pkgKey", "name"))
        return self._data.bin_requires

    @property
    def _bin_provides(self):
        """
        Description: Query SQL for components provided by the binary package

        """
        sql = "select * from provides"
        if not self._data.bin_provides:
            self._query(table="bin_provides", database=self._repo["bin_db_file"], sql=sql, key=(
                "name", "pkgKey"))
        return self._data.bin_provides

    @property
    def _bin_files(self):
        """
        Description: SQL for querying binaries

        """
        sql = "select * from files"
        if not self._data.bin_files:
            self._query(
                table="bin_files", database=self._repo["bin_db_file"], sql=sql, key=("pkgKey",))
        return self._data.bin_files

    @property
    def _files(self):
        """
        Description: SQL for the file collection

        """
        sql = "select * from filelist"
        if not self._data.files:
            self._query(
                table="files", database=self._repo["file_list"], sql=sql, key=("pkgKey",))
        return self._data.files

    def _query(self, table, database, sql, key):
        """
        Description: According to different sql statements, query related table data

        Args:
            table: original table table name in SQLite
            database: Sqlite database
            sql: SQL statement for the query
            key: dictionary key value of the data map
        """

        def combination_binary(row_data):
            try:
                src_package_name = row_data.get('rpm_sourcerpm').split(
                    '-' + row_data.get('version'))[0]
                if src_package_name == row_data.get('rpm_sourcerpm'):
                    src_package_name = None
            except AttributeError:
                src_package_name = None
            row_data["src_name"] = src_package_name
            self._data[table]['packages'][row_data[key]] = row_data
            self._data[table]["pkg_key"][row_data["pkgKey"]] = row_data
            if src_package_name:
                if isinstance(self._data[table]["sources"][src_package_name], ESJson):
                    self._data[table]["sources"][src_package_name] = [row_data]
                else:
                    self._data[table]["sources"][src_package_name].append(
                        row_data)

        def others(row_data, dict_key):
            if isinstance(dict_key, (tuple, list)):
                for key in dict_key:
                    if isinstance(self._data[table][row_data[key]], ESJson):
                        self._data[table][row_data[key]] = [row_data]
                    else:
                        self._data[table][row_data[key]].append(row_data)
            else:
                self._data[table][row_data[dict_key]] = row_data

        try:
            cursor = sqlite3.connect(database).cursor()
            data = cursor.execute(sql)
            columns = [col[0] for col in cursor.description]
        except sqlite3.DatabaseError as error:
            raise sqlite3.DatabaseError(
                "file is encrypted or is not a database:%s" % database) from error

        for row in data.fetchall():
            row_data = dict(zip(columns, row))
            # Whether the combined data needs to be iterable
            if table == "bin_pack":
                combination_binary(row_data)
            else:
                others(row_data, key)


class RepoConfig:
    """
    Repo configuration file

    Attributes:
        _repo: The contents of the repo source
        _message: verified information
    """

    def __init__(self):
        self._repo = None
        self._message = []

    @property
    def message(self):
        """
        Description: Verify the wrong message

        """
        return "\n".join([str(message) for message in self._message])

    @property
    def validate(self):
        """
        Description: mark of whether the file has been validated
                    :True: Verification
                    :False：Not through
        """
        try:
            self._validation_content()
        except ValueError as error:
            self._message.append(error)

        return False if self._message else True

    def __iter__(self):
        return self._iter_repo()

    def _iter_repo(self):
        for repo in self._repo:
            yield repo

    def load_config(self, path):
        """
        Description: Read the contents of the configuration file load each
        node data in the yaml configuration file as a list to return

        Args:
            path: Initialize the repo source configuration file for the data
        Returns:
            Initialize the contents of the database configuration file
        Raises:
            FileNotFoundError: The specified file does not exist
            TypeError: Wrong type of data
        """
        if not path:
            raise ValueError(
                "The configuration source for the data dependency initialization is not specified")

        if not os.path.exists(path):
            raise FileNotFoundError(
                "system initialization configuration file"
                "does not exist: %s" % path)
        # load yaml configuration file
        with open(path, 'r', encoding='utf-8') as file_context:
            try:
                self._repo = yaml.load(
                    file_context.read(), Loader=yaml.FullLoader)
            except yaml.YAMLError as yaml_error:
                raise ValueError(
                    "The format of the yaml configuration"
                    "file is wrong please check and try again:{0}".format(yaml_error))\
                    from yaml_error

    def _validate_priority(self, repo):
        """
        Description: Priority validation in the REPO source

        """
        if not isinstance(repo, dict):
            raise TypeError("The configuration item is not properly formatted")
        _priority = repo.get('priority')
        if not isinstance(_priority, int):
            raise TypeError(
                "priority of database %s must be a number" % repo.get("name"))
        if _priority < 1 or _priority > 100:
            raise ValueError(
                "priority range of the database can only be between 1 and 100")

    def _validate_filepath(self, repo):
        """
        Description: validation of file path

        Args:
            repo: content of the repo
        """
        # A url that matches whether the file is HTTPS or this file is a local file
        regex = r"^((ht|f)tp(s?)|file)\:\/\/(\/?)[0-9a-zA-Z]([-.\w]*[0-9a-zA-Z])"\
            r"*(:(0-9)*)*(\/?)([a-zA-Z0-9\-\.\?\,\'\/\\\+&amp;%$#_]*)?"
        if not isinstance(repo, dict):
            raise TypeError("The configuration item is not properly formatted")

        if not re.match(regex, repo.get("src_db_file", "")):
            raise ValueError(
                "The 'src_db_file' configuration item in the %s database "
                "has an incorrect value ." % repo.get("dbname", ""))
        if not re.match(regex, repo.get("bin_db_file", "")):
            raise ValueError(
                "The 'bin_db_file' configuration item in the %s database "
                "has an incorrect value ." % repo.get("dbname", ""))

    def _validate_database(self):
        """
        Description: Determine if the same database name exists

        """
        try:
            databases = set([database['dbname']
                             for database in self._repo if database['dbname']])
        except (KeyError, TypeError) as error:
            raise ValueError(
                "The initialized configuration file is incorrectly"
                " formatted and lacks the necessary dbname field .") from error
        if len(databases) != len(self._repo):
            raise ValueError(
                "There is a duplicate initialization configuration database name .")
        if not ''.join(databases).islower():
            raise ValueError(
                "The initialized database name cannot contain uppercase characters .")

    def _validation_content(self):
        """
        Description: Verify the contents of the file, logging the
                     error items in the configuration file

        """
        if not self._repo:
            raise ValueError(
                "content of the database initialization configuration file cannot be empty")
        if not isinstance(self._repo, list):
            raise ValueError("""format of the initial database configuration file isincorrect.
                                When multiple databases need to be initialized,
                                it needs to be configured in the form of multiple""")
        self._validate_database()
        for repo in self._repo:
            try:
                self._validate_priority(repo)
                self._validate_filepath(repo)
            except (ValueError, TypeError) as error:
                self._message.append(error)
