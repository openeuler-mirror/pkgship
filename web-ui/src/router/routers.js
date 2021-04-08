/**
 * @file  路由配置文件
 * */

export default [{
    path: '/',
    component: () => import('@/views/home/home.vue')
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