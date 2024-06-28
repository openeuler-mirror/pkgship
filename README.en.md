#  pkgship

- pkgship
  - [Introduction](#)
  - [Architecture](#)
  - [Software Download](#)
  - [Operating Environment](#)
  - [Installation Tool](#)
  - [Configuration Parameter](#)
  - [Starting and Stopping Services](#)
  - [Tool Usage](#)
  - [Viewing and Dumping Logs](#)
  - [Extension tool pkgship-panel](#)

## Introduction

pkgship is a tool used to manage the dependency of OS software packages and provide a complete dependency graph. pkgship provides functions such as software package dependency query, life cycle management, and patch query.

1. Software package dependency query: Enables community personnel to understand the impact scope of software when software packages are introduced, updated, or deleted.
2. Patch query: Allows community personnel to learn about the patches of the openEuler software package and obtain the patch content. For details, see [patch-tracking](https://gitee.com/openeuler/pkgship/blob/patch-tracking/README.md).

## Architecture

The system is developed using the flask-restful mode.

![avatar](https://gitee.com/openeuler/pkgship/raw/master/doc/design/pkgimg/packagemanagement.JPG)

## Software Download

- Official release address for mounting the Repo source: <https://repo.openeuler.org/>
- To obtain the source code, visit <https://gitee.com/openeuler/pkgship>.
- You can obtain the RPM package from <https://117.78.1.88/project/show/openEuler:Mainline>.

## Running Environment

- Hardware configuration:

| Configuration Item | Recommended Specifications |
| ------------------ | -------------------------- |
| CPU                | 8 cores                    |
| Memory             | 32 GB (minimum: 4 GB)      |
| Network bandwidth  | 300 M                      |
| I/O                | 375 MB/sec                 |

- Software configuration

| Software Name | Version and Specifications                                   |
| ------------- | ------------------------------------------------------------ |
| Elasticsearch | The version is 7.10.1. Single-node deployment is available. Clusters can be deployed. |
| Redis         | 5.0.4 or later is recommended. It is recommended that the size be set to 3/4 of the memory. |
| Python        | Version 3.8 or later                                         |

## Installation Tool

> Note: This software can run in Docker. In openEuler21.09, the --privileged parameter is used to create Docker due to environment restrictions. If the --privileged parameter is not used, the software fails to be started. This document will be updated after adaptation.

**1. Install the pkgship tool**

You can use either of the following methods to install the tool:

- Method 1: Mount the repo source using DNF.
  Use DNF to mount the pkgship software to the repo source (for details, see [Application Development Guide]([openEuler](https://www.openeuler.org/zh/) ). Then run the following commands to download and install the pkgship software and its dependencies:

  ```
  dnf install pkgship
  ```

- Method 2: Install the RPM package. Download the pkgship RPM package and run the following command to install it (x.x-x indicates the version number and needs to be replaced with the actual version number):

  ```
  rpm -ivh pkgship-x.x-x.oe1.noarch.rpm
  ```

  or

  ```
  dnf install pkgship-x.x-x.oe1.noarch.rpm
  ```

**2. Install Elasticsearch and Redis and start**

If Elasticsearch or Redis is not installed in the environment, you can run the automatic installation script after pkgship is installed.

The default script path is as follows:

```
/etc/pkgship/auto_install_pkgship_requires.sh
```

The execution method is as follows:

```
/bin/bash auto_install_pkgship_requires.sh elasticsearch
```

> Currently, Elasticsearch is installed without a password by default when the RPM package is used to install it, and the pkgship needs to use Elasticsearch without a password. Therefore, it is recommended that Elasticsearch and pkgship be installed on the same server to improve security through network isolation. The Elasticsearch user name and password will be supported in later versions.

or

```
 /bin/bash auto_install_pkgship_requires.sh redis
```

After elasticsearch and redis is installed, need to start the service.The command is as follows:

```
 systemctl start elasticsearch
```
```
 systemctl start redis
```

**3. Add a user after the installation**

After the pkgship software is installed, the system automatically creates a user named pkgshipuser and a user group named pkgshipuser. You do not need to manually create the user and user group because they will be used when the service is started and running.

## Parameters

1. Configure the parameters in the configuration file. The default configuration file of the system is /etc/pkgship/packge.ini. Modify the configuration file according to the actual situation.

```
vim /etc/pkgship/package.ini
```

```
[SYSTEM-system configuration]
; Location of the .yaml file imported during database initialization. The .yaml file records the location of the imported .sqlite file.
init_conf_path=/etc/pkgship/conf.yaml

If the client-server mode is used, the value of query_ip_addr on the server must be the local IP address or 0.0.0.0,
In addition, the client can access the server by using query_ip_addr and query_port or by setting the mapped remote_host.
; service query port.
query_port=8090

; IP address for service query.
query_ip_addr=127.0.0.1

; Address of the remote service. The command line can directly invoke the remote service to complete the data request.
remote_host=https://api.openeuler.org/pkgmanage

; Directory for storing initialized and downloaded temporary files. The directory will not be occupied for a long time. It is recommended that the available space be at least 1 GB.
temporary_directory=/opt/pkgship/tmp/

[LOG-log]
; Path for storing service logs.
log_path=/var/log/pkgship/

; Log level. The options are as follows:
; INFO DEBUG WARNING ERROR CRITICAL
log_level=INFO

; Maximum size of a single service log file. If the size of a service log file exceeds the value of this parameter, the file is automatically compressed and dumped. The default value is 30 MB.
max_bytes=31457280

; Maximum number of backup logs that can be retained. The default value is 30.
backup_count=30

[UWSGI-Web Server Configuration]
; Path of operation logs.
daemonize=/var/log/pkgship-operation/uwsgi.log
; Size of data transmitted between the frontend and backend.
buffer-size=65536
; Timeout interval of the network connection.
http-timeout=600
; Service response time.
harakiri=600

[REDIS-Cache configuration]
The address of the Redis cache server can be the released domain or IP address that can be accessed normally.
The default link address is 127.0.0.1.
redis_host=127.0.0.1

; Port number of the Redis cache server. The default value is 6379.
redis_port=6379

;Maximum number of connections allowed by the Redis server at a time.
redis_max_connections=10

[DATABASE-Database]
; Database access address. You are advised to set it to the address of the local host.
database_host=127.0.0.1

; Port for accessing the database. The default value is 9200.
database_port=9200
```

2. Create a YAML configuration file for initializing the database. By default, the conf.yaml file is stored in the /etc/pkgship/ directory. The pkgship reads the name of the database to be created and the sqlite file to be imported based on this configuration. You can also configure the repo address of the sqlite file. An example of the conf.yaml file is as follows:

```
dbname: oe20.03 #Database name
Local path of the src_db_file: file:///etc/pkgship/repo/openEuler-20.09/src # source code package.
Local path of the bin_db_file: file:///etc/pkgship/repo/openEuler-20.09/bin # binary package.
priority: 1 # Database priority

dbname: oe20.09
Repo source where the src_db_file: https://repo.openeuler.org/openEuler-20.09/source # source code package is located
Repo source where the bin_db_file: https://repo.openeuler.org/openEuler-20.09/everything/aarch64 # binary package is located
priority: 2
```

> To change the storage path, change the value of **init_conf_path** in the **package.ini** file.
>
> The sqlite file configuration specifications are as follows:
>
> - To save space, the sqlite file cannot be directly used. Use the compressed package that contains the sqlite file. The supported compression format is .bz .gz .tar .zip.
> - The sqlite compressed package is named in the format of xxx.primary.sqlite.xx. The sqlite compressed file of the filelists type must be used in the path where the binary package is located. The format of the sqlite compressed file is xxx.filelists.sqlite.xx. Generally, the sqlite compressed package under the network address complies with this format.
> - Use file:// as the prefix of the local path.
> - The local path and network address path must meet the following requirements: The sqlite package is stored in the configuration path /repodata/xxx.primary.sqlite.xx.
>
> The value of dbname can contain only lowercase letters and digits. Uppercase letters are not supported.

## Starting and Stopping Services

The pkgship can be started and stopped in two modes: systemctl and pkgshipd. In systemctl mode, the automatic startup mechanism can be stopped when an exception occurs. You can run either of the following commands:

```
Starting the systemctl start pkgship.service Service

systemctl stop pkgship.service Stop the service.

Restarting the systemctl restart pkgship.service Service
```

```
pkgshipd start: starts the service.

pkgshipd stop: stops the service.
```

> Only one mode is supported in each start/stop period. The two modes cannot be used at the same time.
>
> The pkgshipd startup mode can be used only by the pkgshipuser user.
>
> In the Docker environment, if the systemctl command is not supported, use the pkgshipd command to start and stop the service.

## Using Tools

1. Initialize the database.

   > Application scenario: After the service is started, to query the package information and package dependency in the corresponding database (for example, oe20.03 and oe20.09), you need to import the sqlite (including the source code library and binary library) generated by the createrepo to the service to generate the JSON body of the corresponding package information and insert the JSON body into the corresponding database of Elasticsearch. The database name is the value of dbname-source/binary generated based on the value of dbname in the config.yaml file.

   ```
   pkgship init [-filepath path]
   ```

   > Parameter description:
   > -filepath: Specifies the path of the initialization configuration file config.yaml. The value can be a relative path or an absolute path. If this parameter is not specified, the default configuration is used for initialization. This parameter is optional.

2. Query a single packet.

   You can query details about a source code package or binary package (packagename) in a specified database table.

   > Application scenario: Users can query the detailed information about the source code package or binary package in a specified database.

   ```
   pkgship pkginfo $packageName $database [-s]
   ```

   > Parameter description:
   > packagename: Specifies the name of the software package to be queried. This parameter is mandatory.
   > database: Specifies the database name. This parameter is mandatory.
   >
   > -s: If you specify `-s`, the `src` source code package information is queried. If you do not specify this parameter, the `bin` binary package information is queried by default. This parameter is optional.

3. Query all packages.

   Query information about all packages in the database.

   > Application scenario: You can query information about all software packages in a specified database.

   ```
   pkgship list $database [-s]
   ```

   > Parameter description:
   > database: Specifies the database name. This parameter is mandatory.
   > -s: If you specify `-s`, the `src` source code package information is queried. If you do not specify this parameter, the `bin` binary package information is queried by default. This parameter is optional.

4. Query the installation dependency.

   Query the installation dependency of the binary package (binaryName).

   > Application scenario: When you need to install binary package A, you need to set the installation dependency of binary package A to B and the installation dependency of binary package B to C. Binary package A can be successfully installed only after all the installation dependencies are installed in the system. Therefore, before installing binary package A, you may need to query all installation dependencies of binary package A. This command allows you to query multiple databases based on the default priority of the platform. You can also customize the database query priority.

   ```
   pkgship installdep [$binaryName $binaryName1 $binaryName2...] [-dbs] [db1 db2...] [-level] $level
   ```

   > Parameter description:
   > binaryName: Name of the dependent binary package to be queried. Multiple binary packages can be transferred. This parameter is mandatory.
   >
   > -dbs: Specifies the priority of the database to be queried. If this parameter is not specified, the database is queried based on the default priority. This parameter is optional.
   >
   > -level: Specifies the dependency level to be queried. If this parameter is not specified, the default value 0 is used, indicating that all levels are queried. This parameter is optional.

5. Query the compilation dependency.

   Query all compilation dependencies of the source code package (sourceName).

   > Application scenario: To compile source code package A, you need to install compilation dependency package B of source code package A. To successfully install compilation dependency package B, you need to obtain all installation dependency packages of package B. Therefore, before compiling source code package A, you may need to query the compilation dependencies of the source code package and all installation dependencies of these compilation dependencies. This command allows you to query multiple databases based on the default priority of the platform. You can also customize the database query priority.

   ```
   pkgship builddep [$sourceName $sourceName1 $sourceName2..] -dbs [db1 db2 ..] [-level] $level
   ```

   > Parameter description:
   > sourceName: Name of the source code package on which the compilation depends. Multiple source code packages can be queried. This parameter is mandatory.
   >
   > -dbs: Specifies the priority of the database to be queried. If this parameter is not specified, the database is queried based on the default priority. This parameter is optional.
   >
   > -level: Specifies the dependency level to be queried. If this parameter is not specified, the default value 0 is used, indicating that all levels are queried. This parameter is optional.

6. Query the self-compilation and self-installation dependency.

   Queries the installation and compilation dependencies of a specified binary package (binaryName) or source code package (sourceName). [pkgName] indicates the name of the binary package or source code package to be queried. When querying a binary package, you can query all installation dependencies of the binary package, compilation dependencies of the source code package corresponding to the binary package, and all installation dependencies of these compilation dependencies. When querying a source code package, you can query the compilation dependency of the source code package, all installation dependencies of these compilation dependencies, and all installation dependencies of all binary packages generated by the source code package. In addition, this command can be used together with the corresponding parameter to query the self-compilation dependency of a software package and the dependency of a subpackage.

   > Application scenario: If you want to introduce a new software package based on the existing version library, you need to introduce all compilation and installation dependencies of the software package. This command allows you to query the two types of dependencies at the same time so that you can know which other packages will be introduced to the software package. This command can be used to query binary packages and source code packages.

   ```
    pkgship selfdepend [$pkgName1 $pkgName2 $pkgName3 ..] [-dbs] [db1 db2..] [-b] [-s] [-w]
   ```

   > Parameter description:
   >
   > pkgName: Name of the software package on which the installation depends. Multiple software packages can be transferred. This parameter is mandatory.
   >
   > -dbs: Specifies the priority of the database to be queried. If this parameter is not specified, the database is queried based on the default priority. This parameter is optional.
   >
   > -b: If `-b` is specified, the package to be queried is in binary format. If the source code package is not specified, the source code package is queried by default. This parameter is optional.
   >
   > -s: If -s is specified, all installation dependencies, compilation dependencies (that is, compilation dependencies of the source code package on which compilation depends), and installation dependencies of all compilation dependencies of the software package are queried. If the -s parameter is not added, all installation dependencies, layer-1 compilation dependencies, and layer-1 compilation dependencies of the software package are queried. This parameter is optional.
   >
   > -w: If -s is specified, when a binary package is imported, the source code package corresponding to the binary package and all binary packages generated by the source code package are displayed in the query result. If -w is not specified, when a binary package is imported, only the corresponding source code package is displayed in the query result. This parameter is optional.

7. Depended query.
   Query the packages that depend on the software package (pkgName) in a database (dbName).

   > Usage scenario: You can run this command to query the software packages that will be affected by the upgrade or deletion of software package A. This command displays the source code packages (for example, B) that depend on the binary packages generated by source code package A (for example, C1) and the binary packages (for example, C1) that depend on the binary packages. And the source code packages (such as D) that depend on the binary package generated by B, the binary packages (such as E1) that depend on the binary package generated by B, and so on. Traverse the dependent binary packages.

   ```
    pkgship bedepend dbName [$pkgName1 $pkgName2 $pkgName3] [-w] [-b] [-install/build]
   ```

   > Argument description:
   >
   > dbName: Name of the repository whose dependency needs to be queried. This parameter is mandatory.
   >
   > pkgName: Specifies the name of the software package to be queried. This parameter is mandatory. Multiple software packages can be queried.
   >
   > -w: If -w is not specified, the query result does not contain the subpackage of the corresponding source code package by default. If the configuration parameter [-w] is specified after the command, the dependency of the binary package C1 is queried, in addition, the dependency of other binary packages (for example, C2 and C3) generated by the source code package C corresponding to C1 is queried. This parameter is optional.
   >
   > -b: (Optional) If `-b` is specified, the package to be queried is a binary package. By default, the source code package is queried.
   >
   > -install/build: If `-install` is specified, the dependency of installation is queried. If `-build` is specified, the dependency of compilation is queried. By default, all dependencies are queried. `-install` and `-build` cannot coexist. This parameter is optional.

8. Obtain the database information.

   > Application scenario: Check which databases are initialized in Elasticsearch. This function returns the list of initialized databases based on the priority.

   `pkgship dbs`

9. Obtain the version number.

   > Application scenario: This interface is used to obtain the version number of the pkgship software.

   `pkgship -v`

10. Compare the dependency between packages in different databases.

Query the information about all source code packages and binary packages of the input database and their layer-1 compilation and installation dependencies, compare the dependency information of each database based on the first database package information, and record the differences in the CSV file.

> Application scenario: Compare the dependencies between systems and analyze the optimization points of software package dependencies.

```
pkgship compare -t build/install -dbs [database1 database2..] [-o out_path]
```

> Parameter description:
>
> -t: Dependency type. Currently, only -build (compilation dependency) and -install (installation dependency) are supported.
>
> -dbs: Indicates the list of databases to be queried. Databases are separated by spaces. To control the execution time, a maximum of four databases are supported. The software package of the first database is used as the benchmark package set for comparison.
>
> -o: Indicates the path for storing CSV files. If this parameter is not specified, the default value /opt/pkgship/compare is used. If this parameter needs to be specified, ensure that the execution user pkgshipuser has the write permission. The .csv file is saved in the ${out_path}/timestamp directory. The csv file contains the package dependency information (named after the database name) of each database and the package dependency comparison information (compare.csv) of all databases.

## Viewing and Dumping Logs

**Viewing Logs**

When the pkgship service is running, two types of logs are generated: service and operation.

1. Service logs:

Path: /var/log/pkgship/log_info.log (You can customize the path using the log_path field in the conf.yaml file.)

Function: This log records the internal running of the code to facilitate fault locating.

Permission: The permission on the path is 755, and the permission on the log file is 644. Common users can view the log file.

2. Operation log:

Path: /var/log/pkgship-operation/uwsgi.log (You can customize the path using the daemonize field in the conf.yaml file.)

Function: Record user operation information, including the IP address, access time, access URL, and access result, to facilitate subsequent query and record attacker information.

Permission: The permission on the path is 700, and the permission on the log file is 644. Only the root and pkgshipuser users can view the log file.

**Log dump**

1. Service log dump:

- Dump Mechanism

  Use the dumping mechanism of the logging built-in function of Python to back up logs based on the log size.

> Configuration item. It is used to configure the capacity and number of backups of each log in the package.ini file.
>
> ```
> ; Maximum capacity of each file, the unit is byte, default is 30M
> max_bytes=31457280
> 
> ; Number of old logs to keep;default is 30
> backup_count=30
> ```

- Dump Process

  After a log is written, if the size of the log file exceeds the configured log capacity, the log file is automatically compressed and dumped. The compressed file name is log_info.log.x.gz, where x is a number. A smaller number indicates a newer backup.

  When the number of backup log files reaches the maximum, the earliest backup log file is deleted and the latest compressed log file is backed up.

2. Operation log dump:

- Dump Mechanism

  A script is used to dump data by time. Data is dumped once a day and is retained for 30 days. The retention period cannot be customized.

  > The script is stored in /etc/pkgship/uwsgi_logrotate.sh.

- Dump Process

  When pkgship is started, the dump script runs in the background. From the startup, dump and compression are performed every one day. A total of 30 compressed files are retained. The compressed file name is uwsgi.log-20201010x.zip, where x indicates the hour when the file is compressed.

  After the pkgship is stopped, the dump script is stopped and does not dump data. When the pkgship is started again, the dump script is executed again.

## Extension tool pkgship-panel

### Introduction

pkgship-panel is designed to integrate package build information and maintenance  information together, so that version maintainers can quickly identify  abnormal packages and quickly notify the relevant responsible persons by email to solve them, so as to ensure the stability of the build project and improve the success rate of IOS builds. 

### Architecture

![img](doc/design/pkgimg/panel%E9%80%BB%E8%BE%91%E8%A7%86%E5%9B%BE.png)

### Tool use

Since the tool data source is not configurable, it is recommended to directly use the official website address of pkgship-panel:  https://pkgmanage.openeuler.org/Infomanagement
