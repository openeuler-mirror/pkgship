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
from datetime import datetime

from packageship.application.cli.base import BaseCommand
from packageship.application.core.compare.compare_repo import CompareRepo
from packageship.application.core.compare.query_depend import QueryDepend
from packageship.application.core.compare.validate import validate_args
from packageship.libs.conf import configuration


class CompareCommand(BaseCommand):
    """
    Compare the one-level dependency difference of different databases
    """

    def __init__(self):
        """
        init
        """
        super(CompareCommand, self).__init__()
        self.parse = BaseCommand.subparsers.add_parser(name='compare',
                                                       help='compare the dependency difference of different databases')
        self.params = [
            ('-t', 'str', 'dependency type of query', None, 'store'),
            ('-o', 'str', 'the storage location of the generated csv file', configuration.COMPARE_OUTPUT_FILE, 'store')
        ]
        self.collection_params = [
            dict(name='-dbs', help='database to be compared,the first database is the benchmark database, '
                                   'and the first database software package is used as a reference '
                                   'when comparing dependent information', nargs='*', default=None)
        ]

    def register(self):
        super(CompareCommand, self).register()
        self.parse.set_defaults(func=self.do_command)

    def do_command(self, args):
        """
        Perform comparison operations of packages' require on different repo
        :param args: input params
        :return: None
        """
        # Determine whether the service is started
        if not self.is_service_start():
            print("[ERROR] The pkgship service is not started,please start the service first")
            return

        depend_type = args.t
        dbs = args.dbs
        output_path = args.o
        validate_args(depend_type, dbs, output_path)
        print('[INFO] Start to compare the software package dependencies in different databases, '
              'please wait a few minutes...')
        # Query dependency information of all packages in each database
        query_dependency_engine = QueryDepend()
        all_db_dependency_info = query_dependency_engine.all_depend_info(depend_type=depend_type, dbs=dbs)
        # Path append date
        new_out_path = self._path_append(output_path)
        # Write the generated dependency information to a csv file
        compare_dependency_engine = CompareRepo(out_path=new_out_path, dbs=dbs)
        is_success = compare_dependency_engine.dbs_compare(all_db_dependency_info)
        if is_success:
            print(
                f'[INFO] The data comparison is successful, and the generated file is in the ({new_out_path}) path.')

    @staticmethod
    def _path_append(old_path):
        """
        In order to prevent the file from being overwritten, append the time to the input path
        :param old_path: input path
        :return: new path
        """
        current_time = datetime.now().strftime("%H%M%S")
        new_path = os.path.join(old_path, current_time)
        if not os.path.exists(new_path):
            os.makedirs(new_path, mode=0o755)
        return new_path
