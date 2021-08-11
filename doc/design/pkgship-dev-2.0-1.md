# pkgship 新增特性1--版本差异对比设计文档

## 1、 需求描述

1. 辅助版本构建优化，通过对比软件包依赖差异剔除无用依赖
2. 辅助多版本软件包引入工作，支持多版本依赖查询和验证

### 1.1、 受益人

|角色|角色描述|
|:--|:-------|
| 软件生态扩展人员 | 维护开源社区软件生态的人员，在针对软件包引入、升级、删除的情况使用pkgship去排查软件包依赖情况 |
| 工程构建开发人员 | 分析不同发行版之间的依赖差异，提出多余依赖关系，优化软件包编译时间 |

### 1.2、 依赖组件

无

### 1.3、 License

Mulan V2

## 2、 设计概述

- 数据与代码分离： 功能实现是需要考虑哪些数据是需要配置动态改变的，不可在代码中将数据写死，应提取出来做成可配置项。

- 分层原则： 上层业务模块的数据查询应通过查询模块调用数据库获取数据，不可直接跨层访问数据库。

- 接口与实现分离：外部依赖模块接口而不是依赖模块实现。

- 模块划分： 模块之间只能单向调用，不能存在循环依赖。

- 变更： 架构设计变更、外部接口变更、特性需求变更需要结合开发、测试等所有相关人员经过开会讨论后决策，不可擅自变更。

## 3、 需求分析

### 3.1、 需求清单

1. 用户指定多个数据库，分别生成这些数据库下软件包的一层安装、编译依赖关系并记录在对应的csv文件中，然后按照第一个数据库为基准生成和其他数据库依赖关系对比的结果并记录在csv文件中。（共生成指定数据库数目+1个csv文件）。
2. 增加compare配置文件，支持软件包名变更情况下的对比（暂时不实现）。

#### 3.1.1 特性列表

|no|特性描述|代码估计规模| 归属需求 |
|:--|:-------|:------|:------|
| 1 | 支持命令行输入查询发行版间安装、编译依赖差异对比 | 0.2k | no.1 |
| 2 | 支持查询某一数据库下所有源码包的一层编译依赖 | 0.1k | no.1 |
| 3 | 支持查询某一数据库下所有二进制包的一层安装依赖 | 0.1k | no.1 |
| 4 | 支持对比所查询数据库下软件包的依赖差异对比 | 0.3k | no.1 |
| 5 | 支持通过配置文件配置不同数据库中包名的映射关系，然后按照映射关系对比依赖差异。(暂时不做) | 0.3k | no.2 |

### 3.2、外部接口清单

#### 3.2.1、命令行接口清单

##### 3.2.1.1、生成版本差异对比文件

pkgship  compare  -t  $requireType  -dbs  [$datbabase1 $database2...]  -o  $filePath

* **必选参数**

  * -t

    依赖类型，目前支持install，build。

  * -dbs

    需要对比的数据库（repo源），可通过pkgship dbs命令查询出支持的数据库，目前限定最多四个。
    
    > - 第一个数据库为基准数据库，比较结果是按照该数据库的软件包依赖关系和其他数据库做对比生成的。
    >
    > - 如果只填写一个数据库，将不生成对比结果数据。

* **可选参数**

  * -o

    差异对比文件存放路径，默认为/opt/pkgship/compare,自定义需保证pkgshipuser有权限访问和写入。
    
    > 说明：为了保证几次对比的文件不互相覆盖，将在输入路径下生成时间戳文件夹，会在对比成功后显示。

* **举例**

  * 生成openEuler21.03和fedora32的版本编译依赖差异对比到/opt路径下

```shell
        pkgship compare -t build -dbs openEuler21.03 fedora32 -o /opt
```

##### 3.2.1.2、对比成功输出信息

```txt
[INFO] The data comparison is successful, and the generated file is in the (xxx) path.
```

### 3.3、内部接口清单


| 所属模块     | 接口名称          | 接口描述                                                     |
| ------------ | ----------------- | ------------------------------------------------------------ |
| 校验模块     | validate_args()   | 校验入参的合法性，包括依赖类型，数据库有效性，路径权限。     |
| 依赖查询模块 | all_rpm_denpend() | 查询入参数据库中所有包的一层依赖（安装依赖，编译依赖，被依赖其中一个），生成依赖字典。 |
| 差异对比模块 | dbs_compare()     | 根据上面依赖查询接口查询出的依赖信息，进行差异对比。         |

#### 3.3.1、校验模块

validate_args()

* **接口描述**

  校验命令行入参，针对不同的异常输入给出提示信息。

* **请求参数**

  | 参数名      | 必填 | 类型 | 说明               |
  | ----------- | ---- | ---- | ------------------ |
  | dbs         | 是   | list | 待查询的数据库列表 |
  | depend_type | 是   | str  | 待查询的依赖类型   |
  | output_path | 是   | str  | csv文件存放路径    |

* **调用示例**

  ```python
  validate_args(dbs=['openEuler21.03', 'fedora32'],depend_type='build',output_path='/opt')
  ```

* **预期返回信息**

  | 异常类型                 | 返回信息                                                     |
  | ------------------------ | ------------------------------------------------------------ |
  | 参数缺失                 | [ERROR] Parameter error, please check the parameter and query again. |
  | 依赖类型不支持           | [ERROR] Dependent type (xxx) is not supported, please enter again. |
  | 输出路径不存在或者无权限 | [ERROR] Output path (xxx) not exist or does not support user pkgshipuser writing. |
  | 数据库不支持             | [ERROR] Database ({db}) is not supported, please enter again. |
  | 输入数据库多于4个        | [ERROR] Supports up to four databases                        |
  | 输入重复的数据库         | [ERROR] Duplicate database entered                           |
  | 服务未启动时查询         | [ERROR] The pkgship service is not started,please start the service first |

#### 3.3.2、依赖查询模块

all_rpm_denpend()

* **接口描述**

  查询入参数据库中所有包的一层依赖（安装依赖，编译依赖，被依赖其中一个），生成依赖字典。

* **请求参数**

  | 参数名       | 必填 | 类型 | 说明               |
  | ------------ | ---- | ---- | ------------------ |
  | dbs          | 是   | list | 待查询的数据库列表 |
  | require_type | 是   | str  | 待查询的依赖类型   |

* **查询示例**

  all_rpm_denpend(dbs=["openEuler21.03","fedora32"],require_type="build")

* **预期返回参数**

  | 参数名          | 类型                | 说明                                           |      |
  | --------------- | ------------------- | ---------------------------------------------- | ---- |
  | all_depend_info | list（depend_info） | 所有数据库的依赖信息的列表，每个数据库一个字典 |      |

  *  depend_info：

  ```json
  {
      "数据库1名称": [
          {
              "软件包名": {
                  /*"软件包信息"*/
                  "依赖": [
                      {
                          /* 依赖信息 */
                      }
                  ]
              }
          }
      ]
  }
  ```

* 返回示例

  ```json
  resp = [
      {
          "openEuler21.03": [
              {
                  "Judy": {
                      "binary_name": "Judy",
                      "bin_version": "1.1.1",
                      "database": "openeuler-20.09",
                      "src_name": "Judy",
                      "src_version": "1.1.1",
                      "requires": [
                          {
                              "component": "lib.so",
                              "com_bin_name": "libJudy",
                              "com_bin_version": "1.1.1",
                              "com_src_name": "lib",
                              "com_src_version": "1.1.1",
                              "com_database": "openeuler-20.09"
                          },
                          {
                              "component": "lib4.so",
                              "com_bin_name": "libJudy",
                              "com_bin_version": "1.1.1",
                              "com_src_name": "lib",
                              "com_src_version": "1.1.1",
                              "com_database": "openeuler-20.09"
                          },
                          {
                              "component": "lib2.so",
                              "com_bin_name": "libJudy2",
                              "com_bin_version": "1.1.1",
                              "com_src_name": "lib",
                              "com_src_version": "1.1.1",
                              "com_src_version": "1.1.1",
                              "com_database": "fedora31"
                          },
                          {
                              "component": "lib3.so"
                          }
                      ]
                  }
              },
              {
                  "CUnit": {
                      "binary_name": "CUit",
                      "bin_version": "1.1.1",
                      "database": "openeuler-20.09",
                      "src_name": "CUit",
                      "src_version": "1.1.1",
                      "requires": [
                          {
                              "component": "lib4.so",
                              "com_bin_name": "libJudy",
                              "com_bin_version": "1.1.1",
                              "com_src_name": "Judy",
                              "com_src_version": "1.1.1",
                              "com_database": "openeuler-20.09"
                          },
                          {
                              "component": "lib4.so",
                              "com_bin_name": "libJudy",
                              "com_bin_version": "1.1.1",
                              "com_src_name": "Judy",
                              "com_src_version": "1.1.1",
                              "com_database": "fedora31"
                          }
                      ]
                  }
              }
          ]
      },
      {
          "fedora32": [
              {
                  "Judy": {
                      "binary_name": "Judy",
                      "bin_version": "1.1.1",
                      "database": "openeuler-20.09",
                      "src_name": "Judy",
                      "src_version": "1.1.1",
                      "requires": [
                          {
                              "component": "lib.so",
                              "com_bin_name": "libJudy",
                              "com_bin_version": "1.1.1",
                              "com_src_name": "lib",
                              "com_src_version": "1.1.1",
                              "com_database": "openeuler-20.09"
                          },
                          {
                              "component": "lib4.so",
                              "com_bin_name": "libJudy",
                              "com_bin_version": "1.1.1",
                              "com_src_name": "lib",
                              "com_src_version": "1.1.1",
                              "com_database": "openeuler-20.09"
                          },
                          {
                              "component": "lib2.so",
                              "com_bin_name": "libJudy2",
                              "com_bin_version": "1.1.1",
                              "com_src_name": "lib",
                              "com_src_version": "1.1.1",
                              "com_src_version": "1.1.1",
                              "com_database": "fedora31"
                          },
                          {
                              "component": "lib3.so"
                          }
                      ]
                  }
              },
              {
                  "CUnit": {
                      "binary_name": "CUit",
                      "bin_version": "1.1.1",
                      "database": "openeuler-20.09",
                      "src_name": "CUit",
                      "src_version": "1.1.1",
                      "requires": [
                          {
                              "component": "lib4.so",
                              "com_bin_name": "libJudy",
                              "com_bin_version": "1.1.1",
                              "com_src_name": "Judy",
                              "com_src_version": "1.1.1",
                              "com_database": "openeuler-20.09"
                          },
                          {
                              "component": "lib4.so",
                              "com_bin_name": "libJudy",
                              "com_bin_version": "1.1.1",
                              "com_src_name": "Judy",
                              "com_src_version": "1.1.1",
                              "com_database": "fedora31"
                          }
                      ]
                  }
              }
          ]
      }
  ]
  ```

#### 3.3.2、差异对比模块

dbs_compare()

* **接口描述**

  根据每个数据库生成的依赖数据，对比差异并存入csv文件。

* **请求参数**

  | 参数名          | 必填 | 类型                | 说明                                           |
  | --------------- | ---- | ------------------- | ---------------------------------------------- |
  | all_depend_info | 是   | list（depend_info） | 所有数据库的依赖信息的列表，每个数据库一个字典 |
  
* **请求示例**

  dbs_compare(all_depend_info)

* **预期返回参数**

  True/False，比较结果将存入cvs文件。

* cvs文件示例

  * openEuler21.03.csv

    | dependence               | dependence package | dependence version | depending package | depending version |
    | ------------------------ | ------------------ | ------------------ | ----------------- | ----------------- |
    | XXX-release -> XXX-repos | XXX-release        | 1.0                | XXX-repos         | 1.0               |
    | attr -> rpm-libs         | attr               | 1.0                | rpm               | 4.3               |
    | audit-libs -> glibc      | audit              | 1.1                | glibc             | 2.0               |
    | audit-libs -> libcap-ng  | audit              | 1.1                | libcap-ng         | 2.0               |

  * fedora32.csv

    | dependence               | dependence package | dependence version | depending package | depending version |
    | ------------------------ | ------------------ | ------------------ | ----------------- | ----------------- |
    | XXX-release -> XXX-repos | XXX-release        | 1.0                | XXX-repos         | 1.0               |
    | attr -> rpm-libs         | attr               | 1.0                | rpm               | 4.3               |
    | audit-libs -> glibc      | audit              | 1.1                | glibc             | 2.0               |
    | audit-libs -> libcap-ng  | audit              | 1.1                | libcap-ng         | 2.0               |
    | audit-libs -> rpm-libs   | audit              | 1.1                | rpm               | 4.3               |

  * compare.csv

    | openEuler                | Fedora32                 |
    | ------------------------ | ------------------------ |
    | XXX-release -> XXX-repos | XXX-release -> XXX-repos |
    | attr -> rpm-libs         | attr -> rpm-libs         |
    | audit-libs -> glibc      | audit-libs -> glibc      |
    | audit-libs -> libcap-ng  | audit-libs -> libcap-ng  |
    | #N/A                     | audit-libs -> rpm-libs   |
