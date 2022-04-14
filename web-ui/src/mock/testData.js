export const iso_info = [
    {
        "branch":"openEuler-22.03-LTS-Next",
        "date": "2022-02-08",
        "build_result": "success",
        "build_time": 75
    }, 
    {
        "branch":"openEuler-22.03-LTS-Next",
        "date": "2022-02-09",
        "build_result": "success",
        "build_time": 36
    }, 
    {
        "branch":"openEuler-22.03-LTS-Next",
        "date": "2022-02-10",
        "build_result": "success",
        "build_time": 50
    }, 
    {
        "branch":"openEuler-22.03-LTS-Next",
        "date": "2022-02-11",
        "build_result": "failed",
        "build_time": 0
    },
    {
        "branch":"openEuler-22.03-LTS-Next",
        "date": "2022-02-12",
        "build_result": "success",
        "build_time": 50
    }, 
    {
        "branch":"openEuler-22.03-LTS-Next",
        "date": "2022-02-13",
        "build_result": "failed",
        "build_time": 0
    }, 
    {
        "branch":"openEuler-22.03-LTS-Next",
        "date": "2022-02-14",
        "build_result": "success",
        "build_time": 40
    }, 
    {
        "branch":"openEuler-22.03-LTS-Next",
        "date": "2022-02-15",
        "build_result": "success",
        "build_time": 76
    }, 
    {
        "branch":"openEuler-22.03-LTS-Next",
        "date": "2022-02-16",
        "build_result": "failed",
        "build_time": 0
    }, 
    {
        "branch":"openEuler-22.03-LTS-Next",
        "date": "2022-02-17",
        "build_result": "success",
        "build_time": 87
    }, 

]

export const pkg_build_states = {
    "unresolvable": 600,
    "broken": 1500,
    "blocked": 1780,
    "building": 750,
    "excluded": 1280,
    "succeeded": 950,
    "failed": 1650
}

export const pr_build_states = {
    "merged": 70,
    "close": 15,
    "open": 35
}

export const pkg_build_times = {
    "less_ten": 0,
    "ten_to_twenty": 0,
    "twenty_to_thirty": 0,
    "more_thirty": 499
}

export const pr_build_times = {
    "1-5天": 50,
    "6-10天": 30,
    ">10天": 20
}

export const  pkg_infos = [
    {
        "repo_name": "gcc", //(gitee仓库)
        "source_name": "gcc", //(源码包名)
        "gitee_version": "7.3.0", //(gitee软件包版本)
        "obs_version": "7.3.0", //(obs软件包版本)
        "architecture": "standard_x86_64", //(软件包架构)
        "gitee_branch": "openEuler-20.03-LTS-SP1", //(软件包所在gitee分支)
        "obs_branch": "openEuler:20.03:LTS:SP1", //(obs工程分支)
        "build_state": "building", //(编译状态)
        "build_detail_link": "https://117.78.1.88/package/live_build_log/openEuler:20.03:LTS:SP1/gcc/standard_x86_64/x86_64 (编译详情)",
        "build_time": 20, //(编译耗时，单位分钟)
        "history_build_times": [
            6,
            10,
            40,
            20,
            30
        ], //软件包近五次构建成功所用时间，单位分钟
        "sig_name": "Compiler", //(sig组名称)
        "mainttainer": [
            {
                "id": "yd_wang",
                "organization": "huawei",
                "email": "yadonn.wang@huawei.com"
            },
            {
                "id": "kuenking111",
                "organization": "huawei",
                "email": "wangkun49@huawei.com"
            }
        ], //(maintainer信息)
        "mentor": [
            {
                "id": "yd_wang",
                "organization": "huawei",
                "email": "yadonn.wang@huawei.com"
            },
            {
                "id": "kuenking111",
                "organization": "huawei",
                "email": "wangkun49@huawei.com"
            }
        ], //(维护者信息)
        "build_requires": [
            "glibc",
            "kernel"
        ] //(编译依赖信息)
    },
    // {


    //     "repo_name": "htc", //(gitee仓库)
    //     "source_name": "htc", //(源码包名)
    //     "gitee_version": "8.1.5", //(gitee软件包版本)
    //     "obs_version": "8.3.1", //(obs软件包版本)
    //     "architecture": "standard_x86_64", //(软件包架构)
    //     "gitee_branch": "openEuler-20.03-LTS-SP1", //(软件包所在gitee分支)
    //     "obs_branch": "openEuler:20.03:LTS:SP1", //(obs工程分支)
    //     "build_state": "closing", //(编译状态)
    //     "build_detail_link": "https://117.78.1.88/package/live_build_log/openEuler:20.03:LTS:SP1/gcc/standard_x86_64/x86_64 (编译详情)",
    //     "build_time": 45, //(编译耗时，单位分钟)
    //     "history_build_times": [
    //         6,
    //         10,
    //         40,
    //         20,
    //         30
    //     ], //软件包近五次构建成功所用时间，单位分钟
    //     "sig_name": "hostinfo", //(sig组名称)
    //     "mainttainer": [
    //         {
    //             "id": "lilei",
    //             "organization": "huawei",
    //             "email": "lilei@huawei.com"
    //         },
    //         {
    //             "id": "jiesi489",
    //             "organization": "huawei",
    //             "email": "jiesi489@huawei.com"
    //         }
    //     ], //(maintainer信息)
    //     "mentor": [
    //         {
    //             "id": "lilei",
    //             "organization": "huawei",
    //             "email": "lilei@huawei.com"
    //         },
    //         {
    //             "id": "jiesi489",
    //             "organization": "huawei",
    //             "email": "jiesi489@huawei.com"
    //         }
    //     ], //(维护者信息)
    //     "build_requires": [
    //         "fgigy",
    //         "clatcal"
    //     ] //(编译依赖信息)
    // }
]

export const  pr_infos = [
    {
        "repo_name": "ignite", //(gitee仓库)
        "pr_title": "关于对A-Ops前端项目漏洞管理模块处cve不能手动刷新问题的处理", //(pr标题))
        "pr_build_link": "https://gitee.com/src-openeuler/ignite/pills/4", //(pr链接)
        "pr_state": "open", //(pr状态)
        "gitee_branch": "master", //(软件包所在gitee分支)
        "submitter": "zhangshaoning", //(提交人)
        "submit_time": "2022-02-23", //(提交时间)
        "open_time": "8天", //(开启时长)
        "access_result": "succeed", //(门禁结果)
        "access_build_link": "https://117.78.1.88/package/live_build_log/openEuler:20.03:LTS:SP1/gcc/standard_x86_64/x86_64", //(门禁链接)
        "sig_name": "sig-ai-bigdata", //(sig组名称)
        "relation_issue": "I4Q1FD", //(关联issue)
        "mainttainer": [
            {
                "id": "yd_wang",
                "organization": "huawei",
                "email": "yadonn.wang@huawei.com"
            },
            {
                "id": "kuenking111",
                "organization": "huawei",
                "email": "wangkun49@huawei.com"
            }
        ], //(maintainer信息)
        "mentor": [
            {
                "id": "yd_wang",
                "organization": "huawei",
                "email": "yadonn.wang@huawei.com"
            },
            {
                "id": "kuenking111",
                "organization": "huawei",
                "email": "wangkun49@huawei.com"
            }
        ], //(相关人员)
    },
]

export const sig_infos = [
    {
        "name": "Base-service",
        "description": "The Base-service team is responsible for maintain the basic package for linux.",
        "maintainer": [ 
            {
                "id": "zhujianwei001",
                "organization": "huawei",
                "email": "zhujianwei7@huawei.com"
            },
            {
                "id": "xiezhipeng1",
                "organization": "huawei",
                "email": "xiezhipeng1@huawei.com"
            }
        ],
        "mentors": [
            {
                "id": "licihua",
                "organization": "huawei",
                "email": "licihua@huawei.com"
            }
        ],
        "repositories": [
            "openeuler/openEuler-rpm-config",
            "src-openeuler/abseil-cpp"
        ]
    },
    {
        "name": "Base-service",
        "description": "The Base-service team is responsible for maintain the basic package for linux.",
        "maintainer": [ 
            {
                "id": "zhujianwei001",
                "organization": "huawei",
                "email": "zhujianwei7@huawei.com"
            },
            {
                "id": "xiezhipeng1",
                "organization": "huawei",
                "email": "xiezhipeng1@huawei.com"
            }
        ],
        "mentors": [
            {
                "id": "licihua",
                "organization": "huawei",
                "email": "licihua@huawei.com"
            }
        ],
        "repositories": [
            "openeuler/openEuler-rpm-config",
            "src-openeuler/abseil-cpp"
        ]
    },
    {
        "name": "Base-service",
        "description": "The Base-service team is responsible for maintain the basic package for linux.",
        "maintainer": [ 
            {
                "id": "zhujianwei001",
                "organization": "huawei",
                "email": "zhujianwei7@huawei.com"
            },
            {
                "id": "xiezhipeng1",
                "organization": "huawei",
                "email": "xiezhipeng1@huawei.com"
            }
        ],
        "mentors": [
            {
                "id": "licihua",
                "organization": "huawei",
                "email": "licihua@huawei.com"
            }
        ],
        "repositories": [
            "openeuler/openEuler-rpm-config",
            "src-openeuler/abseil-cpp"
        ]
    },
    {
        "name": "Base-service",
        "description": "The Base-service team is responsible for maintain the basic package for linux.",
        "maintainer": [ 
            {
                "id": "zhujianwei001",
                "organization": "huawei",
                "email": "zhujianwei7@huawei.com"
            },
            {
                "id": "xiezhipeng1",
                "organization": "huawei",
                "email": "xiezhipeng1@huawei.com"
            }
        ],
        "mentors": [
            {
                "id": "licihua",
                "organization": "huawei",
                "email": "licihua@huawei.com"
            }
        ],
        "repositories": [
            "openeuler/openEuler-rpm-config",
            "src-openeuler/abseil-cpp"
        ]
    },
    {
        "name": "Base-service",
        "description": "The Base-service team is responsible for maintain the basic package for linux.",
        "maintainer": [ 
            {
                "id": "zhujianwei001",
                "organization": "huawei",
                "email": "zhujianwei7@huawei.com"
            },
            {
                "id": "xiezhipeng1",
                "organization": "huawei",
                "email": "xiezhipeng1@huawei.com"
            }
        ],
        "mentors": [
            {
                "id": "licihua",
                "organization": "huawei",
                "email": "licihua@huawei.com"
            }
        ],
        "repositories": [
            "openeuler/openEuler-rpm-config",
            "src-openeuler/abseil-cpp"
        ]
    }
]

export const iso_success_rate = "95%"