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
InitConf
"""
import os
import yaml
from configparser import ConfigParser
from packageship import BASE_PATH
from packageship.libs.conf import configuration


class InitConf:
    """
    InitConf
    """

    def __init__(self):
        base_path = os.path.join(os.path.dirname(BASE_PATH),
                                 "test",
                                 "common_files")
        config = ConfigParser()
        sys_path = os.environ.get('SETTINGS_FILE_PATH')
        config.read(sys_path)

        conf_path = os.path.join(base_path, "conf.yaml")
        init_dbs = os.path.join(base_path, "init_dbs")
        tem_path = os.path.join(base_path, "tem_path")
        config.set("SYSTEM", "database_folder_path", init_dbs)
        config.set("SYSTEM", "init_conf_path", conf_path)
        config.set("SYSTEM", "temporary_directory", tem_path)
        config.write(open(sys_path, "w"))

        with open(conf_path, 'r', encoding='utf-8') as r_f:
            origin_yaml = yaml.load(r_f.read(), Loader=yaml.FullLoader)

            for index, obj in enumerate(origin_yaml, 1):
                src_path = os.path.join(
                    base_path,
                    "db_origin",
                    "data_{}_src.sqlite".format(
                        str(index)))
                bin_path = os.path.join(
                    base_path,
                    "db_origin",
                    "data_{}_bin.sqlite".format(
                        str(index)))
                obj["src_db_file"] = src_path
                obj["bin_db_file"] = bin_path
            with open(conf_path, 'w', encoding='utf-8') as w_f:
                yaml.dump(origin_yaml, w_f)

        configuration.reload()


init_config = InitConf()
