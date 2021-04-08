/**
 * @file  包管理 issue接口配置文件
 * */

import appAjax from './../libs/ajax-utils';
export const packageBin = ({
                               pageNum,
                               pageSize,
                               queryPkgName,
                               tableName
                           }) => {
    return new Promise((resolve, reject) => {
        appAjax.postJson({
            url: '/packages/bin',
            type: 'get',
            params: {
                database_name: tableName,
                page_num: pageNum,
                page_size: pageSize,
                query_pkg_name: queryPkgName
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

export const issueDetail = ({databaseName, pkgName}) => {
    return new Promise((resolve, reject) => {
        appAjax.postJson({
            url: `/packages/bin/${pkgName}`,
            type: 'get',
            params: {
                database_name: databaseName,
                pkg_name: pkgName
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