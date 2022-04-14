/**
 * @file  路由配置文件
 * */

export const constantRouterMap = [
    {
        path: '/',
        component: () => import('@/views/home/home.vue')
        // redirect: '/Home',
    },
    // {
    //     path: '/Home',
    //     name: 'Home',
    //     component: () => import('@/views/home/home.vue')
    // },
    {
        path: '/Packagemanagement',
        name: 'Packagemanagement',
        component: () => import('@/views/home/Packagemanagement.vue')
    },
    {
        path: '/Infomanagement',
        name: 'Infomanagement',
        meta: {
            keepAlive: true
        },
        component: () => import('@/views/home/Infomanagement.vue')
    },
    {
        path: '/sig-detail',
        component: () => import('@/views/package/sig-detail.vue')
    },
    {
        path: '/source-detail',
        component: () => import('@/views/package/source-detail.vue')
    },
    {
        path: '/binary-detail',
        component: () => import('@/views/package/binary-detail.vue')
    },
    {
        path: '*',
        component: () => import('@/views/404.vue')
    }
];