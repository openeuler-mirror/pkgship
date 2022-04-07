/**
 * @file  包管理 depend 接口配置文件
 * */

import appAjax from './../libs/ajax-utils';

export const dependList = ({
                               queryPkgName,
                               dependType,
                               parameter
                           }) => {
    return new Promise((resolve, reject) => {
        appAjax.postJson({
            url: '/dependinfo/dependlist',
            type: 'post',
            data: {
                packagename: queryPkgName,
                depend_type: dependType,
                parameter,
            },
            success(result) {
                if (result) {
                    resolve(result);
                    return;
                }
                reject(result);
            },
            error(msg) {
                reject(msg);
            }

        });

    });
};

export const dependDown = ({
                               queryPkgName,
                               dependType,
                               parameter
                           }) => {
    return new Promise((resolve, reject) => {
        appAjax.postJson({
            url: '/dependinfo/downloadfiles',
            type: 'post',
            responseType: 'blob',
            data: {
                packagename: queryPkgName,
                depend_type: dependType,
                parameter
            },
            success(result) {
                if (result) {
                    resolve(result);
                    return;
                }
                reject(result);
            },
            error(msg) {
                reject(msg);
            }

        });

    });
};

export const dependGraph = ({
                                queryPkgName,
                                dependType,
                                parameter,
                                node_name,
                                node_type
                            }) => {
    return new Promise((resolve, reject) => {
        appAjax.postJson({
            url: '/dependinfo/dependgraph',
            type: 'post',
            data: {
                packagename: queryPkgName,
                depend_type: dependType,
                parameter,
                node_name,
                node_type
            },
            success(result) {
                if (result) {
                    resolve(result);
                    return;
                }
                reject(result);
            },
            error(msg) {
                reject(msg);
            }

        });

    });
};