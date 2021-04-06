/**
 * @file  包管理 issue接口配置文件
 * */

import appAjax from './../libs/ajax-utils';
export const packageBin = ({
                               pageNum,  //当前页数
                               pageSize,  // 每页条数
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

export const issueDetail = ({database_name, pkg_name}) => {
    return new Promise((resolve, reject) => {
        appAjax.postJson({
            url: `/packages/bin/${pkg_name}`,
            type: 'get',
            params: {
                database_name,
                pkg_name
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