<template>
    <div>
      <div class="home">
            <div style="display:flex;">
               <h1>{{ sig_name }}</h1>
               <i class="el-icon-back backBtn" @click="goBack"></i>
               <span class="backMsg" @click="goBack">Go back</span>
            </div>
            <el-input
                v-model="queryPackageName"
                class="pc-search"
                placeholder="Search PackageName"
                @keyup.enter.native="queryData()">
                <i slot="suffix" class="icon-search" @click="queryData()"></i>
            </el-input>
            <div class="package-container">
                <div class="pc-pkg-table" v-if="visMsg">
                    <ul class="repositories-line" v-for="(item, index) in tableData.slice(0,10)" :key="'infoA' + index">
                        <li class="detail-title"><span>{{index + 1}}</span><span style="margin-left:30px;">{{item}}</span></li>
                    </ul>
                    <ul class="repositories-line" v-if="tableData.length > 10 && !moreMsg">
                        <li @click="showMore" style="color:#2b4490;cursor: pointer;font-weight: bold;">Show More</li>
                    </ul>
                    <ul class="repositories-line" v-for="(item, index) in tableData.slice(10)" :key="'infoB' + index">
                        <li class="detail-title" v-if="moreMsg"><span>{{index + 11}}</span><span style="margin-left:30px;">{{item}}</span></li>
                    </ul>
                </div>
                <ul class="repositories-line" v-if="!visMsg">
                        <li class="detail-title" style="font-weight: bold;"><span>No Result</span></li>
                </ul>
            </div>
        </div>
    </div>
</template>

<script>
import { getSigInfo } from '../../api/sig'
export default {
    name: 'SigDetail',
    mounted(){
       this.initData()
    },
    created(){
        this.sig_name = this.$route.query.sig_name
    },
    data() {
        return {
            visMsg: true,
            moreMsg: false,
            queryPackageName: '',
            sig_name: '',
            tableData: [],
            propData: [],
            tableLoading: false,
        }
    },
    methods: {
        initData() {
            this.getPropData()
        },
        getPropData(){
            this.tableLoading = true
            getSigInfo(this.sig_name)
                .then(response => {
                    if(response.code === '200') {
                        // this.tableData = response.resp;
                        this.tableLoading = false
                        this.propData = response.resp[0].repositories
                        this.tableData = this.propData
                    } else {
                        this.tableLoading = false
                        this.$message.error(response.message + '\n' + response.tip);
                    }
                })
                .catch(response => {
                    this.tableLoading = false
                    this.$message.error(response.message + '\n' + response.tip);
                })
                .finally(function () {
                //   this.tableLoading = false;
                })
        },
        goBack() {
            this.$router.go(-1)
        },
        showMore() {
            this.moreMsg = true
        },
        queryData() {
            this.tableData = []
            this.moreMsg = false //重置默认属性
            if (this.queryPackageName.length === 0 || this.queryPackageName.split(" ").join("").length === 0) {
                this.visMsg = true
                this.initData()
            } else {
                let reg = new RegExp(this.queryPackageName)
                for(let i = 0; i < this.propData.length; i++) {
                        if(this.propData[i].match(reg)) {
                           this.tableData.push(this.propData[i])
                        }
                }
                var dataLength = this.tableData.length
                if (dataLength === 0) {
                   this.visMsg = false
                } else {
                   this.visMsg = true
                }
            }  
        }
    }
}
</script>

<style scoped>

@keyframes toOpacity {
    0% { opacity: 0;}
    50% { opacity: 0; }
    100% { opacity: 1;}
}
.backBtn {
    position: absolute;
    right: 250px;
    margin-top: 70px;
    font-size: 29px;
    color: #002FA7;
    cursor: pointer;
}
.backMsg{
    position: absolute;
    right: 168px;
    margin-top: 71px;
    font-size: 18px;
    color: #002FA7;
    cursor: pointer;
}
.icon-search {
    position: absolute;
    cursor: pointer;
    margin-top: 13px;
    margin-left: -20px;
}
.pc-search {
    width: 260px;
    margin-bottom: 30px;
}
.repositories-line {
    width: 100%;
    height: 40px;
}
.pc-pkg-table {
    width: 100%;
    display: block;
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
    margin-top: 60px;
    margin-bottom: 30px;
}
.home {
    width: 1300px;
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