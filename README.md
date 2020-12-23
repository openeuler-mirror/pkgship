# pkgship

<!-- TOC -->

- [pkgship](#pkgship)
    - [介绍](#介绍)
    - [架构](#架构)
    - [软件下载](#软件下载)
    - [运行环境](#运行环境)
    - [安装工具](#安装工具)
    - [配置参数](#配置参数)
    - [服务启动和停止](#服务启动和停止)
    - [工具使用](#工具使用)

<!-- /TOC -->

## 介绍
pkgship是一款管理OS软件包依赖关系，提供依赖和被依赖关系完整图谱的查询工具，pkgship提供软件包依赖查询、生命周期管理、补丁查询等功能。

1. 软件包依赖查询：方便社区人员在软件包引入、更新和删除的时候了解软件的影响范围。
2. 补丁查询：方便社区人员了解openEuler软件包的补丁情况以及提取补丁内容，详细内容请参见[patch-tracking](../patch-tracking/README.md)。

## 架构

系统采用flask-restful开发

![avatar](./doc/design/pkgimg/packagemanagement.JPG)

## 软件下载

* Repo源挂载正式发布地址：<https://repo.openeuler.org/>
* 源码获取地址：<https://gitee.com/openeuler/pkgship>
* rpm包版本获取地址：<https://117.78.1.88/project/show/openEuler:Mainline>

## 运行环境

* 可用内存700M以上
* python版本 3.8及以上

## 安装工具
工具安装可通过以下两种方式中的任意一种实现。

* 方法一，通过dnf挂载repo源实现。  
 先使用dnf挂载pkgship软件在所在repo源（具体方法可参考[应用开发指南](https://openeuler.org/zh/docs/20.09/docs/ApplicationDev/%E5%BC%80%E5%8F%91%E7%8E%AF%E5%A2%83%E5%87%86%E5%A4%87.html)），然后执行如下指令下载以及安装pkgship及其依赖。

    ```bash
    dnf install pkgship
    ```
* 方法二，通过安装rpm包实现。
 先下载pkgship的rpm包，然后执行如下命令进行安装（其中“x.x-x”表示版本号，请用实际情况代替）。

    ```bash
    rpm -ivh pkgship-x.x-x.oe1.noarch.rpm
    ```

    或者

    ```bash
    dnf install pkgship-x.x-x.oe1.noarch.rpm
    ```

## 配置参数
待更新

## 服务启动和停止
待更新

## 工具使用
