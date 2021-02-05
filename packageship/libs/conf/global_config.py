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
Global environment variable value when the system is running
"""

import os

# Configuration file path for data initialization
INIT_CONF_PATH = os.path.join('/', 'etc', 'pkgship', 'conf.yaml')

# If the path of the imported database is not specified in the configuration file, the
# configuration in the system is used by default
DATABASE_FOLDER_PATH = os.path.join('/', 'var', 'run', 'pkgship_dbs')

# The database engines supported in the system is sqlite database by default
DATABASE_ENGINE_TYPE = 'elastic'

# Default ip address of database
DATABASE_HOST = '127.0.0.1'

# Default port of database
DATABASE_PORT = '9200'

# Ordinary user query port, only the right to query data, no permission to write data
QUERY_PORT = 8090

# IP address path with permission to query data
QUERY_IP_ADDR = '127.0.0.1'

# The address of the remote service, the command line can directly
# call the remote service to complete the data request
REMOTE_HOST = 'https://api.openeuler.org/pkgmanage'

# If the directory of log storage is not configured,
# it will be stored in the following directory specified by the system by default
LOG_PATH = os.path.join('/', 'var', 'log', 'pkgship')

# Logging level
# The log level option value can only be as follows
# INFO DEBUG WARNING ERROR CRITICAL
LOG_LEVEL = 'INFO'

# logging name
LOG_NAME = 'log_info.log'

# The number of dynamically created logs
# after the log file size reaches the upper limit. The default is 10 dynamically created logs
BACKUP_COUNT = 10

# The size of each log file, in bytes, the default size of a single log file is 300M
MAX_BYTES = 314572800

# The address of the Redis cache server can be either a published
# domain or an IP address that can be accessed normally
# The link address defaults to 127.0.0.1
# redis_host = 127.0.0.1

REDIS_HOST = '127.0.0.1'

# Redis cache server link port number, default is 6379
REDIS_PORT = 6379

# Maximum number of connections allowed by RedIS server at one time

REDIS_MAX_CONNECTIONS = 10

# Maximum queue length
QUEUE_MAXSIZE = 1000

# A temporary directory for files downloaded from the network that are cleaned periodically
TEMPORARY_DIRECTORY = '/var/run/pkgship'
