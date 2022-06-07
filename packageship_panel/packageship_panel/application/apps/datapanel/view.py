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
pkgship-panel display board information interface
"""
from flask import request
from flask import jsonify
from packageship.application.common.export import CompressIo
from packageship_panel.application.core.sig import SigInfo
from packageship.libs.log import LOGGER
from flask_restful import Resource
from flask import send_file
from packageship.application.common.rsp import RspMsg
from packageship.application.serialize.validate import validate
from packageship_panel.application.serialize.datapanel import (
    ObsInfoListSchema,
    ExportObsinfoSchema,
)
from packageship.application.common.exc import (ElasticSearchQueryException,
                                                DatabaseConfigException)
from packageship_panel.application.core.obs import ObsInfo


class ObsInfoList(Resource):
    """
        Obtain obS building and maintenance information
    """

    def get(self):
        """
        Get obs info
        Args:
            pkg_name: package name, if not specified, it means to query all package information.
            gitee_branch: The gitee branch where the package is located, which corresponds to the obs project one by one
            architecture: The architecture of the package
            build_state: package build status
            sig_name: sig group name
            page_index: page number for pagination query
            page_size: The size of each page when querying by pagination
        Returns:
             for example:
                {
                    "pkg_infos": [
                        {
                            "repo_name": "",
                            "source_name": "",
                            "gitee_version": "",
                            "obs_version": "",
                            "architecture": "",
                            "gitee_branch": "",
                            "obs_branch": ""
                            "build_state": "",
                            "build_detail_link": "",
                            "build_time":
                            "history_build_times": [],
                            "sig_name": "Compiler",
                            "mainttainer": [
                                {
                                    "id": "",
                                    "organization": "",
                                    "email": ""
                                }],
                            "build_requires": []
                        }
                    ],
                    "pkg_build_states": {
                        "unresolvable": ,
                        "broken": ,
                        "blocked": ,
                        "building": ,
                        "excluded":
                    },
                    "pkg_build_times": {
                        "less_ten": ,
                        "ten_to_twenty": ,
                        "twenty_to_thirty": ,
                        "more_thirty":
                    },
                    "iso_info":[
                        {
                            "branch":"",
                            "date": "",
                            "build_result": "",
                            "build_time":
                        },
                        {
                            "branch":"",
                            "date": "",
                            "build_result": "",
                            "build_time": null
                        }
                    ]
                }
        """
        rspmsg = RspMsg()
        result, error = validate(ObsInfoListSchema, dict(request.args), load=True)
        if error:
            response = rspmsg.body("param_error")
            return jsonify(response)
        try:
            obs = ObsInfo(**result)
            obs_infos = obs.get_obs_infos()
        except (ElasticSearchQueryException, DatabaseConfigException, TypeError, KeyError) as error:
            LOGGER.error(error)
            return jsonify(rspmsg.body("connect_db_error"))
        return jsonify(rspmsg.body("success", resp=obs_infos))


class PkgSuggestView(Resource):
    """
        Example Query the recommended software package list on the OBS build page
    """

    def get(self):
        """
        Fuzzy matching package name
        Args:
            query: query condition
        Returns:
            ["suggest1","suggest2","suggest3"]
        """
        rspmsg = RspMsg()
        query = request.args.get("query")
        if not query:
            response = rspmsg.body("param_error")
            return jsonify(response)
        try:
            obs = ObsInfo()
            suggest_pkgs = obs.suggest_pkg(query=query)
        except (ElasticSearchQueryException, DatabaseConfigException, TypeError) as error:
            LOGGER.error(error)
            return jsonify(rspmsg.body("connect_db_error"))

        return jsonify(rspmsg.body("success", resp=list(set(suggest_pkgs))))


class BranchSuggestView(Resource):
    """
        Query the OBS build page gitee branch suggestion list
    """

    def get(self):
        """
        Fuzzy matching branch name
        Args:
            query: query condition
        Returns:
            ["suggest1","suggest2","suggest3"]
        """
        rspmsg = RspMsg()
        query = request.args.get("query")
        try:
            obs = ObsInfo()
            suggest_branch = obs.suggest_branch(query=query)
        except (ElasticSearchQueryException, DatabaseConfigException, TypeError) as error:
            LOGGER.error(error)
            return jsonify(rspmsg.body("connect_db_error"))

        return jsonify(rspmsg.body("success", resp=list(set(suggest_branch))))


class SigInfoList(Resource):
    """Query sig group information"""

    def get(self):
        """
        Querying sig group information
        Args:
            sig_name: sig group name
        Returns:
            for example:
                [{
                    "name": "",
                    "description": "",
                    "maintainer": [
                        {
                            "id": "",
                            "organization": "",
                            "email": ""
                        }],
                    "contributors": [
                        {
                            "id": "",
                            "organization": "",
                            "email": ""
                        }
                    ],
                    "repositories": []
                }]
        """
        rspmsg = RspMsg()
        sig_name = request.args.get("sig_name")
        try:
            sig_infos = SigInfo().sig_infos(sig_name)
        except (ElasticSearchQueryException, DatabaseConfigException) as error:
            LOGGER.error(error)
            return jsonify(rspmsg.body("connect_db_error"))
        return jsonify(rspmsg.body("success", resp=sig_infos))


class ExportObsInfo(Resource):
    """
    Export OBS information
    """

    def post(self):
        """
        obs file information export
        Args:
            pkg_name: package name, if not specified, it means to query all package information.
            gitee_branch: The gitee branch where the package is located,
                          which corresponds to the obs project one by one
            architecture: The architecture of the package
            build_state: package build status
            sig_name: sig group name
        Returns:
            file stream
        """
        rspmsg = RspMsg()
        result, error = validate(ExportObsinfoSchema, request.get_json(), load=True)
        if error:
            response = rspmsg.body("param_error")
            return jsonify(response)
        try:
            obs_csv_path = ObsInfo(**result).export_obs_info_csv()

            memory_file = CompressIo().send_memory_file(obs_csv_path)
            return send_file(
                memory_file, attachment_filename="obs-infos.zip", as_attachment=True)
        except (ElasticSearchQueryException, DatabaseConfigException) as error:
            LOGGER.error(error)
            return jsonify(rspmsg.body("connect_db_error"))
        except (IOError, ValueError, AttributeError, IndexError, TypeError, OSError) as error:
            LOGGER.error(error)
            return jsonify(rspmsg.body("download_failed"))


class ExportSiginfo(Resource):
    """
    Export the sig group information
    """

    def post(self):
        """
        sig file information export
        Args:

        Returns:
            file stream
        """
        rspmsg = RspMsg()
        try:
            sig_csv_path = SigInfo().sig_infos_csv()
            memory_file = CompressIo().send_memory_file(sig_csv_path)
            return send_file(
                memory_file, attachment_filename="sig-infos.zip", as_attachment=True
            )
        except (ElasticSearchQueryException, DatabaseConfigException) as error:
            LOGGER.error(error)
            return jsonify(rspmsg.body("connect_db_error"))

        except (IOError, ValueError, AttributeError, IndexError, TypeError) as error:
            LOGGER.error(error)
            return jsonify(rspmsg.body("download_failed"))


class SigSuggestView(Resource):
    """
        Query the OBS build page gitee sig suggestion list
    """

    def get(self):
        """
        Fuzzy matching sig group name
        Args:
            query: query condition
        Returns:
            ["suggest1","suggest2","suggest3"]
        """
        rspmsg = RspMsg()
        query = request.args.get("query")
        try:
            obs = ObsInfo()
            sig_infos = obs.suggest_sig(query=query)
        except (ElasticSearchQueryException, DatabaseConfigException, TypeError) as error:
            LOGGER.error(error)
            return jsonify(rspmsg.body("connect_db_error"))

        return jsonify(rspmsg.body("success", resp=list(set(sig_infos))))
