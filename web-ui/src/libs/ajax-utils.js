/**
 * @file  axios工具类
 * */

import axios from 'axios';
import config from '@/config';
import Vue from 'vue';

let postJson = params => {
    let api = axios.create({
        baseURL: config.serviceBaseUrl || ''
    });
    api.defaults.headers.post['Content-Type'] = 'application/json';

    // 请求数据
    let dataStr = params['data'] && ((typeof (params['data']) === 'object')
        ? JSON.stringify(params['data']) : params['data']);

    let ajaxParams = {};
    // success方法重载
    ajaxParams['success'] = function (d) {
        if (params.responseType) {
            const data = d.data;
            if (data) {
                params.success(data);
            } else {
                new Vue().$message.error('Please try again later');
            }
        } else {
            const data = typeof d.data === 'string' ? JSON.parse(d.data) : d.data;
            if (data.code === '200') {
                params.success(data);
            } else {
                new Vue().$message.error(data.message + '\n' + data.tip);
            }
        }
    };

    return api({
        method: params['type'] || 'post',
        url: params['url'],
        data: dataStr,
        params: params['params'],
        responseType: params['responseType'] || 'json',
        timeout: 60000
    }).then(ajaxParams['success']).catch(params['error']);
};

let exportsMethods = {
    postJson: params => postJson(params)
};

export default exportsMethods;