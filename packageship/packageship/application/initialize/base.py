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
import hashlib
import shutil
from packageship.application.database.session import DatabaseSession
from packageship.application.common.exc import ElasticSearchInsertException, RepoError
from packageship.libs.log import LOGGER
from .repo import RepoFile


def del_temporary_file(path, folder=False):
    """
    Description: Delete temporary files or folders

    Args:
        path: temporary files or folders
        folder: file or folder, fsiles are deleted by default
    """
    if not os.path.exists(path):
        return
    try:
        if folder:
            shutil.rmtree(path)
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


def file_hash(file_path: str, hash_method=hashlib.md5) -> str:
    if not os.path.isfile(file_path):
        LOGGER.error("Not a file or file does not exist: %s" % file_path)
        return None
    hash_func = hash_method()
    with open(file_path, "rb") as file:
        while file_bit := file.read(1024):
            hash_func.update(file_bit)
    return hash_func.hexdigest()


def str_hash(content: str, encoding: str = "UTF-8", hash_method=hashlib.md5) -> str:
    return hash_method(content.encode(encoding)).hexdigest()


class BaseInitialize:
    """
    Initialize the base class of the service, which is
    used to initialize file fetching, ES index creation、 deletion

    """

    _session = DatabaseSession().connection()

    @property
    def elastic_index(self):
        """elastic index name"""
        return self._repo["dbname"]

    def _index(self, index):
        return self.elastic_index + "-" + index

    def _create_index(self, indexs):
        """
        Description: Initializes the relevant index

        """
        _path = os.path.join(os.path.dirname(__file__), "mappings")
        _indexs = [
            {
                "file": os.path.join(_path, index + ".json"),
                "name": self._index(index),
            }
            for index in indexs
        ]
        fails = self._session.create_index(_indexs)
        if fails:
            LOGGER.warning(
                "Failed to create the %s index when initializing the %s database ."
                % (",".join(fails), self.elastic_index)
            )
            del_index = set([self._index(index) for index in indexs]).difference(
                set(fails)
            )
            self._session.delete_index(list(del_index))
        return fails

    def _delete_index(self, index_name=None):
        """
        Description: Delete dependencies related indexes

        """
        if not index_name:
            index_name = self.elastic_index
        index_extend = ("source", "binary", "bedepend")
        fails = self._session.delete_index(
            [index_name + "-" + index for index in index_extend]
        )
        return fails

    def _reindex(self, old_index, new_index):
        index_extend = ("source", "binary", "bedepend")
        try:
            for extend in index_extend:
                self._session.reindex(
                    old_index + "-" + extend, new_index + "-" + extend
                )
            return True
        except ElasticSearchInsertException:
            return False

    def _repo_files(self):
        xml = True if "db_file" in self._repo else False
        try:
            self._find_files(xml=xml)
        except (FileNotFoundError, ValueError) as error:
            LOGGER.error(error)
            return False

        if xml:
            exists = all([self._repo["file_list"], self._repo["db_file"]])
        else:
            exists = self._sqlite()

        return exists

    def _find_files(self, xml=False):
        """Find the file configured in the repo source"""

        if "src_db_file" in self._repo:
            self._repo["src_db_file"] = RepoFile.files(path=self._repo["src_db_file"])

        filelist = self._repo["db_file"] if xml else self._repo["bin_db_file"]
        # xml repo or sqlite repo
        if xml:
            self._repo["db_file"] = RepoFile.files(path=self._repo["db_file"])
        else:
            self._repo["bin_db_file"] = RepoFile.files(path=self._repo["bin_db_file"])

        self._repo["file_list"] = RepoFile.files(path=filelist, file_type="filelists")

    def _xml(self):
        repos = dict(xml=[], filelist=self._repo["file_list"])
        # Get the XML file that meets the requirements
        keys = ("src_db_file", "bin_db_file", "file_list")
        if all([key in self._repo for key in keys]):
            extend = list(set([self._repo[key].split(".")[-1] for key in keys]))
            if len(extend) != 1:
                raise RepoError("The repo file format must be XML or SQLite")
            if extend[0] == "xml":
                repos["xml"] = [
                    self._repo[key] for key in ("src_db_file", "bin_db_file")
                ]
        else:
            repos["xml"] = self._repo["db_file"]
            if not repos["xml"].endswith("xml") or not repos["filelist"].endswith(
                "xml"
            ):
                raise RepoError(
                    "The repo file does not match the XML: %s" % self.elastic_index
                )

        return repos

    def _sqlite(self):
        repos = [
            self._repo["src_db_file"],
            self._repo["bin_db_file"],
            self._repo["file_list"],
        ]
        return all(repos)
