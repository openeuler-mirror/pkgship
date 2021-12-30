<template>
    <div>
      <div class="home">
            <h1>Package Management</h1>
            <div class="switcher">
                <a :class="{'active': isInfoShow }" @click="showInfo">Source Info</a>
                <el-tooltip class="item" effect="light" content="Query source code package information" placement="top">
                        <img src="@/assets/images/question.svg" alt="">
                </el-tooltip>
                <a :class="{'active': isListShow }" @click="showList">Binary Info</a>
                <el-tooltip class="item" effect="light" content="Query binary package information" placement="top">
                        <img src="@/assets/images/question.svg" alt="">
                </el-tooltip>
                <a :class="{'active': isDependShow }" @click="showDepend">Depend Info</a>
                <el-tooltip class="item" effect="light" content="Query software package dependencies" placement="top">
                        <img src="@/assets/images/question.svg" alt="">
                </el-tooltip>
            </div>
            <div class="package-container">
                <package-Info v-if="isInfoShow" />
                <issue-list v-if="isListShow" />
                <depend-info v-if="isDependShow" />
            </div>
        </div>
    </div>
</template>

<script>
import InfoList from "./source-info";
import IssueList from "./binary-info";
import DependInfo from "./depend-info";

export default {
    name: 'Packagemanagement',
    components: {
        "package-Info": InfoList,
        "issue-list": IssueList,
        "depend-info": DependInfo
    },
    mounted(){

    },
    created(){
        this.isInfoShow = true;
        this.isListShow = false;
        this.isDependShow = false;
    },
    data() {
        return {
            isInfoShow: false,
            isListShow: false,
            isDependShow: false,
        }
    },
    methods: {
        showInfo() {
            this.isInfoShow = true;
            this.isListShow = false;
            this.isDependShow = false;
        },
        showList() {
            this.isListShow = true;
            this.isInfoShow = false;
            this.isDependShow = false;
        },
        showDepend() {
            this.isInfoShow = false;
            this.isListShow = false;
            this.isDependShow = true;
        },
    }
}
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
.home-hide {
    display: none;
}
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