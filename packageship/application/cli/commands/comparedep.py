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

from packageship.application.cli.base import BaseCommand
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
            dict(name='-dbs', help='database to be compared,The first database is the benchmark database, '
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
