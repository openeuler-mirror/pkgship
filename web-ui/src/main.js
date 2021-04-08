/**
 * @file  vue组件主入口
 * */

import Vue from 'vue';
import App from './App.vue';
import router from './router';
import ElementUI from 'element-ui';
import locale from 'element-ui/lib/locale/lang/en';
import '@/assets/style/base.css';
import  echarts from 'echarts';

if (!localStorage.getItem('locale') || localStorage.getItem('locale') === 'zh-en') {
    import('@/assets/style/font-en.css');
} else {
    import('@/assets/style/font-cn.css');
}

Vue.use(ElementUI, {locale});
Vue.use(echarts);
Vue.prototype.$echarts = echarts;
Vue.config.productionTip = false;

new Vue({
    router,
    render: h => h(App)
}).$mount('#app');