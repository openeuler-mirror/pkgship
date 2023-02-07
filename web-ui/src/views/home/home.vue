<template>
    <div>
        <div class="first-page">
            <h1>Packages in the palm of your hand</h1>
            <div style="display:flex">
               <p>Pkgship – A query tool that manages OS software package information and dependencies.</p>
               <p>Pkgship-panel – A query tool that package build status and maintenance information.</p>
            </div>
            <div style="display:flex">
               <p class="btn-start" @click="jump('pack')">Package Management</p>
               <p class="btn-start" @click="jump('info')">Info Management</p>
            </div>
            <img class="icon-earth" src="@/assets/images/earth.svg" alt="">
            <img class="icon-pack" :class="[isWait ? 'wait' : '']" src="@/assets/images/icon-pack.png" alt="">
        </div>
        <!-- <div class="home" :class="[isHomeShow ? 'home' : 'home-hide']">
            <h1>Package Management</h1>
            <div class="switcher">
                <a :class="{'active': isInfoShow }" @click="showInfo">Source Info</a>
                <el-tooltip class="item" effect="light" content="查询源码包信息" placement="top">
                        <img src="@/assets/images/question.svg" alt="">
                </el-tooltip>
                <a :class="{'active': isListShow }" @click="showList">Binary Info</a>
                <el-tooltip class="item" effect="light" content="查询二进制包信息" placement="top">
                        <img src="@/assets/images/question.svg" alt="">
                </el-tooltip>
                <a :class="{'active': isDependShow }" @click="showDepend">Depend Info</a>
                <el-tooltip class="item" effect="light" content="查询软件包依赖关系" placement="top">
                        <img src="@/assets/images/question.svg" alt="">
                </el-tooltip>
            </div>
            <div class="package-container">
                <package-Info v-if="isInfoShow" />
                <issue-list v-if="isListShow" />
                <depend-info v-if="isDependShow" />
            </div>
        </div> -->
    </div>
</template>

<script>
// import InfoList from "./source-info";
// import IssueList from "./binary-info";
// import DependInfo from "./depend-info";

export default {
    name: "Home",
    components: {},
    mounted() {
        let _self = this;
        setTimeout(function () {
            _self.isWait = false;
        }, 2000);
    },
    data() {
        return {
            // isInfoShow: false,
            // isListShow: false,
            // isDependShow: false,
            // isHomeShow: false,
            isWait: true
        }
    },
    methods: {
        jump(msg){
            if(msg === 'pack'){
               this.$router.push('/Packagemanagement')
            }
            else {
               this.$router.push('/Infomanagement')
            }
        }
    }
};
</script>

<style scoped>

@keyframes toOpacity {
    0% { opacity: 0;}
    50% { opacity: 0; }
    100% { opacity: 1;}
}
.item{
    position: relative;
    left: -35px;
    top: 2px;
}
.tool-tips{
    position: absolute;
    left: -12px;
    top: 12px;
}
.icon-earth {
    animation: toOpacity 2s;
}
.icon-pack.wait {
    display: none;
}
.icon-pack {
    animation: toOpacity 2s;
    position: absolute;
    left: 0;
}
h1 {
    font-size: 36px;
    font-family: HuaweiSans-Medium;
    margin: 60px 0;
}
.home {
    width: 1200px;
    margin: 0 auto;
}
.first-page {
    width: 1200px;
    margin: 0 auto;
    text-align: center;
    position: relative;
}
.first-page h1 {
    font-size: 60px;
    text-align: center;
    margin-bottom: 43px;
}
.first-page p {
    width: 620px;
    font-size: 18px;
    line-height: 21px;
    margin: 0 auto;
}
.first-page .btn-start {
    width: 227px;
    height: 48px;
    color: #fff;
    font-size: 18px;
    padding: 14px 0;
    margin: 45px auto 65px;
    background: #002FA7;
    border: none;
    border-radius: 8px;
    cursor: pointer;
}
.first-page img {
    max-width: 1200px;
}
/* .home-hide {
    display: none;
} */
.switcher a {
    font-size: 24px;
    font-family: HuaweiSans-Medium;
    color: rgba(0, 0, 0, 0.5);
    margin-right: 40px;
    cursor: pointer;
    padding-bottom: 10px;
    margin-bottom: 30px;
}
.switcher .active {
    color: #000;
    display: inline-block;
    border-bottom: 4px solid #002fa7;

}
@media screen and (max-width: 1000px) {
    .home {
        width: 100%;
        padding: 0 30px;
    }
    h1 {
        font-size: 18px;
        font-family: FZLTCHJW;
        margin: 40px 0;
    }
    .switcher a {
        font-size: 16px;
        margin-right: 18px;
    }
}
</style>
