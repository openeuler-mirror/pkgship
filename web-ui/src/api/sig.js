/**
 * @file  信息管理接口配置文件
 * */

 import appAjax from './../libs/ajax-utils';
 
 export const getSigInfo = (sig_name) => {
     return new Promise((resolve, reject) => {
         appAjax.postJson({
             url: '/infoBoard/sig',
             type: 'get',
             params: {
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

 export const getSigDown = ({
                               sig_name
                           }) => {
    return new Promise((resolve, reject) => {
        appAjax.postJson({
            url: '/infoBoard/sig/export',
            type: 'post',
            responseType: 'blob',
            data: {
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

export const getSigSuggests = (querySigName) => {
    return new Promise((resolve, reject) => {
        appAjax.postJson({
            url: '/infoBoard/obs/sig/suggest',
            type: 'get',
            params: {
                query: querySigName
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