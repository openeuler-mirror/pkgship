/**
 * @file  信息管理接口配置文件
 * */

 import appAjax from './../libs/ajax-utils';
 
 export const getObsInfo = ({
                                pkg_name,
                                gitee_branch,
                                architecture,
                                build_state,
                                sig_name,
                                page_index,
                                page_size
                            }) => {
     return new Promise((resolve, reject) => {
         appAjax.postJson({
             url: '/infoBoard/obs',
             type: 'get',
             params: {
                pkg_name,
                gitee_branch,
                architecture,
                build_state,
                sig_name,
                page_index,
                page_size
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
 
 export const getObsSuggests = (queryName) => {
     return new Promise((resolve, reject) => {
         appAjax.postJson({
             url: '/infoBoard/obs/package/suggest',
             type: 'get',
             params: {
                 query: queryName,
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

 export const getBranchSuggests = (queryName) => {
    return new Promise((resolve, reject) => {
        appAjax.postJson({
            url: '/infoBoard/obs/branch/suggest',
            type: 'get',
            params: {
                query: queryName,
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

export const getObsDown = ({
                               pkg_name,
                               gitee_branch,
                               architecture,
                               build_state,
                               sig_name
                           }) => {
    return new Promise((resolve, reject) => {
        appAjax.postJson({
            url: '/infoBoard/obs/export',
            type: 'post',
            responseType: 'blob',
            data: {
                pkg_name,
                gitee_branch,
                architecture,
                build_state,
                sig_name
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