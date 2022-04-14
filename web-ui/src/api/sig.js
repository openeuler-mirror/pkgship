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