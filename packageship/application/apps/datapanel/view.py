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
from flask import request
from flask import jsonify
from packageship.application.common.export import CompressIo
from packageship.application.core.datapanel.sig import SigInfo
from packageship.libs.log import LOGGER
from flask_restful import Resource
from flask import send_file
from packageship.application.common.rsp import RspMsg
from packageship.application.serialize.validate import validate
from packageship.application.serialize.datapanel import (
    ObsInfoListSchema,
    ExportObsinfoSchema,
    PrInfoListSchema,
)
from packageship.application.common.exc import (
    ElasticSearchQueryException,
    DatabaseConfigException,
)
from packageship.application.core.datapanel.obs import ObsInfo


class ObsInfoList(Resource):
    """Obtain obS building and maintenance information"""

    def get(self):
        rspmsg = RspMsg()
        result, error = validate(ObsInfoListSchema, dict(request.args), load=True)
        if error:
            response = rspmsg.body("param_error")
            return jsonify(response)
        try:
            obs = ObsInfo(**result)
            obs_infos = obs.get_obs_infos()
        except (ElasticSearchQueryException, DatabaseConfigException) as e:
            LOGGER.error(e)
            return jsonify(rspmsg.body("connect_db_error"))

        return jsonify(rspmsg.body("success", resp=obs_infos))


class PkgSuggestView(Resource):
    """Example Query the recommended software package list on the OBS build page"""

    def get(self):
        rspmsg = RspMsg()
        query = request.args.get("query")
        if not query:
            response = rspmsg.body("param_error")
            return jsonify(response)
        try:
            obs = ObsInfo()
            suggest_pkgs = obs.suggest_pkg(query=query)
        except (ElasticSearchQueryException, DatabaseConfigException) as e:
            LOGGER.error(e)
            return jsonify(rspmsg.body("connect_db_error"))

        return jsonify(rspmsg.body("success", resp=suggest_pkgs))


class BranchSuggestView(Resource):
    """Query the OBS build page gitee branch suggestion list"""

    def get(self):
        rspmsg = RspMsg()
        query = request.args.get("query")
        try:
            obs = ObsInfo()
            suggest_branch = obs.suggest_branch(query=query)
        except (ElasticSearchQueryException, DatabaseConfigException) as e:
            LOGGER.error(e)
            return jsonify(rspmsg.body("connect_db_error"))

        return jsonify(rspmsg.body("success", resp=suggest_branch))


class SigInfoList(Resource):
    """Query sig group information"""

    def get(self):
        rspmsg = RspMsg()
        sig_name = request.args.get("sig_name")
        try:
            pass
        except (ElasticSearchQueryException, DatabaseConfigException) as e:
            LOGGER.error(e)
            return jsonify(rspmsg.body("connect_db_error"))


class ExportObsInfo(Resource):
    """Export OBS information"""

    def post(self):
        rspmsg = RspMsg()
        result, error = validate(ExportObsinfoSchema, dict(request.args), load=True)
        if error:
            response = rspmsg.body("param_error")
            return jsonify(response)
        try:
            obs_csv_path = ObsInfo(**result).export_obs_info
            memory_file = CompressIo().send_memory_file(obs_csv_path)
            return send_file(
                memory_file, attachment_filename="obs-infos.zip", as_attachment=True
            )
        except (ElasticSearchQueryException, DatabaseConfigException) as e:
            LOGGER.error(e)
            return jsonify(rspmsg.body("connect_db_error"))
        except (IOError, ValueError, AttributeError, IndexError) as e:
            LOGGER.error(e)
            return jsonify(rspmsg.body("download_failed"))


class ExportSiginfo(Resource):
    """Export the sig group information"""

    def post(self):
        rspmsg = RspMsg()
        try:
            sig_csv_path = SigInfo().sig_infos_csv()
            memory_file = CompressIo().send_memory_file(sig_csv_path)
            return send_file(
                memory_file, attachment_filename="sig-infos.zip", as_attachment=True
            )
        except (ElasticSearchQueryException, DatabaseConfigException) as e:
            return jsonify(rspmsg.body("connect_db_error"))

        except (IOError, ValueError, AttributeError, IndexError) as e:
            LOGGER.error(e)
            return jsonify(rspmsg.body("download_failed"))


class PrInfoList(Resource):
    """Query pr and maintenance information about a software package"""

    def get(self):
        result, error = validate(PrInfoListSchema, dict(request.args), load=True)
