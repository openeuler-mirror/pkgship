<template>
    <div>
      <div class="home">
            <h1>{{ sig_name }}</h1>
            <el-input
                v-model="querySigName"
                class="pc-search"
                placeholder="Search SigName"
                @keyup.enter.native="queryData()">
                <i slot="suffix" class="icon-search" @click="queryData()"></i>
            </el-input>
            <div class="package-container">
                <div class="pc-pkg-table" v-for="(item, index) in tableData" :key="index">
                    <ul class="repositories-line" v-if="visMsg">
                        <li class="detail-title"><span>{{index + 1 + numSize}}</span><span style="margin-left:30px;">{{item}}</span></li>
                    </ul>
                </div>
                <ul class="repositories-line" v-if="!visMsg">
                        <li class="detail-title"><span>No data</span></li>
                </ul>
                <el-pagination
                    class="safety-bulletin-pagination"
                    :current-page.sync="pageNum"
                    :page-size="pageSize"
                    layout="total, prev, pager, next, jumper"
                    @current-change="initData"
                    :total="total"
                    v-if="visMsg">
                </el-pagination>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: 'SigDetail',
    mounted(){
       this.initData()
    },
    created(){
        this.sig_name = this.$route.query.sig_name
        this.propData = this.$route.query.repositories
        console.log(this.sig_name);
        console.log(this.propData);
    },
    data() {
        return {
            visMsg: true,
            querySigName: '',
            sig_name: '',
            tableData: [],
            propData: [],
            tableLoading: false,
            total: 0,
            pageNum: 1,
            pageSize: 10,
            numSize: 0
        }
    },
    methods: {
        initData() {
            this.getTablePage()
        },
        getTablePage() {
            var dataLength = this.propData.length
            this.total = dataLength
            var PageMax = Math.ceil(dataLength/this.pageSize)
            if ( this.pageNum != PageMax ) {
              this.tableData = this.propData.slice(((this.pageNum - 1) * this.pageSize), ((this.pageNum - 1) * this.pageSize) + this.pageSize)
              this.numSize = (this.pageNum - 1) * this.pageSize
            } else {
              this.tableData = this.propData.slice(this.pageSize * (PageMax - 1), dataLength)
              this.numSize = (PageMax - 1) * this.pageSize
            }
        },
        queryData() {
            if (this.querySigName.length === 0 || this.querySigName.split(" ").join("").length === 0) {
                this.visMsg = true
                this.initData()
            } else {
               if (this.propData.indexOf(this.querySigName) === -1) {
                  this.visMsg = false
               } else {
                  this.visMsg = true
                  this.tableData = [this.querySigName]
                  this.total = 1
                  this.pageNum = 1
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
.safety-bulletin-pagination {
    display: block;
    margin: 30px 0 200px 0!important;
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