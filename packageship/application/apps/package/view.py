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
from flask import request, make_response
from flask import jsonify
from flask_restful import Resource
from packageship.libs.log import LOGGER


class SourcePackages(Resource):

    def get(self):
        """

        """
        pass

class BinaryPackages(Resource):

    def get(self):
        """

        """
        pass


class SourcePackageInfo(Resource):

    def get(self, pkg_name):
        """

        """
        pass

class BinaryPackageInfo(Resource):

    def get(self, pkg_name):
        """

        """
        pass

class DatabasePriority(Resource):

    def get(self):
        pass

class PkgshipVersion(Resource):

    def get(self):
        pass

class InitSystem(Resource):

    def post(self):
        pass
