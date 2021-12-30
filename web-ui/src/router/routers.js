/**
 * @file  路由配置文件
 * */

export const constantRouterMap = [
    {
        path: '/',
        redirect: '/Home',
    },{
        path: '/Home',
        name: 'Home',
        component: () => import('@/views/home/home.vue')
    },
    {
        path: '/Packagemanagement',
        name: 'Packagemanagement',
        component: () => import('@/views/home/Packagemanagement.vue')
    },
    // {
    //     path: '/source-info',
    //     name: 'package-info',
    //     component: () => import('@/views/home/source-info.vue')
    // },
    // {
    //     path: '/binary-info',
    //     name: 'issue-list',
    //     component: () => import('@/views/home/binary-info.vue')
    // },
    // {
    //     path: '/depend-info',
    //     name: 'depend-info',
    //     component: () => import('@/views/home/depend-info.vue')
    // },
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