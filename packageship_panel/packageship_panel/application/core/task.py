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
import asyncio
import yaml
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from packageship.libs.log import LOGGER
from packageship_panel.application.core.tracking import (
    ObsSynchronization,
    PrSynchronization,
    SigInfo,
    IsoInfoSynchronization,
)
from packageship_panel.application.sendmail import sendmail


class Synchronization:
    """Scheduled Synchronization Task"""

    tasks = {
        "sync_rpm_build": ObsSynchronization().start,
        "sync_iso_build": IsoInfoSynchronization().start,
        "sync_version": PrSynchronization().synchronous_version,
        "sync_branch": ObsSynchronization().synchronous_branch,
        "sync_sig": SigInfo().start,
        "send_email": sendmail.Mail().start,
    }

    def __init__(self) -> None:
        self.exit = False
        self._timed_task = (
            "sync_rpm_build",
            "sync_iso_build",
            "sync_version",
            "sync_branch",
            "sync_sig",
            "send_email",
        )
        self.scheduler = AsyncIOScheduler()
        self.config = self._set_config()

    @staticmethod
    def cron(hour=0, minute=0, second=0, **kwargs):
        """The scheduled task is executed once"""
        return {
            "hour": hour,
            "minute": minute,
            "second": second,
        }

    @staticmethod
    def interval(hour=2, minute=0, second=0, **kwargs):
        """Scheduled tasks are executed periodically"""
        return {
            "hours": hour,
            "minutes": minute,
            "seconds": second,
        }

    def _set_config(self):
        config_file = "/etc/pkgship/timed_task.yaml"
        if not os.path.exists(config_file):
            raise FileNotFoundError("File not found: %s" % config_file)
        try:
            with open(config_file, "r", encoding="utf-8") as file:
                config = yaml.load(file, Loader=yaml.SafeLoader)
            for task_type in config:
                self._validate_config(tasks=task_type.get("tasks"))
        except (yaml.YAMLError, KeyError) as error:
            raise RuntimeError(error)
        else:
            return config

    def _validate_config(self, tasks):
        if not tasks:
            raise yaml.YAMLError("At least one scheduled task is required.")
        if not all(
            [True if task.get("name") in self._timed_task else False for task in tasks]
        ):
            raise yaml.YAMLError(
                "The name of a scheduled task can be contained only in 'sync_rpm_build \
                 sync_iso_build sync_pull sync_version sync_sig'."
            )
        if not all(
            [
                True if task.get("trigger") in ("interval", "cron") else False
                for task in tasks
            ]
        ):
            raise yaml.YAMLError(
                "The type triggered by a scheduled task can only be 'interval cron'."
            )

    def run(self):
        """
        Running scheduled Tasks,loading a scheduled policy Starts a scheduled task.
        """
        asyncio.set_event_loop_policy(asyncio.get_event_loop_policy())
        for task_type in self.config:
            self.__add_job(task_type.get("tasks", []))
        self.scheduler.start()
        try:
            asyncio.run_coroutine_threadsafe(
                self._execute_tasks(), asyncio.get_event_loop()
            )
            asyncio.get_event_loop().run_forever()
        except (KeyboardInterrupt, SystemExit) as error:
            LOGGER.error(
                f"An error occurred during the scheduled task execution:{error}"
            )
            print("exit")

    async def _execute_tasks(self):
        tasks = [
            asyncio.create_task(task())
            for task_name, task in self.tasks.items()
            if task_name not in ("sync_rpm_build", "send_email", "sync_version")
        ]
        await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
        LOGGER.info("The email sending and version synchronization task starts.")
        await asyncio.wait(
            [
                asyncio.create_task(PrSynchronization().synchronous_version()),
            ]
        )
        LOGGER.info("version synchronization tasks are complete.")

    def __add_job(self, tasks):
        if not tasks:
            return
        for task in tasks:
            if not task.get("enable", False):
                continue
            start_job = self.tasks[task["name"]]
            timing_schedule = getattr(self, task["trigger"])(**task)
            self.scheduler.add_job(
                start_job, trigger=task["trigger"], **timing_schedule
            )
