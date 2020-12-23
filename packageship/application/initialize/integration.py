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

def del_temporary_file(path, folder=False):
    """
        delete temp file/dir
        :param path: temp file/dir path
        :param folder: file/dir, default file
    """
    pass


class InitializeService:

    @property
    def success(self):
        pass

    def import_depend(self):
        """
            import depend data while init
        """
        pass


class RepoConfig:

    @property
    def validate(self):
        """
            files validate pass or not
            :True: validate pass
            :False：validate fail
        """
        pass

    def load_config(self, config_path):
        """
            loading config file
            :param config_path: config file path
        """
        pass

    def validation_content(self):
        """
            Verify the file's contents, logging the error items in the configuration file
        """
        pass
