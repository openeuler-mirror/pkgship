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
Description: Initialization of data import
            Import the data in the sqlite database into the mysql database
Class: InitDataBase,MysqlDatabaseOperations,SqliteDatabaseOperations
"""
import os
import re
import bz2
import gzip
import tarfile
import zipfile
import shutil
import requests
import yaml
from retrying import retry
from requests.exceptions import HTTPError
from requests.exceptions import RequestException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError, InternalError
from packageship.libs.dbutils.sqlalchemy_helper import DBHelper
from packageship.libs.exception import ContentNoneException
from packageship.libs.exception import DatabaseRepeatException
from packageship.libs.exception import Error
from packageship.libs.exception import ConfigurationException
from packageship.libs.log import LOGGER
from packageship.libs.conf import configuration
from packageship.application.models.package import SrcPack
from packageship.application.models.package import DatabaseInfo
from packageship.application.models.package import BinPack
from packageship.application.models.package import BinRequires
from packageship.application.models.package import SrcRequires
from packageship.application.models.package import BinProvides
from packageship.application.models.package import BinFiles
from packageship.application.models.package import Packages
from packageship.application.models.package import FileList


class InitDataBase():
    """
    Description: Database initialization, generate multiple databases and data
                 based on configuration files

    Attributes:
        config_file_path: configuration file path
        config_file_datas: initialize the configuration content of the database
        db_type: type of database
    """

    def __init__(self, config_file_path=None):
        """
        Description: Class instance initialization

        Args:
            config_file_path: Configuration file path
        """
        self.config_file_path = config_file_path
        if self.config_file_path:
            # yaml configuration file content
            self.config_file_datas = self.__read_config_file()
        self.db_type = configuration.DATABASE_ENGINE_TYPE
        self.sql = None
        self._database = None
        self._sqlite_db = None
        self._database_engine = {
            'sqlite': SqliteDatabaseOperations,
            'mysql': MysqlDatabaseOperations
        }
        self.database_name = None
        self._tables = ['src_pack', 'bin_pack',
                        'bin_requires', 'src_requires', 'bin_provides', 'bin_files', 'filelist']
        # Create life cycle related databases and tables
        if not self.create_database(db_name='lifecycle',
                                    tables=['packages_issue',
                                            'packages_maintainer',
                                            'databases_info'],
                                    storage=True):
            raise SQLAlchemyError(
                'Failed to create the specified database and table：lifecycle')
        # A valid remote address
        # For example：<a href="http://openeuler.org/openEuler-20.03-LTS/everything/aarch64" />
        # Use the regular expression to match the remote address in the href
        self._http_regex = r"^(ht|f)tp(s?)\:\/\/[0-9a-zA-Z]([-.\w]*[0-9a-zA-Z])"\
            r"*(:(0-9)*)*(\/?)([a-zA-Z0-9\-\.\?\,\'\/\\\+&amp;%$#_]*)?"

    def __read_config_file(self):
        """
        Read the contents of the configuration file load each
        node data in the yaml configuration file as a list to return

        Returns:
            Initialize the contents of the database configuration file
        Raises:
            FileNotFoundError: The specified file does not exist
            TypeError: Wrong type of data
        """

        if not os.path.exists(self.config_file_path):
            raise FileNotFoundError(
                "system initialization configuration file"
                "does not exist: %s" % self.config_file_path)
        # load yaml configuration file
        with open(self.config_file_path, 'r', encoding='utf-8') as file_context:
            try:
                init_database_config = yaml.load(
                    file_context.read(), Loader=yaml.FullLoader)
            except yaml.YAMLError as yaml_error:

                raise ConfigurationException(
                    "The format of the yaml configuration"
                    "file is wrong please check and try again:{0}".format(yaml_error))

            if init_database_config is None:
                raise ConfigurationException(
                    'The content of the database initialization configuration file cannot be empty')
            if not isinstance(init_database_config, list):
                raise ConfigurationException(
                    "The format of the initial database configuration file"
                    "is incorrect.When multiple databases need to be initialized,"
                    "it needs to be configured in the form of multiple"
                    "nodes:{}".format(self.config_file_path))
            for config_item in init_database_config:
                if not isinstance(config_item, dict):
                    raise ConfigurationException(
                        "The format of the initial database "
                        "configuration file is incorrect, and the value "
                        "in a single node should be presented in the form "
                        "of key - val pairs:{}".format(self.config_file_path))
            return init_database_config

    def init_data(self):
        """
        Initialization of the database

        Raises:
            IOError: An error occurred while deleting the database information file
        """
        if getattr(self, 'config_file_datas', None) is None or \
                self.config_file_datas is None:
            raise ContentNoneException("The content of the database initialization"
                                       "configuration file is empty")

        if self.__exists_repeat_database():
            raise DatabaseRepeatException(
                'There is a duplicate database configuration')

        if not self.__clear_database():
            raise SQLAlchemyError(
                'Failed to delete the database, throw an exception')

        if not InitDataBase.__clear_database_info():
            raise SQLAlchemyError(
                'Failed to clear data in database_info or lifecycle database')

        for database_config in self.config_file_datas:
            if not database_config.get('dbname'):
                LOGGER.logger.error(
                    'The database name in the database initialization configuration file is empty')
                continue
            priority = database_config.get('priority')
            if not isinstance(priority, int) or priority < 0 or priority > 100:
                LOGGER.logger.error("The priority value type in the database initialization"
                                    "configuration file is incorrect")
                continue
            lifecycle_status_val = database_config.get('lifecycle')
            if lifecycle_status_val not in ('enable', 'disable'):
                LOGGER.logger.error("The value of the life cycle in the initialization"
                                    "configuration file can only be enable or disable")
                continue
            # Initialization data
            self._init_data(database_config)

    def _create_database(self, db_name, tables, storage=False):
        """
        create related databases

        Args:
            database_config: Initialize the configuration content of the database_config
        Returns:
            The generated mysql database or sqlite database
        Raises:
            SQLAlchemyError: Abnormal database operation
        """
        _database_engine = self._database_engine.get(self.db_type)
        if not _database_engine:
            raise Error("The database engine is set incorrectly,"
                        "currently only the following engines are supported: %s "
                        % '、'.join(self._database_engine.keys()))
        _create_table_result = _database_engine(
            db_name=db_name, tables=tables, storage=storage).create_database(self)
        return _create_table_result

    def _get_sqlite_file(self, database_config, db_name):
        """
        Gets the path to a local or remote SQLite file
        Args:
            database_config:Initializes the contents of the configuration file
        return:
            A tuple that contains the binary, source package
            and binary collection path addresses
        """

        def src_sqlite_file(src_db_file):
            if not src_db_file:
                raise ContentNoneException(
                    "The path to the sqlite file in the database initialization"
                    "configuration is incorrect ")
            if not re.match(self._http_regex, src_db_file):
                src_db_file = src_db_file.split('file://')[-1]

            file = DownloadFile(src_db_file, 'primary', db_name + '_src')
            if re.match(self._http_regex, src_db_file):
                src_db_file = file.get_remote_file()
            else:
                src_db_file = file.get_location_file()
            return src_db_file

        def bin_sqlite_file(bin_db_file):
            if not bin_db_file:
                raise ContentNoneException(
                    "The path to the sqlite file in the database initialization"
                    "configuration is incorrect ")
            if not re.match(self._http_regex, bin_db_file):
                bin_db_file = bin_db_file.split('file://')[-1]

            file_bin = DownloadFile(
                bin_db_file, 'primary', db_name + '_bin')
            files = DownloadFile(
                bin_db_file, 'filelists', db_name + '_files')
            if re.match(self._http_regex, bin_db_file):
                bin_db_file = file_bin.get_remote_file()
                file_list = files.get_remote_file()
            else:
                bin_db_file = file_bin.get_location_file()
                file_list = files.get_location_file()
            return (bin_db_file, file_list)

        src_db_file = src_sqlite_file(database_config.get('src_db_file'))
        bin_db_file, file_list = bin_sqlite_file(
            database_config.get('bin_db_file'))

        if not all([src_db_file, bin_db_file, file_list]):
            raise ContentNoneException(
                "The path to the sqlite file in the database initialization"
                "configuration is incorrect ")
        return (src_db_file, bin_db_file, file_list)

    def _init_data(self, database_config):
        """
        data initialization operation

        Args:
            database: Initialize the configuration content of the database
        Returns:

        Raises:
            ContentNoneException: Exception with empty content
            TypeError: Data type error
            SQLAlchemyError: Abnormal database operation
            IOError: An error occurred while deleting the database information file
        """

        try:
            # 1. create a database and related tables in the database
            _db_name = database_config.get('dbname')
            _create_database_result = self._create_database(
                _db_name, self._tables)
            if not _create_database_result:
                raise SQLAlchemyError(
                    'Failed to create the specified database and table：%s'
                    % database_config['dbname'])
             # 2. get the data of binary packages and source packages
            src_db_file, bin_db_file, file_list = self._get_sqlite_file(
                database_config, _db_name)
            if not all([os.path.exists(src_db_file),
                        os.path.exists(bin_db_file),
                        os.path.exists(file_list)]):
                raise FileNotFoundError(
                    "sqlite file {src} or {bin} does not exist, please"
                    "check and try again".format(src=src_db_file, bin=bin_db_file))
            # 3. Obtain temporary source package files and binary package files
            if self.__save_data(database_config,
                                self.database_name, src_db_file, bin_db_file, file_list):
                # Update the configuration file of the database
                database_content = {
                    'database_name': _db_name,
                    'priority': database_config.get('priority'),
                }
                InitDataBase.__update_database_info(database_content)

        except (SQLAlchemyError, ContentNoneException, TypeError,
                Error, FileNotFoundError) as error_msg:
            LOGGER.logger.error(error_msg)
            # Delete the specified database
            self.__del_database(_db_name)
        finally:
            # Delete the downloaded temporary files
            DownloadFile.del_temporary_file()

    def __del_database(self, db_name):
        try:
            _database_engine = self._database_engine.get(self.db_type)
            del_result = _database_engine(db_name=db_name).drop_database()
            return del_result
        except (IOError, Error) as exception_msg:
            LOGGER.logger.error(exception_msg)
            return False

    @staticmethod
    def __columns(cursor):
        """
        functional description:Returns all the column names
        queried by the current cursor

        Args:
            cursor: Cursor
        Returns:
            The first columns
        Raises:

        """
        return [col[0] for col in cursor.description]

    def __get_data(self):
        """
        According to different sql statements, query related table data

        Args:

        Returns:

        Raises:

        """
        if self.sql is None:
            return None
        try:
            src_packages_data = self._database.session.execute(self.sql)
            columns = InitDataBase.__columns(
                src_packages_data.cursor)
            return [dict(zip(columns, row)) for row in src_packages_data.fetchall()]
        except SQLAlchemyError as sql_error:
            LOGGER.logger.error(sql_error)
            return None

    def __save_data(self, database_config, db_name, src_db_file, bin_db_file, file_list):
        """
        integration of multiple data files

        Args:
            src_package_paths: Source package database file
            bin_package_paths: Binary package database file
        Returns:
            Path of the generated temporary database file
        Raises:

        """
        table_name = database_config.get('dbname')
        lifecycle_status_val = database_config.get('lifecycle')
        try:
            with DBHelper(db_name=src_db_file, db_type='sqlite:///', complete_route_db=True) \
                    as database:
                self._database = database
                # Save data related to source package
                self._save_src_packages(
                    db_name, table_name, lifecycle_status_val)
                self._save_src_requires(db_name)

            with DBHelper(db_name=bin_db_file, db_type='sqlite:///', complete_route_db=True)\
                    as database:
                self._database = database
                # Save binary package related data
                self._save_bin_packages(db_name)
                self._save_bin_requires(db_name)
                self._save_bin_provides(db_name)
                self._save_bin_files(db_name)
            self._save_file_list(file_list, db_name)
        except (SQLAlchemyError, ContentNoneException) as sql_error:
            LOGGER.logger.error(sql_error)
            self.__del_database(db_name)
            return False
        else:
            return True

    def _save_file_list(self, file_list, db_name):
        """
        Holds a collection of binary file paths
        Args:
            file_list:The file path
            db_name:The name of the database saved
        """
        # Save filelist package
        file_list_datas = None
        with DBHelper(db_name=file_list, db_type='sqlite:///', complete_route_db=True)\
                as database:
            self._database = database
            self.sql = " select * from filelist "
            file_list_datas = self.__get_data()
        if not file_list_datas:
            raise ContentNoneException(
                "{db_name}:The binary path provided has no relevant data"
                " in the SQLite database ".format(db_name=db_name))
        with DBHelper(db_name=db_name) as database:
            database.batch_add(file_list_datas, FileList)

    def _save_src_packages(self, db_name, table_name, lifecycle_status_val):
        """
        Save the source package data

        Args:
            db_name: Saved database name
        """
        # Query all source packages
        self.sql = " select * from packages "
        packages_datas = self.__get_data()
        if packages_datas is None:
            raise ContentNoneException(
                "{db_name}:There is no relevant data in the source "
                "package provided ".format(db_name=db_name))
        for index, src_package_item in enumerate(packages_datas):
            try:
                src_package_name = '-'.join([src_package_item.get('name'),
                                             src_package_item.get('version'),
                                             src_package_item.get(
                                                 'release') + '.src.rpm'
                                             ])
            except AttributeError as exception_msg:
                src_package_name = None
                LOGGER.logger.warning(exception_msg)
            finally:
                packages_datas[index]['src_name'] = src_package_name
        with DBHelper(db_name=db_name) as database:
            database.batch_add(packages_datas, SrcPack)
        if lifecycle_status_val == 'enable':
            InitDataBase._storage_packages(table_name, packages_datas)

    @staticmethod
    def _storage_packages(table_name, package_data):
        """
            Bulk storage of source code package data
        """
        add_packages = []
        cls_model = Packages.package_meta(table_name)
        pkg_keys = ('name', 'url', 'rpm_license', 'version',
                    'release', 'summary', 'description')
        with DBHelper(db_name="lifecycle") as database:
            if table_name not in database.engine.table_names():
                database.create_table([table_name])
            # Query data that already exists in the database
            exist_packages_dict = dict()
            for pkg in database.session.query(cls_model).all():
                exist_packages_dict[pkg.name] = pkg
            _packages = []
            for pkg in package_data:
                _package_dict = {key: pkg[key] for key in pkg_keys}
                _packages.append(_package_dict)

            # Combine all package data, save or update
            for package_item in _packages:
                package_model = exist_packages_dict.get(package_item['name'])
                if package_model:
                    for key, val in package_item.items():
                        setattr(package_model, key, val)
                else:
                    add_packages.append(package_item)

            if add_packages:
                database.batch_add(add_packages, cls_model)
                database.session.commit()

    def _save_src_requires(self, db_name):
        """
        Save the dependent package data of the source package

        Args:
            db_name：Name database
        Returns:

        Raises:

        """
        # Query all source packages
        self.sql = " select * from requires "
        requires_datas = self.__get_data()
        if requires_datas is None:
            raise ContentNoneException(
                "{db_name}: The package data that the source package "
                "depends on is empty".format(db_name=db_name))
        with DBHelper(db_name=db_name) as database:
            database.batch_add(requires_datas, SrcRequires)

    def _save_bin_packages(self, db_name):
        """
        Save binary package data

        Args:
            db_name：Name database
        Returns:

        Raises:

        """
        self.sql = " select * from packages "
        bin_packaegs = self.__get_data()
        if bin_packaegs is None:
            raise ContentNoneException(
                "{db_name}:There is no relevant data in the provided "
                "binary package ".format(db_name=db_name))
        for index, bin_package_item in enumerate(bin_packaegs):
            try:
                src_package_name = bin_package_item.get('rpm_sourcerpm').split(
                    '-' + bin_package_item.get('version'))[0]
            except AttributeError as exception_msg:
                src_package_name = None
                LOGGER.logger.warning(exception_msg)
            finally:
                bin_packaegs[index]['src_name'] = src_package_name

        with DBHelper(db_name=db_name) as database:
            database.batch_add(bin_packaegs, BinPack)

    def _save_bin_requires(self, db_name):
        """
        Save the dependent package data of the binary package

        Args:
            db_name：Name database
        Returns:

        Raises:

        """
        self.sql = " select * from requires "
        requires_datas = self.__get_data()
        if requires_datas is None:
            raise ContentNoneException(
                "{db_name}:There is no relevant data in the provided binary "
                "dependency package".format(db_name=db_name))

        with DBHelper(db_name=db_name) as database:
            database.batch_add(requires_datas, BinRequires)

    def _save_bin_provides(self, db_name):
        """
        Save the component data provided by the binary package

        Args:
            db_name：Name database
        Returns:

        Raises:

        """
        self.sql = " select * from provides "
        provides_datas = self.__get_data()
        if provides_datas is None:
            raise ContentNoneException(
                "{db_name}:There is no relevant data in the provided "
                "binary component ".format(db_name=db_name))

        with DBHelper(db_name=db_name) as database:
            database.batch_add(provides_datas, BinProvides)

    def _save_bin_files(self, db_name):

        self.sql = " select * from files "
        files_datas = self.__get_data()
        if files_datas is None:
            raise ContentNoneException(
                "{db_name}:There is no relevant binary file installation "
                "path data in the provided database ".format(db_name=db_name))

        with DBHelper(db_name=db_name) as database:
            database.batch_add(files_datas, BinFiles)

    def __exists_repeat_database(self):
        """
        Determine if the same database name exists

        Returns:
            True if there are duplicate databases, false otherwise
        Raises:

        """
        db_names = [name.get('dbname')
                    for name in self.config_file_datas]

        if len(set(db_names)) != len(self.config_file_datas):
            return True

        return False

    @staticmethod
    def __update_database_info(database_content):
        """
        Update the database_name table

        Args:
            database_content:
                Dictionary of database names and priorities
        Returns:

        """
        try:
            with DBHelper(db_name="lifecycle") as database_name:
                name = database_content.get("database_name")
                priority = database_content.get("priority")
                database_name.add(DatabaseInfo(
                    name=name, priority=priority
                ))
                database_name.session.commit()
        except (SQLAlchemyError, Error, AttributeError) as error:
            LOGGER.logger.error(error)

    @staticmethod
    def __clear_database_info():
        """
            Delete the tables in the lifecycle except for the specific three tables
        Returns:

        """
        try:
            with DBHelper(db_name="lifecycle") as database_name:
                clear_sql = """delete from databases_info;"""
                database_name.session.execute(text(clear_sql))
                table_list = database_name.engine.table_names()
                for item in table_list:
                    if item not in ['packages_maintainer', 'databases_info', 'packages_issue']:
                        drop_sql = '''DROP TABLE if exists `{table_name}`'''.format(
                            table_name=item)
                        database_name.session.execute(text(drop_sql))
                database_name.session.commit()
        except SQLAlchemyError as sql_error:
            LOGGER.logger.error(sql_error)
            return False
        else:
            return True

    def __clear_database(self):
        """
            Delete database
        Returns:

        """
        try:
            with DBHelper(db_name='lifecycle') as data_name:
                name_data_list = data_name.session.query(
                    DatabaseInfo.name).order_by(DatabaseInfo.priority).all()
                name_list = [name[0] for name in name_data_list if name[0]]
                for item in name_list:
                    self.__del_database(item)
        except (SQLAlchemyError, Error, IOError) as error:
            LOGGER.logger.error(error)
            return False
        else:
            return True

    def delete_db(self, db_name):
        """
        delete the database

        Args:
            db_name: The name of the database
        Returns:

        Raises:
            IOError: File or network operation io abnormal
        """
        try:
            del_result = True
            with DBHelper(db_name='lifecycle') as database_name:
                database_name.session.query(DatabaseInfo).filter(
                    DatabaseInfo.name == db_name).delete()
                drop_sql = '''DROP TABLE if exists `{table_name}`''' \
                    .format(table_name=db_name)
                database_name.session.execute(text(drop_sql))
                database_name.session.commit()
        except SQLAlchemyError as sql_error:
            LOGGER.logger.error(sql_error)
            del_result = False
        if del_result:
            del_result = self.__del_database(db_name)
        return del_result

    def create_database(self, db_name, tables=None, storage=True):
        """
            Create databases and tables related to the package life cycle

            Args:
                db_name: The name of the database
                tables: Table to be created
        """
        _create_database_result = self._create_database(
            db_name, tables, storage)
        return _create_database_result


class MysqlDatabaseOperations():
    """
    Related to database operations, creating databases, creating tables

    Attributes:
        db_name: The name of the database
        create_database_sql: SQL statement to create a database
        drop_database_sql: Delete the SQL statement of the database
    """

    def __init__(self, db_name, tables=None, storage=False):
        """
        Class instance initialization

        Args:
            db_name: Database name
        """
        self.db_name = db_name
        self.create_database_sql = ''' CREATE DATABASE if not exists `{db_name}` \
                                    DEFAULT CHARACTER SET utf8mb4; '''.format(db_name=self.db_name)
        self.drop_database_sql = '''drop DATABASE if exists `{db_name}` '''.format(
            db_name=self.db_name)
        self.tables = tables
        self.storage = storage

    def create_database(self, init_db):
        """
        create a mysql database

        Returns:
            True if successful, otherwise false
        Raises:
            SQLAlchemyError: An exception occurred while creating the database
        """
        _create_success = True
        if isinstance(init_db, InitDataBase):
            init_db.database_name = self.db_name
        with DBHelper(db_name='mysql') as data_base:

            try:
                # create database
                if not self.storage:
                    data_base.session.execute(self.drop_database_sql)
                data_base.session.execute(self.create_database_sql)
            except InternalError as internal_error:
                LOGGER.logger.info(internal_error)
            except SQLAlchemyError as exception_msg:
                LOGGER.logger.error(exception_msg)
                return False
        if self.tables:
            _create_success = self.__create_tables()
        return _create_success

    def drop_database(self):
        """
        Delete the database according to the specified name

        Args:
            db_name: The name of the database to be deleted
        Returns:
            True if successful, otherwise false
        Raises:
            SQLAlchemyError: An exception occurred while creating the database
        """
        if self.db_name is None:
            raise IOError(
                "The name of the database to be deleted cannot be empty")
        with DBHelper(db_name='mysql') as data_base:
            drop_database = '''  drop DATABASE if exists `{db_name}` '''.format(
                db_name=self.db_name)
            try:
                data_base.session.execute(drop_database)
            except SQLAlchemyError as exception_msg:
                LOGGER.logger.error(exception_msg)
                return False
            else:
                return True

    def __create_tables(self):
        """
        Create the specified data table

        Returns:
            True if successful, otherwise false
        Raises:
            SQLAlchemyError: An exception occurred while creating the database
        """
        try:
            with DBHelper(db_name=self.db_name) as database:
                if self.tables:
                    _tables = list(set(self.tables).difference(
                        set(database.engine.table_names())))
                    database.create_table(_tables)

        except SQLAlchemyError as exception_msg:
            LOGGER.logger.error(exception_msg)
            return False
        else:
            return True


class SqliteDatabaseOperations():
    """
    sqlite database related operations

    Attributes:
        db_name: Name database
        database_file_folder: Database folder path
    """

    def __init__(self, db_name, tables=None, storage=False, ** kwargs):
        """
        Class instance initialization

        Args:
            db_name: Database name
            kwargs: data related to configuration file nodes
        """
        self.db_name = db_name
        self.database_file_folder = configuration.DATABASE_FOLDER_PATH
        if hasattr(kwargs, 'database_path'):
            self.database_file_folder = kwargs.get('database_path')
        self._make_folder()
        self.tables = tables
        self.storage = storage

    def _make_folder(self):
        """
        Create a folder to hold the database

        Raises:
            IOError: File or network operation io abnormal
        """
        if not os.path.exists(self.database_file_folder):
            try:
                os.makedirs(self.database_file_folder)
            except IOError as makedirs_error:
                LOGGER.logger.error(makedirs_error)
                self.database_file_folder = None

    def create_database(self, init_db):
        """
        create sqlite database and table

        Returns:
            After successful generation, return the database file address,
            otherwise return none
        Raises:
            FileNotFoundError: The specified folder path does not exist
            SQLAlchemyError: An error occurred while generating the database
        """
        _create_success = False
        if self.database_file_folder is None:
            raise FileNotFoundError('Database folder does not exist')

        _db_file = os.path.join(
            self.database_file_folder, self.db_name)

        if not self.storage and os.path.exists(_db_file + '.db'):
            os.remove(_db_file + '.db')

        # create a sqlite database
        with DBHelper(db_name=_db_file) as database:
            try:
                if self.tables:
                    _tables = list(set(self.tables).difference(
                        set(database.engine.table_names())))
                    database.create_table(_tables)
            except (SQLAlchemyError, InternalError) as create_table_err:
                LOGGER.logger.error(create_table_err)
                return _create_success
        if isinstance(init_db, InitDataBase):
            init_db.database_name = _db_file
            _create_success = True
        return _create_success

    def drop_database(self):
        """
        Delete the specified sqlite database

        Returns:
            Return true after successful deletion, otherwise return false
        Raises:
            IOError: An io exception occurred while deleting the specified database file
        """
        try:
            db_path = os.path.join(
                self.database_file_folder, self.db_name + '.db')
            if os.path.exists(db_path):
                os.remove(db_path)
        except IOError as exception_msg:
            LOGGER.logger.error(exception_msg)
            return False
        else:
            return True


class Unpack():
    """
    Decompression of a file is related to the operation

    Attributes:
        file_path: The path to the zip file
        save_file: The path to the saved file
    """

    def __init__(self, file_path, save_file):
        self.file_path = file_path
        self.save_file = save_file

    @classmethod
    def dispatch(cls, extend, *args, **kwargs):
        """
        Specific decompression methods are adopted for different compression packages
        Args:
            extend:The format of the compressed package
        """
        self = cls(*args, **kwargs)
        meth = getattr(self, extend[1:].lower(), None)
        if meth is None:
            raise Error(
                "Unzipping files in the current format is not supported：%s" % extend)
        meth()

    def bz2(self):
        """
        Unzip the bZ2 form of the compression package
        """
        with open(self.save_file, 'wb') as file, bz2.BZ2File(self.file_path, 'rb') as bz_file:
            for data in iter(lambda: bz_file.read(100 * 1024), b''):
                file.write(data)

    def gz(self):
        """
        Unzip the compressed package in GZIP format
        """
        with open(self.save_file, 'wb') as file, gzip.GzipFile(self.file_path) as gzip_file:
            for data in iter(lambda: gzip_file.read(100 * 1024), b''):
                file.write(data)

    def tar(self):
        """
        Unzip the tar package
        """
        with open(self.save_file, 'wb') as file, tarfile.open(self.file_path) as tar_file:
            file_names = tar_file.getnames()
            if len(file_names) != 1:
                raise IOError(
                    "Too many files in the zip file, do not"
                    " conform to the form of a single file：%s" % self.file_path)
            _file = tar_file.extractfile(file_names[0])
            for data in iter(lambda: _file.read(100 * 1024), b''):
                file.write(data)

    def zip(self):
        """
        Unzip the zip package
        """
        with open(self.save_file, 'wb') as file, zipfile.open(self.file_path) as zip_file:
            file_names = zip_file.namelist()
            if len(file_names) != 1:
                raise IOError("Too many files in the zip file, do not"
                              " conform to the form of a single file：%s" % self.file_path)
            file.write(zip_file.read())


class DownloadFile():
    """
    Download the file for the remote address
    """

    def __init__(self, url, file_type, file_name):
        if not url:
            raise Error("The path to download the file is empty")
        if not url.endswith('/'):
            url += '/'
        self.url = url + 'repodata/'
        self._file_type = file_type
        self._temporary_directory = configuration.TEMPORARY_DIRECTORY
        if not os.path.exists(self._temporary_directory):
            os.makedirs(self._temporary_directory)
        # Matches the remote download address in the Href attribute in the A tag
        self._file_regex = r'href=\"([^\"]*%s.sqlite.{3,4})\".?' % self._file_type
        self._file_remote = None
        self.file_name = file_name

    @retry(stop_max_attempt_number=3, stop_max_delay=1000)
    def __download_file(self, url):
        """
        Download the file or web page in the specified path
        Args:
            url:Remote online address
        Return:
            Successful download of binary stream
        """
        try:
            response = requests.get(url)
        except RequestException as error:
            raise RequestException(error)
        if response.status_code != 200:
            _msg = "There is an exception with the remote service [%s]，" \
                   "Please try again later.The HTTP error code is：%s" % (url, str(
                       response.status_code))
            raise HTTPError(_msg)
        return response

    @staticmethod
    def del_temporary_file():
        """
        Delete temporary files or directories
        """
        try:
            del_list = os.listdir(configuration.TEMPORARY_DIRECTORY)
            for file in del_list:
                file_path = os.path.join(
                    configuration.TEMPORARY_DIRECTORY, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
        except IOError as error:
            LOGGER.error(error)

    def _matching_remote_file(self):
        """
        Matches the filename that the remote needs to download
        """
        try:
            response = self.__download_file(self.url)
            result = re.search(
                self._file_regex, response.content.decode('utf-8'))
            if result:
                self._file_remote = self.url + result.group(1)
        except (RequestException, HTTPError)as error:
            LOGGER.error(error)

    def __unzip_file(self, file_path, file_name):
        """
        Unzip a compressed package file in a specific format
        Args:
            file_path: The path of the compression package
        """
        if not os.path.exists(file_path):
            raise Error("The unzip file does not exist：%s" % file_path)
        sqlite_file_path = os.path.join(
            os.path.dirname(file_path), file_name + ".sqlite")
        try:
            Unpack.dispatch(os.path.splitext(file_path)[-1], file_path=file_path,
                            save_file=sqlite_file_path)
            return sqlite_file_path
        except IOError as error:
            raise Error(
                "An error occurred during file decompression：%s" % error)
        finally:
            os.remove(file_path)

    def get_location_file(self):
        """
        Get the local compressed file and copy the local file to a temporary folder
        """
        # A file that matches the end of a particular character
        regex = r'.*?%s.sqlite.{3,4}' % self._file_type

        file_path = None
        for file in os.listdir(self.url):
            if os.path.isfile(os.path.join(self.url, file)) and re.match(regex, file):
                file_path = os.path.join(self._temporary_directory, file)
                shutil.copyfile(os.path.join(self.url, file), file_path)
                continue
        if file_path:
            file_path = self.__unzip_file(file_path, self.file_name)
        return file_path

    def get_remote_file(self):
        """
        Gets the remote zip file
        """
        self._matching_remote_file()
        if not self._file_remote:
            raise Error("There is no SQLite file in the specified remote"
                        " service %s that can be used for initialization" % self.url)
        try:
            response = self.__download_file(self._file_remote)
        except (RequestException, HTTPError) as error:
            LOGGER.error(error)
            raise Error("There was an error downloading file: %s, "
                        "Please try again later." % self._file_remote)
        try:
            _file_path = os.path.join(
                self._temporary_directory, self._file_remote.split('/')[-1])
            with open(_file_path, "wb") as file:
                file.write(response.content)
        except IOError as error:
            LOGGER.error(error)
            raise Error("There was an error downloading file: %s, "
                        "Please try again later." % self._file_remote)
        return self.__unzip_file(_file_path, self.file_name)
