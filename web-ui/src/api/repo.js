/**
 * @file  包管理接口配置文件
 * */

import appAjax from './../libs/ajax-utils';

export const dbPriority = () => {
    return new Promise((resolve, reject) => {
        appAjax.postJson({
            url: '/db_priority',
            type: 'get',
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

export const packageSrc = ({
                               pageNum,
                               pageSize,
                               queryPkgName,
                               tableName
                           }) => {
    return new Promise((resolve, reject) => {
        appAjax.postJson({
            url: '/packages/src',
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

export const packageDetail = ({databaseName, pkgName}) => {
    return new Promise((resolve, reject) => {
        appAjax.postJson({
            url: `/packages/src/${pkgName}`,
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