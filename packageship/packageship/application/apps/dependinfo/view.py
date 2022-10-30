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
description: Interface processing
class: DependList, DownloadFiles, DependGraph
"""
from flask import send_file
from flask import request
from flask import jsonify
from packageship.libs.log import LOGGER
from flask_restful import Resource
from packageship.application.common.rsp import RspMsg
from packageship.application.common.export import CompressIo
from packageship.application.core.depend.down_load import Download
from packageship.application.serialize.validate import validate
from packageship.application.serialize.dependinfo import DependSchema
from packageship.application.serialize.dependinfo import DownSchema

from packageship.application.core.depend import DispatchDepend
from packageship.application.common.exc import ElasticSearchQueryException, DatabaseConfigException


class DependList(Resource):
    """
    Get a list of installation, compilation, self-dependence and dependent query results
    """

    def post(self):
        """
        Query a package's all dependencies including install and build depend
        (support quering a binary or source package in one or more databases)
        Args:
            packagename: package name
            depend_type: installdep/builddep/selfdep/bedep
            parameter : Query dependent parameters
        Returns:
            for
            example:
                {
                  "code": "",
                  "data": "",
                  "msg": ""
                }
        """
        rspmsg = RspMsg()
        result, error = validate(
            DependSchema, request.get_json(), load=True, partial=("node_name", "node_type"))
        if error:
            response = rspmsg.body('param_error')
            return jsonify(response)
        try:
            depend = DispatchDepend.execute(**result)
        except (ElasticSearchQueryException, DatabaseConfigException) as e:
            return jsonify(rspmsg.body('connect_db_error'))
        result_data = depend.depend_list()
        if not result_data['binary_list'] and not result_data['source_list']:
            return jsonify(rspmsg.body('pack_name_not_found'))
        binarys_sum, sources_sum = 0, 0
        for statistics_con in result_data["statistics"]:
            binarys_sum += statistics_con["binary_sum"]
            sources_sum += statistics_con["source_sum"]
        result_data["statistics"].append(
            {"sum": "Sum", "binarys_sum": binarys_sum, "sources_sum": sources_sum})
        res_dict = rspmsg.body("success", resp=result_data)
        return jsonify(res_dict)


class DownloadFiles(Resource):
    """
    Download file
    """

    def send(self, memory_file, names, depend_type):
        """

        Args:
            memory_file:
            names:
            depend_type:

        Returns:

        """
        return send_file(memory_file,
                         download_name="{search_name}_{file_type}.zip".format(
                             search_name=names,
                             file_type=depend_type),
                         as_attachment=True)

    def _validate_data(self, depend_type, data):
        """
        Verified data
        Args:
            depend_type: depend type
            data: data

        Returns:
            result: result
            error: error
        """
        if depend_type in ["src", "bin"]:
            result, error = validate(
                DownSchema, data, load=True, partial=("packagename",))
        else:
            result, error = validate(DownSchema, data, load=True)
        return result, error

    def post(self):
        """
        Download file
        Returns:

        """
        rspmsg = RspMsg()
        data = request.get_json()
        compress_io = CompressIo()
        package_name = data.get("packagename")
        depend_type = data.get("depend_type")
        result, error = self._validate_data(depend_type, data)
        if error:
            response = rspmsg.body('param_error')
            return jsonify(response)
        try:
            if depend_type in ["src", "bin"]:
                database_name = result['parameter']["db_priority"]
                folder_path = Download().process_packages(
                    depend_type, database_name[0])
                names = "".join(database_name)
                memory_file = compress_io.send_memory_file(folder_path)
                return self.send(memory_file, names, depend_type)
            else:
                try:
                    depend = DispatchDepend.execute(**result)
                except (ElasticSearchQueryException, DatabaseConfigException) as e:
                    return jsonify(rspmsg.body('connect_db_error'))
                folder_path = depend.download_depend_files()
                names = "".join(package_name)
                if folder_path:
                    memory_file = compress_io.send_memory_file(folder_path)
                    return self.send(memory_file, names, depend_type)
                else:
                    return jsonify(rspmsg.body('pack_name_not_found'))
        except (ValueError, IOError, AttributeError) as error:
            LOGGER.error(error)
            return jsonify(rspmsg.body("download_failed"))


class DependGraph(Resource):
    """
    Specifies the binary package dependency graph fetch
    """

    def post(self):
        """
        Specifies that the binary package dependency graph gets the interface

        Args:
            packagename:The package name, binary package, or source package
            dbname:databases name
            query_type:The type of data you want to query
            selfbuild:Is a self-compiling dependency
            withsubpack:Whether the query subpackage query needs to pass this parameter
            packagetype:The type of data, mainly source or binary
            node_name:The name of the node to be queried
        Returns:
            for example:
                {
                    "code": "",
                    "data": "",
                    "msg": ""
                }
        Raises:
        """
        rspmsg = RspMsg()
        result, error = validate(DependSchema, request.get_json(), load=True)
        if error:
            response = rspmsg.body('param_error')
            return jsonify(response)
        node_name = result.pop('node_name')
        node_type = result.pop('node_type')
        try:
            depend = DispatchDepend.execute(**result)
        except (ElasticSearchQueryException, DatabaseConfigException) as e:
            return jsonify(rspmsg.body('connect_db_error'))
        graph_data = depend.depend_info_graph(
            source=node_name, package_type=node_type)
        if not graph_data['edges'] and not graph_data['nodes']:
            return jsonify(rspmsg.body('pack_name_not_found'))
        res_dict = rspmsg.body("success", resp=graph_data)
        return jsonify(res_dict)
