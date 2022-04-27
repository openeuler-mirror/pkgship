<template>
    <div>
      <div class="home">
            <h1>Info Management</h1>
            <div class="switcher">
                <a :class="{'active': isObsShow }" @click="showObs">OBS构建</a>
                <el-tooltip class="item" effect="light" content="Query binary package information" placement="top">
                        <img src="@/assets/images/question.svg" alt="">
                </el-tooltip>
                <!-- <a :class="{'active': isPrShow }" @click="showPr">PR信息</a>
                <el-tooltip class="item" effect="light" content="Query source code package information" placement="top">
                        <img src="@/assets/images/question.svg" alt="">
                </el-tooltip> -->
                <a :class="{'active': isSigShow }" @click="showSig">SIG组</a>
                <el-tooltip class="item" effect="light" content="Query source code package information" placement="top">
                        <img src="@/assets/images/question.svg" alt="">
                </el-tooltip>
            </div>
            <div class="package-container">
                <obs-info v-if="isObsShow" />
                <pr-info v-if="isPrShow" />
                <sig-info v-if="isSigShow" />
            </div>
        </div>
    </div>
</template>

<script>
import ObsList from "./obs-info";
import SigList from "./sig-info";
import PrList from './pr-info';

export default {
    name: 'Infomanagement',
    components: {
        "obs-info": ObsList,
        "sig-info": SigList,
        "pr-info": PrList,
    },
    mounted(){

    },
    created(){
        this.isObsShow = true;
        this.isSigShow = false;
        this.isPrShow = false;
    },
    data() {
        return {
            isObsShow: false,
            isSigShow: false,
            isPrShow: false,
        }
    },
    methods: {
        showObs() {
            this.isObsShow = true;
            this.isSigShow = false;
            this.isPrShow = false;
        },
        showSig() {
            this.isObsShow = false;
            this.isSigShow = true;
            this.isPrShow = false;
        },
        showPr() {
            this.isObsShow = false;
            this.isSigShow = false;
            this.isPrShow = true;
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
    width: 1800px;
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