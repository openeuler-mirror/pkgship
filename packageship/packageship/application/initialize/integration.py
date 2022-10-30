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
import yaml
import redis
from elasticsearch import helpers
from elasticsearch.exceptions import ElasticsearchException
from packageship.application.common.exc import (
    ElasticSearchInsertException,
    InitializeError,
    ResourceCompetitionError,
    RepoError,
)
from packageship.application.common.constant import (
    MAX_INIT_DATABASE,
    REDIS_CONN,
    DB_INFO_INDEX,
)
from packageship.application.query import database as db
from packageship.libs.log import LOGGER
from packageship.libs.conf import configuration

from .base import ESJson, BaseInitialize, del_temporary_file, str_hash, file_hash
from .xtp import XmlPackage


class InitializeService(BaseInitialize):
    """
    Data initialization service

    Attributes:
        _config:Repo source configuration file
        _repo: The content of the repo
        _data: Sqlite data
        _fail: Failed to initialize the database
        _success: The result of the initialization
    """

    def __init__(self):
        self._config = RepoConfig()
        self._repo = dict()
        self._data = None
        self._fail = []
        self._success = False
        self._archive_database = None
        self._database_info = ESJson(
            database_name=None,
            priority=0,
            hash_addr=None,
            src_dbfile_hash=None,
            bin_dbfile_hash=None,
            db_file_hash=None,
            file_list_hash=None,
        )
        self.remove_error = dict()
        self.reindex_error = []

    @property
    def success(self):
        """
        Description: Successfully initialize the database

        """
        if not self._fail and not any([self.remove_error, self.reindex_error]):
            self._success = True
        return self._success

    @property
    def fail(self):
        """
        Description: Failed database initialization

        """
        databases = []
        for failed_index in self._fail:
            databases.extend(list(failed_index.keys()))
        return databases

    @staticmethod
    def _clear_redis_cache():
        try:
            if REDIS_CONN.keys("pkgship_*"):
                REDIS_CONN.delete(*REDIS_CONN.keys("pkgship_*"))
        except redis.RedisError:
            LOGGER.error(
                "There is an exception in Redis service. Please check it later."
                " After restart , please check the key value with pkgship_ prefix"
            )

    @staticmethod
    def _process():
        _ps = os.popen("ps -ef | grep -v grep | grep 'pkgship init'").readlines()
        if len(_ps) > 1:
            raise ResourceCompetitionError(
                "Multiple processes are initializing at the same time, Resource contention error ."
            )

    def _remove_error(self, dbname):
        self.remove_error[
            dbname
        ] = f"Please manually remove indexes starting with {dbname}."

    def _xml_parse(self, xml, filelist):
        self._data = XmlPackage(xml, filelist).parse()
        if not all(
            [
                key in self._data
                for key in (
                    "src_pack",
                    "src_requires",
                    "bin_pack",
                    "bin_requires",
                    "bin_provides",
                )
            ]
        ):
            raise RepoError(
                "The information in the REPo source is incomplete and partial dependent data is missing:%s"
                % self.elastic_index
            )

    def is_update(self, hash_addr, repo_files):
        self._database_info.hash_addr = hash_addr
        file_list = repo_files["filelist"]

        self._database_info.file_list_hash = file_hash(file_list)
        if not repo_files["xml"] or isinstance(repo_files["xml"], list):
            self._database_info.src_dbfile_hash = file_hash(self._repo["src_db_file"])
            self._database_info.bin_dbfile_hash = file_hash(self._repo["bin_db_file"])
            compare_xml = False
        else:
            self._database_info.db_file_hash = file_hash(repo_files["xml"])
            compare_xml = True

        if not self._archive_database:
            LOGGER.info("No archived database exists.")
            return True
        return self._update_compore(hash_addr, compare_xml)

    def _update_compore(self, hash_addr, compare_xml=False):
        def compare(database):
            compare_list = [
                database["db_file_hash"] == self._database_info.db_file_hash,
                database["file_list_hash"] == self._database_info.file_list_hash,
                database["src_dbfile_hash"] == self._database_info.src_dbfile_hash,
                database["bin_dbfile_hash"] == self._database_info.bin_dbfile_hash,
            ]
            return all(compare_list[:2]) if compare_xml else all(compare_list[1:])

        def remove_archive_database(dbname):
            self._archive_database = [
                _database
                for _database in self._archive_database
                if _database["database_name"] != dbname
            ]

        for _database in self._archive_database:
            if _database["database_name"] == self._repo["dbname"]:
                if _database["hash_addr"] != hash_addr:
                    if self._delete_index(self._repo["dbname"]):
                        self._remove_error(_database["database_name"])
                    remove_archive_database(_database["database_name"])
                    LOGGER.warning(
                        f"The configuration file path has been updated,database name {self._repo['dbname']}"
                    )
                    return True
                if compare(_database):
                    self._insert_database_info()
                    remove_archive_database(_database["database_name"])
                    LOGGER.info(
                        f"The contents of initialization files are consistent,database name {self._repo['dbname']}"
                    )
                    return False
                else:
                    if self._delete_index(self._repo["dbname"]):
                        self._remove_error(_database["database_name"])
                    remove_archive_database(_database["database_name"])
                    LOGGER.warning(
                        f"The file path remains the same, but the content is updated,database name {self._repo['dbname']}"
                    )
                    return True

            if _database["hash_addr"] == hash_addr:
                if compare(_database):
                    LOGGER.info(
                        "The contents of the initialization file are the same, but the database name has been updated. "
                        + f"Archived database:{ _database['database_name']} Update database: {self._repo['dbname']}"
                    )
                    if self._reindex(_database["database_name"], self._repo["dbname"]):
                        if self._delete_index(_database["database_name"]):
                            LOGGER.warning(
                                f"Index renaming creates redundant data,please manually \
                                    remove indexes starting with {_database['database_name']}"
                            )
                            self._remove_error(_database["database_name"])

                        self._insert_database_info()
                    else:
                        self.reindex_error.append(
                            {
                                "message": f"The data in database {self._repo['dbname']} is the same \
                                as that in database {_database['database_name']}, but renaming fails",
                                "reindex": f"{_database['database_name']} TO {self._repo['dbname']}",
                                "del_index": [
                                    _database["database_name"],
                                    self._repo["dbname"],
                                ],
                            }
                        )
                        if self._delete_index(self._repo["dbname"]):
                            self._remove_error(self._repo["dbname"])
                        self._insert_database_info(dbname=_database["database_name"])

                    remove_archive_database(_database["database_name"])
                    return False
                else:
                    LOGGER.warning(
                        f"The file path remains the same, but the content is updated,\
                        database name {self._repo['dbname']}"
                    )
                    if self._delete_index(_database["database_name"]):
                        self._remove_error(_database["database_name"])
                    remove_archive_database(_database["database_name"])
                    return True
        LOGGER.warning(
            f"The database name and address of the repo have been changed, dbname: {self._repo['dbname']}."
        )
        return True

    def _insert_database_info(self, index="databaseinfo", dbname=None):
        self._database_info.database_name = dbname or self._repo["dbname"]
        self._database_info.priority = self._repo["priority"]
        try:
            self._session.insert(index=index, body=self._database_info)
        except ElasticSearchInsertException as error:
            LOGGER.error(f"Insert databaseinfo error: {error}")

    def import_depend(self, path=None):
        """
        Description: Initializes import dependency data

        Args:
            path: repo source file
        """
        # Initialize the judgment of the process
        self._process()

        if not path:
            path = configuration.INIT_CONF_PATH
        try:
            self._config.load_config(path)
        except (ValueError, FileNotFoundError) as error:
            raise InitializeError(str(error)) from error
        if not self._config.validate:
            raise InitializeError(self._config.message)

        # Clear the cached value for a particular key
        self._clear_redis_cache()
        self._archive_database = db.get_all_archive_database()
        if self._archive_database:
            self._session.delete_index([DB_INFO_INDEX])

        for repo in self._config:
            self._insert_initialize_data(repo)

        for _database in self._archive_database:
            if self._delete_index(_database["database_name"]):
                LOGGER.warning(
                    f"Please manually remove indexes starting with {_database['database_name']}."
                )
                self._remove_error(_database["database_name"])

    def _insert_initialize_data(self, repo):
        self._data = ESJson()
        self._repo = repo
        hash_addr = str_hash(
            content=repo.get("src_db_file", "")
            + repo.get("bin_db_file", "")
            + repo.get("db_file", "")
        )
        try:
            if not self._repo_files():
                raise RepoError("Repo source data error: %s" % self.elastic_index)
            xml_files = self._xml()
            if not self.is_update(hash_addr, xml_files):
                LOGGER.warning(
                    f"The database content is not updated and does not need \
                     to be reconstructed, database name: {self._repo['dbname']}"
                )
                return

            if xml_files["xml"] and xml_files["filelist"]:
                self._xml_parse(**xml_files)

            self._save()
            self._session.update_setting()
        except (RepoError, ElasticsearchException) as error:
            LOGGER.error(error)
            self._fail.append(
                {self.elastic_index: f"Failed to initialize data: {self.elastic_index}"}
            )
            if isinstance(error, ElasticsearchException):
                self._delete_index()
        finally:
            # delete temporary directory
            del_temporary_file(configuration.TEMPORARY_DIRECTORY, folder=True)
            self._repo = None

    def _source_depend(self):
        """
        Description: Source package dependencies

        """
        sources = []
        for _, src_pack in self._src_pack.items():
            es_json = ESJson()
            es_json.update(src_pack)
            es_json["requires"] = self._build_requires(src_pack["pkgKey"])
            try:
                location_href = src_pack["location_href"].split("/")[-1]
                for bin_pack in self._bin_pack["sources"].get(location_href, []):
                    _subpacks = dict(name=bin_pack["name"], version=bin_pack["version"])
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
            bin_pack["src_name"] = self._src_location[bin_pack["src_name"]]["name"]
            if isinstance(bin_pack["src_name"], ESJson):
                bin_pack["src_name"] = None

            be_depends.append(self._be_depend(bin_pack))
            es_json = ESJson()
            es_json.update(bin_pack)

            es_json["provides"] = self._provides(bin_pack["pkgKey"])
            es_json["files"] = self._binpack_files(bin_pack["pkgKey"])
            es_json["filelists"] = self._files.get(bin_pack["pkgKey"], [])
            es_json["requires"] = []
            src_pack = self._src_pack.get(bin_pack["src_name"])
            if src_pack:
                es_json["src_version"] = (
                    src_pack.get("version") if src_pack.get("version") else None
                )
                es_json["requires"] = self._build_requires(src_pack["pkgKey"])

            es_json["requires"] = es_json["requires"] + self._install_requires(bin_pack)

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
                    component_json["build_require"].append(
                        {
                            "req_src_name": _src_pack["name"] or None,
                            "req_src_version": _src_pack["version"] or None,
                        }
                    )

            except (TypeError, AttributeError):
                pass

        def _install(component_json, provide):
            component_json["install_require"] = list()
            try:
                for require in self._bin_requires.get(provide["name"]):
                    _bin_pack = self._bin_pack["pkg_key"][require["pkgKey"]]
                    _src_pack = self._src_location[_bin_pack["src_name"]]
                    if not _src_pack:
                        _src_pack = self._src_pack[_bin_pack["src_name"]]
                    component_json["install_require"].append(
                        {
                            "req_bin_name": _bin_pack["name"],
                            "req_bin_version": _bin_pack["version"],
                            "req_src_name": _src_pack["name"] or None,
                            "req_src_version": _src_pack["version"] or None,
                        }
                    )
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

        for provide in self._bin_provides.get(bin_pack["pkgKey"], []):
            component_json = dict()
            component_json["component"] = provide["name"]
            _build(component_json, provide)
            _install(component_json, provide)
            es_json["provides"].append(component_json)

        return self._es_json("-bedepend", es_json)

    def _import_error(self, error, record=True):
        if record:
            LOGGER.error(error)
        self._fail.append(
            {self.elastic_index: f"Failed to initialize data: {self.elastic_index}"}
        )
        fails = self._delete_index()
        if fails:
            LOGGER.warning("Delete the failed ES database:%s ." % fails)
            self._remove_error(dbname=self.elastic_index)

    def _save(self):
        """
        Description: Save dependencies and dependencies between source packages, binary packages

        """
        fails = self._create_index(("source", "binary", "bedepend"))
        if fails:
            self._fail.append(
                {self.elastic_index: f"Failed to create index: {self.elastic_index}"}
            )
            return

        try:
            self._source_depend()
            self._binary_depend()
        except (
            TypeError,
            AttributeError,
            ElasticsearchException,
            sqlite3.DatabaseError,
        ) as error:
            self._import_error(error=error)
        else:
            self._insert_database_info()

    def _es_json(self, index, source, _type="_doc"):
        """
        Description: A JSON document for the ES database

        """
        return {
            "_index": str(self._repo["dbname"] + index).lower(),
            "_type": _type,
            "_source": source,
        }

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
            for bin_require in self._bin_requires.get(bin_pack["pkgKey"]):
                bin_require["requires_type"] = "install"
                install_requires.append(bin_require)

        except TypeError:
            pass
        return install_requires

    def _provides(self, key):
        try:
            _provides = [provide for provide in self._bin_provides.get(key)]
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
                table="src_pack",
                database=self._repo["src_db_file"],
                sql=sql,
                key="name",
            )
        return self._data.src_pack

    @property
    def _src_pkgkey(self):
        if not self._data.src_pkgkeys:
            for _, src_pack in self._src_pack.items():
                self._data.src_pkgkeys[src_pack["pkgKey"]] = src_pack
        return self._data.src_pkgkeys

    @property
    def _src_location(self):
        if not self._data.src_location:
            for _, package in self._src_pack.items():
                key = package["location_href"].split("/")[-1]
                self._data["src_location"][key] = package
        return self._data.src_location

    @property
    def _src_requires(self):
        """
        Description: Query source package dependent SQL

        """
        sql = "select * from requires"
        if not self._data.src_requires:
            self._query(
                table="src_requires",
                database=self._repo["src_db_file"],
                sql=sql,
                key=("pkgKey", "name"),
            )
        return self._data.src_requires

    @property
    def _bin_pack(self):
        """
        Description: SQL to query binary package data

        """
        sql = "select * from packages"
        if not self._data.bin_pack:
            self._query(
                table="bin_pack",
                database=self._repo["bin_db_file"],
                sql=sql,
                key="name",
            )
        return self._data.bin_pack

    @property
    def _bin_requires(self):
        """
        Description: Query SQL that relies on data for binary packages

        """
        sql = "select * from requires"
        if not self._data.bin_requires:
            self._query(
                table="bin_requires",
                database=self._repo["bin_db_file"],
                sql=sql,
                key=("pkgKey", "name"),
            )
        return self._data.bin_requires

    @property
    def _bin_provides(self):
        """
        Description: Query SQL for components provided by the binary package

        """
        sql = "select * from provides"
        if not self._data.bin_provides:
            self._query(
                table="bin_provides",
                database=self._repo["bin_db_file"],
                sql=sql,
                key=("name", "pkgKey"),
            )
        return self._data.bin_provides

    @property
    def _bin_files(self):
        """
        Description: SQL for querying binaries

        """
        sql = "select * from files"
        if not self._data.bin_files:
            self._query(
                table="bin_files",
                database=self._repo["bin_db_file"],
                sql=sql,
                key=("pkgKey",),
            )
        return self._data.bin_files

    @property
    def _files(self):
        """
        Description: SQL for the file collection

        """
        sql = "select * from filelist"
        if not self._data.files:
            self._query(
                table="files",
                database=self._repo["file_list"],
                sql=sql,
                key=("pkgKey",),
            )
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
            rpm_sourcerpm = row_data.get("rpm_sourcerpm")
            row_data["src_name"] = rpm_sourcerpm
            self._data[table]["packages"][row_data[key]] = row_data
            self._data[table]["pkg_key"][row_data["pkgKey"]] = row_data
            if rpm_sourcerpm:
                if isinstance(self._data[table]["sources"][rpm_sourcerpm], ESJson):
                    self._data[table]["sources"][rpm_sourcerpm] = [row_data]
                else:
                    self._data[table]["sources"][rpm_sourcerpm].append(row_data)

        def join_files(row_data, table):

            if isinstance(self._data[table][row_data["pkgKey"]], ESJson):
                self._data[table][row_data["pkgKey"]] = []

            file_names = row_data["filenames"].split("/")
            for index, file_type in enumerate(row_data["filetypes"]):
                file = dict(
                    file=row_data["dirname"] + "/" + file_names[index],
                )
                if file_type == "f":
                    file["filetype"] = "file"
                if file_type == "d":
                    file["filetype"] = "dir"
                self._data[table][row_data["pkgKey"]].append(file)

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
                "file is encrypted or is not a database:%s" % database
            ) from error

        for row in data.fetchall():
            row_data = dict(zip(columns, row))
            # Whether the combined data needs to be iterable
            if table == "bin_pack":
                combination_binary(row_data)
            elif table == "files":
                join_files(row_data=row_data, table=table)
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

        # A url that matches whether the file is HTTPS or this file is a local file
        self._url_or_path = (
            r"^((ht|f)tp(s?)|file)\:\/\/(\/?)[0-9a-zA-Z]([-.\w]*[0-9a-zA-Z])"
            r"*(:(0-9)*)*(\/?)([a-zA-Z0-9\-\.\?\,\'\/\\\+&amp;%$#_]*)?"
        )
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
            self._message.append(str(error))

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
                "The configuration source for the data dependency initialization is not specified"
            )

        if not os.path.exists(path):
            raise FileNotFoundError(
                "system initialization configuration file " "does not exist: %s" % path
            )
        # load yaml configuration file
        with open(path, "r", encoding="utf-8") as file_context:
            try:
                self._repo = yaml.safe_load(file_context.read())
            except yaml.YAMLError as yaml_error:
                LOGGER.error(yaml_error)
                raise ValueError(
                    "The format of the yaml configuration "
                    "file is wrong please check and try again:{0}".format(yaml_error)
                ) from yaml_error

    def _validate_priority(self, repo):
        """
        Description: Priority validation in the REPO source

        """
        _priority = repo.get("priority")
        if not _priority:
            raise TypeError(
                "The database priority of %s does not exist ." % repo.get("dbname", "")
            )

        if not isinstance(_priority, int):
            raise TypeError(
                "priority of database %s must be a integer number ."
                % repo.get("dbname", "")
            )
        if _priority < 1 or _priority > 100:
            raise ValueError(
                "priority range of the database can only be between 1 and 100 ."
            )

    def _validate_filepath(self, repo):
        """
        Description: validation of file path

        Args:
            repo: content of the repo
        """

        if not re.match(self._url_or_path, repo.get("src_db_file", "")):
            raise ValueError(
                "The 'src_db_file' configuration item in the %s database "
                "has an incorrect value ." % repo.get("dbname", "")
            )
        if not re.match(self._url_or_path, repo.get("bin_db_file", "")):
            raise ValueError(
                "The 'bin_db_file' configuration item in the %s database "
                "has an incorrect value ." % repo.get("dbname", "")
            )

    def _validate_xml(self, repo):

        if not re.match(self._url_or_path, repo.get("db_file", "")):
            raise ValueError(
                "The 'xml' configuration item in the %s database "
                "has an incorrect value ." % repo.get("dbname", "")
            )

    def _validate_database(self):
        """
        Description: Determine if the same database name exists

        """
        try:
            databases = [database["dbname"] for database in self._repo]
        except (KeyError, TypeError) as error:
            raise ValueError(
                "The initialized configuration file is incorrectly"
                " formatted and lacks the necessary dbname field ."
            ) from error

        if databases.count(None) != 0:
            raise ValueError(
                "The name of the database that the configuration item did "
                "not specify in the initialized configuration file ."
            )

        databases = set([db for db in databases if db])
        if len(databases) != len(self._repo):
            raise ValueError(
                "There is a duplicate initialization configuration database name ."
            )
        if not "".join(databases).islower():
            raise ValueError(
                "The initialized database name cannot contain uppercase characters ."
            )

    def _validation_content(self):
        """
        Description: Verify the contents of the file, logging the
                     error items in the configuration file

        """
        if not self._repo:
            raise ValueError(
                "content of the database initialization configuration file cannot be empty ."
            )
        if not isinstance(self._repo, list):
            raise ValueError(
                "format of the initial database configuration file is incorrect."
                " When multiple databases need to be initialized,"
                " it needs to be configured in the form of multiple ."
            )
        if len(self._repo) > MAX_INIT_DATABASE:
            raise ValueError(
                "The initial database supports up to 500, please control the number."
            )
        self._validate_database()
        for repo in self._repo:
            try:
                if not isinstance(repo, dict):
                    raise TypeError(
                        "The database %s configuration item is not formatted correctly ."
                        % repo.get("dbname", "")
                    )
                self._validate_priority(repo)
                if "db_file" in repo:
                    self._validate_xml(repo)
                else:
                    self._validate_filepath(repo)

            except (ValueError, TypeError) as error:
                self._message.append(str(error))
