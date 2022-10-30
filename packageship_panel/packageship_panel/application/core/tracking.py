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
import json
import asyncio
from pathlib import Path
import subprocess
from functools import reduce
import redis
import yaml
from packageship.application.common.exc import ElasticSearchQueryException
from packageship.application.database.session import DatabaseSession
from packageship.libs.conf import configuration
from packageship.application.common import constant
from packageship.libs.log import LOGGER
from packageship_panel.application.core.obs import ObsInfo
from packageship_panel.application.query.panel import PanelInfo
from packageship_panel.libs.api.gitee import GiteeApi
from packageship_panel.libs.api.obs import ObsApi


class BaseTracking:
    """Data synchronization trace base class"""

    obs = ObsApi()
    gitee = GiteeApi()
    prefix = "synchronous"
    session = DatabaseSession().connection()

    @staticmethod
    def key(sequence_val):
        """Generate cache keys"""
        if sequence_val is None:
            return ValueError("None is not a hashable value")
        return hashlib.sha256(sequence_val.encode("utf8")).hexdigest()

    @staticmethod
    def cmd(cmd_list, cwd=None):
        """
        Executing shell commands
        :param cmd_list: Command set
        :param cwd: Directory where the command is executed
        :returns: Result is a tuple,exp: (Status code,output,err)
        """
        pipe = subprocess.Popen(
            cmd_list,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=cwd,
        )
        out, err = pipe.communicate()

        return (
            pipe.returncode,
            out.decode("utf-8", errors="ignore"),
            err.decode("utf-8", errors="ignore"),
        )

    def set_cache(self, source_val):
        """
        Setting cache values
        :param source_val: Cache content
        """
        sig_key = self.prefix + "_" + self.key(source_val["name"])
        try:
            constant.REDIS_CONN.set(sig_key, json.dumps(source_val))
            for pkg in source_val["repositories"]:
                pkg = pkg.split("/")[-1]
                pkg_corresponding_sigkey = self.prefix + "_pkg_" + self.key(pkg)
                constant.REDIS_CONN.set(pkg_corresponding_sigkey, sig_key)
        except redis.ConnectionError as error:
            LOGGER.error(error)

    def get_cache(self, package):
        """
        Get cached values
        :param package: repo name
        """
        if package is None:
            return None
        pkg_corresponding_sigkey = self.prefix + "_pkg_" + self.key(package)
        try:
            sig_key = constant.REDIS_CONN.get(pkg_corresponding_sigkey)
            if not sig_key:
                raise ValueError
            sig_val = constant.REDIS_CONN.get(sig_key)
        except (redis.ConnectionError, ValueError):
            return None
        return json.loads(sig_val) if sig_val else None

    def clear_index(self, index):
        """
        Clear es index
        :param index: es index
        """
        LOGGER.info(f"delete elasticsearch index: {index}")
        self.session.delete_index(index)

    async def es_bulk(self, bodys):
        try:
            await self.session.async_bulk(body=bodys)
        except ElasticSearchQueryException as error:
            LOGGER.error(error)


class SigInfo(BaseTracking):
    """
    Sig group information is synchronized
    """

    index = "sig_info"
    community = "https://gitee.com/openeuler/community.git"

    def __init__(self) -> None:
        self.folder_path = os.path.join(configuration.TEMPORARY_DIRECTORY, "community")

    @staticmethod
    def list_dict_duplicate_removal(data_list):
        """
        Deduplication of nested dictionaries in lists
        Args:
            data_list: Nested dictionaries in lists

        Returns:
            data after deduplication
        """
        return reduce(
            lambda x, y: x if y in x else x + [y],
            [
                [],
            ]
            + data_list,
        )

    @staticmethod
    def _sig_name(file_path):
        """
        Get the sig name according to the path interception
        Args:
            file_path: sig_info.yaml path

        Returns:
            sig_group_name: sig group name
        """
        sig_group_name = None
        try:
            sig_group_name = str(file_path).split("/")[-2]
        except IndexError as error:
            LOGGER.error(f"Error looking up sig group name,because {error}")
        return sig_group_name

    async def _clone(self):
        """
        clone community repository
        Returns:
            Result of cloning the repository
        """

        Path(self.folder_path).mkdir(parents=True)
        cmds = ["git", "clone", self.community, self.folder_path]
        code, out, err = self.cmd(cmds)
        return code, out, err

    async def _pull(self):
        """
        Pull the latest repository
        Returns:
            Result of pull the repository
        """
        cmds = ["git", "pull", "origin", "master"]
        code, out, err = self.cmd(cmds, cwd=self.folder_path)
        return code, out, err

    async def read_yaml_info(self, file):
        """
        Read local yaml file
        Args:
            file: sig_info.yaml path

        Returns:
            sig_infos: single sig information
        """

        def responsible_infos(responsibles):
            """
            Get basic information about people
            Args:
                responsibles: responsible infos

            Returns:
                Person's id email organization
            """
            return [
                {
                    "id": responsible.get("gitee_id"),
                    "email": responsible.get("email"),
                    "organization": responsible.get("organization"),
                }
                for responsible in responsibles
            ]

        def update_sig_infos(sig_key, repo_key, repositorie):
            """
            Update sig group information data
            Args:
                sig_key: sig name
                repo_key: repo name
                repositorie: repositorie

            Returns:
                sig_infos: update sig information
            """
            if repositorie.get(repo_key):
                sig_infos[sig_key].extend(responsible_infos(repositorie.get(repo_key)))

        if Path(file).parent.joinpath("OWNERS").exists():
            return dict()

        with open(file, "r", encoding="utf-8") as file_pointer:
            sig_info = yaml.safe_load(file_pointer)
            sig_infos = {
                "name": self._sig_name(file) or sig_info.get("name"),
                "description": sig_info.get("description", ""),
                "contributors": list(),
                "repositories": list(),
            }
            maintainer = responsible_infos(sig_info.get("maintainers", []))
            committers = list()
            for repositorie in sig_info.get("repositories", []):
                sig_infos["repositories"].extend(repositorie.get("repo"))
                committers.extend(responsible_infos(repositorie.get("committers", [])))
                update_sig_infos("contributors", "contributors", repositorie)

            sig_infos["contributors"] = self.list_dict_duplicate_removal(
                sig_infos.get("contributors", [])
            )
            sig_infos["maintainer"] = (
                self.list_dict_duplicate_removal(committers)
                if committers
                else self.list_dict_duplicate_removal(maintainer)
            )
        return sig_infos

    async def search_sig_file(self):
        """
        Find the sig_info.yaml file, combine the data and return
        Returns:
            sig_groups: Data for all sig groups
        """
        sig_groups = list()
        try:
            if not Path(self.folder_path).joinpath("sig").exists():
                await self._clone()
            await self._pull()
            sig_paths = Path(self.folder_path).joinpath("sig")
            for file in sig_paths.glob("**/sig-info.yaml"):
                if not file.is_file():
                    continue
                sig_infos = await self.read_yaml_info(file)
                if sig_infos:
                    sig_groups.append(sig_infos)
        except (IOError, OSError, ValueError, TypeError) as error:
            LOGGER.error(error)
        return sig_groups

    async def sig_info_integration(self, insert_db=False):
        """
        Composite SIG data model
        exp:
            {
                "name": "Base-service",
                "description": "The Base-service team is responsible for maintain the basic package for linux.",
                "maintainer": [
                    {
                        "id": "",
                        "organization": "",
                        "email": ""
                    }
                ],
                "contributors": [
                    {
                        "id": "",
                        "organization": "",
                        "email": ""
                    }
                ],
                "repositories": [
                    "openeuler/openEuler-rpm-config",
                    "src-openeuler/abseil-cpp"
                ]
            }
        """
        sig_groups = []
        if not insert_db:
            if constant.REDIS_CONN.keys(self.prefix + "*"):
                return
            pannel = PanelInfo()
            try:
                sig_groups = pannel.query_sig_info(sig_name=None)
            except ElasticSearchQueryException:
                sig_groups = []
        if not sig_groups:
            sig_groups_om = await self.gitee.get_sig_info()
            sig_groups = await self.search_sig_file()
            sig_groups.extend(
                [
                    sig_group_om
                    for sig_group_om in sig_groups_om
                    if sig_group_om["name"]
                    not in [
                        sig_group_cummunity["name"]
                        for sig_group_cummunity in sig_groups
                    ]
                ]
            )
        bulk_bodys = []
        for sig_info in sig_groups:
            if "contributors" not in sig_info.keys():
                sig_info["contributors"] = list()
            if sig_info.get("name") == "sig-template":
                continue
            self.set_cache(source_val=sig_info)
            if insert_db:
                bulk_bodys.append(
                    self.session.es_insert_struct(index=self.index, source=sig_info)
                )
        if bulk_bodys and insert_db:
            await self.session.async_bulk(body=bulk_bodys)

    async def start(self):
        """Enable sig group information synchronization"""
        LOGGER.info("The sig group data starts to be synchronized.")
        self.clear_index(index=self.index)
        await self.sig_info_integration(insert_db=True)
        LOGGER.info("The sig group data is synchronized.")


class ObsSynchronization(BaseTracking):
    """Obs information synchronization"""

    index = "obs_info"

    def __init__(self) -> None:
        self.main_project = []

    async def get_main_project(self):
        """Get the main project name of obs"""
        projects = await self.obs.main_project()
        self.main_project = list(
            set(
                [
                    item
                    for item in projects
                    if item not in set(constant.OBS_PROJECT_BLACKLIST)
                ]
            )
        )

    @staticmethod
    def obs_map_gitee_branch(obs_branch):
        """Branch mapping of OBS project name and open source project"""

        if obs_branch.endswith("Mainline") or obs_branch == "openEuler:Epol":
            gitee_branch = "master"
            return gitee_branch
        if obs_branch.endswith(":Epol"):
            obs_branch = obs_branch.replace(":Epol", "")
        gitee_branch = obs_branch.replace(":", "-")
        return gitee_branch

    def _build_detail_link(self, project, package):
        return "{host}/package/live_build_log/{project}/{pkg}/{architecture}/{arch}".format(
            host=configuration.OBS_HOST,
            project=project,
            pkg=package["repo_name"],
            architecture=package["architecture"],
            arch=self.obs.architectures.get(package["architecture"]),
        )

    def _gitee_obs_map(self):
        branchs_map = dict()
        for project in self.main_project:
            if project.endswith("Mainline") or project == "openEuler:Epol":
                gitee_branch = "master"
            else:
                gitee_branch = "-".join(project.replace(":Epol", "").split(":"))
            try:
                branchs_map[gitee_branch].append(project)
            except KeyError:
                branchs_map[gitee_branch] = [project]

        return branchs_map

    def _get_sourcerepo_version(self, repo, branch):
        name, version = (None, None)
        cache_key = self.key(self.prefix + "_" + repo + "_" + branch)
        try:
            gitee_pkg_info = constant.REDIS_CONN.hgetall(cache_key)
        except redis.ConnectionError:
            gitee_pkg_info = None
        if gitee_pkg_info:
            name = gitee_pkg_info["name"]
            version = gitee_pkg_info["version"]
        return name, version

    async def _save(self, packages, project):
        """
        Integrate SIG group data in OBS information and save to ES
        """
        bodys = []
        pannel = PanelInfo()
        pannel.delete(body=dict(obs_branch=project), index=self.index)
        for package in packages:
            # get sig groups info
            sig_info = self.get_cache(package=package["repo_name"])
            if sig_info:
                package.update(sig_info)
            package["gitee_branch"] = self.obs_map_gitee_branch(package["obs_branch"])
            (
                package["source_name"],
                package["gitee_version"],
            ) = self._get_sourcerepo_version(
                package["repo_name"], package["gitee_branch"]
            )
            bodys.append(
                self.session.es_insert_struct(index=self.index, source=package)
            )
            if len(bodys) >= 100:
                await self.es_bulk(bodys)
                bodys = []
        if bodys:
            await self.es_bulk(bodys)

    async def _get_all_packages(self, project):
        pre_tasks = [
            asyncio.create_task(self.obs.get_project_status(project), name="pkgs"),
            asyncio.create_task(
                self.obs.get_complete_packages(project=project), name="success_pkgs"
            ),
        ]
        packages, om_packages = [], []
        done_task, _ = await asyncio.wait(pre_tasks)
        for finish_task in done_task:
            if finish_task.get_name() == "pkgs":
                packages = finish_task.result()
            if finish_task.get_name() == "success_pkgs":
                om_packages = finish_task.result()
        return packages, om_packages

    async def _obs_packages(self, project):
        """
        Compile status of the software package
        :param project: Obs project name
        """
        packages, om_packages = await self._get_all_packages(project=project)
        for package in packages:
            key = package["repo_name"] + "_" + package["architecture"]
            if key in om_packages:
                conplete_package = om_packages[key]
                package["build_time"] = (
                    conplete_package["history_build_times"][-1]
                    if conplete_package["history_build_times"]
                    else None
                )
                package["history_build_times"] = conplete_package["history_build_times"]
            else:
                package["history_build_times"] = []
                package["build_time"] = None

            package.setdefault(
                "build_detail_link",
                self._build_detail_link(project, package),
            )
        if packages:
            await self._save(packages, project)

    async def synchronous_branch(self):
        """Source repository branch and OBS project mapping"""
        LOGGER.info("Start obs project and warehouse branch mapping synchronization.")
        await self.get_main_project()
        self.clear_index(index="branch_info")
        branchs_map = self._gitee_obs_map()
        branch_info = []
        for gitee, obs in branchs_map.items():
            sources = dict(gitee_branch=gitee, obs_branch=None)
            sources["obs_branch"] = [dict(name=obs_name) for obs_name in obs]

            branch_info.append(
                self.session.es_insert_struct(index="branch_info", source=sources)
            )

        await self.session.async_bulk(body=branch_info)
        LOGGER.info(
            "Complete obs project and warehouse branch mapping synchronization."
        )

    async def _cache_pkg_versions(self):
        try:
            for pkg_base_info in self.session.scan(
                index="pkg_repo_version", body={"query": {"match_all": {}}}
            ):
                pkg_base_info = pkg_base_info["_source"]
                base_info = {
                    "name": pkg_base_info["name"],
                    "version": pkg_base_info["version"],
                }
                constant.REDIS_CONN.hmset(
                    self.key(
                        self.prefix
                        + "_"
                        + pkg_base_info["repo"]
                        + "_"
                        + pkg_base_info["branch"]
                    ),
                    base_info,
                )
        except (ElasticSearchQueryException, redis.ConnectionError) as error:
            LOGGER.error(f"{error}")

    async def start(self):
        """Enable obs data synchronization"""
        LOGGER.info("The OBS data synchronization starts.")
        sig = SigInfo()
        pre_task = [
            asyncio.create_task(self.get_main_project()),
            asyncio.create_task(self._cache_pkg_versions()),
            asyncio.create_task(sig.sig_info_integration(insert_db=False)),
        ]
        await asyncio.gather(*pre_task)
        tasks = [
            asyncio.create_task(self._obs_packages(project))
            for project in self.main_project
        ]

        await asyncio.gather(*tasks)
        LOGGER.info("The project branch data is synchronized.")


class PrSynchronization(BaseTracking):
    """Open source project PR information synchronization"""

    index = "pr_info"

    async def _iteration_repos(self, sema):
        repos, total_page = await self.gitee.all_src_repo(page=1)
        if total_page == 1:
            return repos
        repos_tasks = [
            asyncio.create_task(self.gitee.all_src_repo(page=page))
            for page in range(2, total_page + 1)
        ]
        async with sema:
            done_task, _ = await asyncio.wait(repos_tasks)
            for task in done_task:
                repo, _ = task.result()
                repos.extend(repo)
        return repos

    async def _get_repo_version(self, repo, branch, sema):
        async with sema:
            name, version = await self.gitee.src_repo_spec(repo=repo, sha=branch)
            try:
                base_info = {"name": name or "", "version": version or ""}
                constant.REDIS_CONN.hmset(
                    self.key(self.prefix + "_" + repo + "_" + branch), base_info
                )
                base_info.update({"repo": repo, "branch": branch})
                await self.session.async_insert(
                    index="pkg_repo_version", body=base_info
                )
            except redis.ConnectionError as error:
                LOGGER.error(error)

    async def synchronous_version(self):
        """The mapping between software package branches and software versions is synchronized"""
        LOGGER.info("The gitee and OBS project data are synchronized.")
        sema = asyncio.Semaphore(2)
        self.clear_index(index="pkg_repo_version")
        repos = await self._iteration_repos(sema)
        branchs = ObsInfo().suggest_branch()
        tasks = []
        for repo in repos:
            for branch in branchs:
                tasks.append(
                    asyncio.create_task(self._get_repo_version(repo, branch, sema))
                )
        await asyncio.gather(*tasks)
        LOGGER.info("OBS engineering data synchronization is complete.")


class IsoInfoSynchronization(BaseTracking):
    """Iso information Construction"""

    index = "iso_info"

    async def start(self):
        """Start iso info data synchronization"""
        LOGGER.info("The ISO data synchronization starts.")
        await self._query_iso_infos()

    async def _query_iso_infos(self):
        panel = PanelInfo()
        iso_infos = await self.obs.get_iso_infos()
        if not iso_infos:
            LOGGER.warning("No ISO construction information is displayed.")
            return
        bulk_bodys = []
        for iso in iso_infos:
            iso["date"] = iso["date"].split()[0]
            panel.delete(
                body=dict(date=iso["date"], branch=iso["branch"]), index=self.index
            )
            bulk_bodys.append(
                self.session.es_insert_struct(index=self.index, source=iso)
            )

        await self.session.async_bulk(body=bulk_bodys)
        LOGGER.info("The ISO data synchronization finished.")
