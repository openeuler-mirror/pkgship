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

export const version = () => {
    return new Promise((resolve, reject) => {
        appAjax.postJson({
            url: '/version',
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

export const packageDetail = ({database_name, pkg_name}) => {
    return new Promise((resolve, reject) => {
        appAjax.postJson({
            url: `/packages/src/${pkg_name}`,
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

export const packageSrcName = ({
                                   database_name,
                                   pkg_name
                               }, url) => {
    return new Promise((resolve, reject) => {
        appAjax.postJson({
            url: `/packages/src/$${url}`,
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


export const packageTablecol = () => {
    return new Promise((resolve, reject) => {
        appAjax.postJson({
            url: '/packages/tablecol',
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
export const packagevsersion = () => {
    return new Promise((resolve, reject) => {
        appAjax.postJson({
            url: '/version',
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