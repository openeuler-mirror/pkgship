<template>
    <div class="package-info">
        <el-form
            :inline="true"
            class="form">
            <div class="form-inputs">
                <el-form-item label="软件包:">
                    <el-autocomplete
                        v-model="formData.pkg_name"
                        class="pc-search"
                        placeholder="请输入包名"
                        :fetch-suggestions="querySearchPkg"
                        @keyup.enter.native="initData()"
                        @select="initData()">
                        <i slot="suffix" class="icon-search" @click="initData()"></i>
                    </el-autocomplete>
                </el-form-item>
                <el-form-item label="gitee分支版本:">
                    <el-autocomplete
                        v-model="formData.gitee_branch"
                        class="pc-search"
                        placeholder="请输入分支版本"
                        :fetch-suggestions="querySearchBrh"
                        @keyup.enter.native="initData()"
                        @select="initData()">
                        <i slot="suffix" class="icon-search" @click="initData()"></i>
                    </el-autocomplete>
                </el-form-item>
                <el-form-item label="架构:">
                    <el-select class="pc-select" v-model="formData.architecture" @change="initData()" placeholder="请输入分支版本">
                        <el-option v-for="(item, index) in productV" :key="index"
                                   :label="item"
                                   :value="item">
                        </el-option>
                    </el-select>
                </el-form-item>
            </div>
            <div class="listinfo">
              <el-dropdown :hide-on-click="false" ref="messageDrop" @visible-change="changeStatic">
                <div class="el-dropdown-link">
                  <span style="margin-right: 10px;">展示信息</span><i :class="showFlag === true ? 'el-icon-arrow-down' : 'el-icon-arrow-up'"></i>
                </div>
                <el-dropdown-menu slot="dropdown">
                  <el-dropdown-item>
                      <el-checkbox label="依赖信息" v-model="checked1"></el-checkbox>
                  </el-dropdown-item>
                  <el-dropdown-item>
                      <el-checkbox label="gitee版本" v-model="checked2"></el-checkbox>
                  </el-dropdown-item>
                  <el-dropdown-item>
                      <el-checkbox label="源码包" v-model="checked3"></el-checkbox>
                  </el-dropdown-item>
                  <!-- <div class="el-dropdown-buttom"> -->
                      <!-- <el-button class="dropdownbutton" type="primary" @click="dropListChange"><span>确定</span></el-button> -->
                      <!-- <el-button class="dropdownbutton" type="warning" @click="resetdrop"><span>重置</span></el-button>
                  </div> -->
                </el-dropdown-menu>
              </el-dropdown>
              <el-button type="primary" style="background-color: #002fa7;width:120px;font-size: 18px;border:none;" @click="initData()">搜索</el-button>
            </div>
            <div class="form-btns">
                <el-form
                    :inline="true"
                    class="form">
                    <a class="form-button" @click="excelDownload" ref="srcDown">
                        <img src="@/assets/images/dowmload.svg" alt="">
                        Export Excel
                    </a>
                </el-form>
                <el-tooltip class="export-default-explain" content="Export the query result" placement="bottom" effect="light">
                             <img src="@/assets/images/question.svg" alt="">
                </el-tooltip>
            </div>
        </el-form>
        <template>
            <el-table
                :data="tableData"
                class="pc-pkg-table"
                stripe
                style="width: 100%"
                v-loading.fullscreen="loading">
                <el-table-column
                    prop="repo_name"
                    label="仓库名称"
                    width="180">
                </el-table-column>
                <el-table-column
                    prop="obs_branch"
                    label="obs工程分支"
                    width="250">
                </el-table-column>
                <el-table-column
                    prop="build_status"
                    label="编译状态"
                    width="180">
                </el-table-column>
                <el-table-column
                    prop="build_detail_link"
                    label="编译详情"
                    width="350"
                    :show-overflow-tooltip="true">
                </el-table-column>
                <el-table-column
                    prop="build_time"
                    label="编译耗时(min)"
                    width="180">
                </el-table-column>
                <el-table-column
                    prop="sig_name"
                    label="SIG组"
                    width="180"
                    :show-overflow-tooltip="true">
                </el-table-column>
                <el-table-column
                    prop="maintainer"
                    label="maintainer"
                    width="350"
                    :show-overflow-tooltip="true">
                    <template slot-scope="scope">
                        <span v-for="(item, index) in scope.row.maintainer" :key="index">
                            姓名:{{item.id}} | 邮箱:{{item.email}}
                        </span>
                    </template>
                </el-table-column>
                <el-table-column
                    prop="mentors"
                    label="维护者"
                    width="350"
                    :show-overflow-tooltip="true">
                    <template slot-scope="scope">
                        <span v-for="(item, index) in scope.row.mentors" :key="index">
                           姓名:{{item.id}} | 邮箱:{{item.email}}
                        </span>
                    </template>
                </el-table-column>
                <el-table-column
                    v-if="checked1"
                    prop="build_requires"
                    label="依赖信息"
                    width="200">
                </el-table-column>
                <el-table-column
                    v-if="checked2"
                    prop="gitee_version"
                    label="gitee版本"
                    width="180">
                </el-table-column>
                <el-table-column
                    v-if="checked3"
                    prop="source_name"
                    label="源码包"
                    width="180">
                </el-table-column>
            </el-table>
        </template>
        <el-pagination
            class="safety-bulletin-pagination"
            :current-page.sync="formData.page_index"
            :page-size="formData.page_size"
            layout="total, prev, pager, next, jumper"
            @current-change="initData()"
            :total="total">
        </el-pagination>
        <el-pagination
            class="mobile-safety-bulletin-pagination"
            :current-page.sync="formData.page_index"
            :page-size="formData.page_size"
            layout="prev, pager, next"
            @current-change="initData()"
            :total="total">
        </el-pagination>
        <div class="map-container">
            <div class="map-left" v-if="pieVisible">
                <pie-chart :title="title1" :pieData="pieData1"></pie-chart>
            </div>
            <div class="map-right" v-if="pieVisible">
                <span class="isomsg">iso构建成功率:{{ msg }}</span>
                <line-chart 
                :title="title2"
                :xAxisData="xAxisData1"
                :linedata="data1"
                 />
            </div>
            <div class="map-left" v-if="pieVisible">
                <pie-chart :title="title3" :pieData="pieData2"></pie-chart>
            </div>
            <div class="map-right" v-if="queryIf">
                <line-chart
                @closepop="closelineChart"
                :title="title4"
                :xAxisData="xAxisData2"
                :linedata="data2" />
            </div>
        </div>
    </div>
</template>

<script>
import { getObsInfo } from '../../api/obs'
import { getObsSuggests } from '../../api/obs'
import { getBranchSuggests } from '../../api/obs'
import { getObsDown } from '../../api/obs'
import PieChart from '@/components/PieChart.vue'
import LineChart from '@/components/LineChart.vue'

//测试数据
// import { iso_info,pkg_build_states,pkg_build_times,pkg_infos,iso_success_rate } from '@/mock/testData'
// import { pkg_build_states,pkg_build_times } from '@/mock/testData'
export default {
    name: "obs-info",
    components: {
      PieChart,
      LineChart
    },
    data() {
        return {
            checked1:false,
            checked2:false,
            checked3:false,
            showFlag:false,
            search: '',
            tableName: '',
            msg:'95%',
            pieVisible: false,
            formData: {
                page_index: 1,
                page_size: 10,
                pkg_name: "",
                gitee_branch: "openEuler-20.03-LTS-SP3",
                architecture: "standard_x86_64",
                build_state: '',
                sig_name: ''
            },
            loading: false,
            queryIf: false,
            pkgName: "",
            total: 0,
            productV: ["standard_x86_64","standard_aarch64"],
            tableTitle: ['Name', 'Version', 'Release', 'URL', 'License'],
            tableData: [],
            excelUrl: "",
            giteevalue: "",
            title1: '软件包编译状态分布图',
            title2: '近十天iso构建时间对比图',
            title3: '软件包平均构建时长',
            title4: '单包近5次构建成功的时间(只在搜索具体软件包时显示)',
            pieData1: [],
            pieData2: [],
            xAxisData1: [1,2,3,4,5,6,7,8,9,10],
            xAxisData2: [1,2,3,4,5],
            data1: [],
            data2: [],
            pieData: [],
            roseData: [],
            timeout:  null
        }
    },
    mounted() {
        this.initData();
    },
    methods: {
        getTablePage () {
            this.queryIf = false
            this.loading = true
            getObsInfo(this.formData)
                .then(response => {
                    if(response.code === '200') {
                        this.loading = false
                        this.pieVisible = true
                        this.tableData = response.resp.pkg_infos;
                        this.total = response.resp.total_count;
                        // 真实接口返回的数据处理
                        this.pieData1 = Object.keys(response.resp.pkg_build_states).map(key => ({ name:key,value:response.resp.pkg_build_states[key] }))
                        this.pieData2 = Object.keys(response.resp.pkg_build_times).map(key => ({ name:key,value:response.resp.pkg_build_times[key] }))
                        this.msg = response.resp.iso_success_rate
                        this.data1 = response.resp.iso_info.map(item => (item["build_time"]))
                        if( this.formData.pkg_name.length === 0 || this.formData.pkg_name.split(" ").join("").length === 0 ) {
                            this.data2 = []
                        } else {
                              if( response.resp.pkg_infos.length > 1 ){
                                 this.data2 = []
                              } else if( response.resp.pkg_infos.length === 1 && response.resp.pkg_infos[0]['history_build_times'].length != 0 ) {
                                 this.data2 = response.resp.pkg_infos[0]['history_build_times']
                                 this.queryIf = true
                                 this.pieVisible = false
                              } else {
                                 this.data2 = [] 
                              }
                        }
                        console.log(this.data2);
                    } else {
                        this.loading = false
                        this.$message.error(response.message + '\n' + response.tip);
                    }
                })
                .catch(response => {
                    this.loading = false
                    this.$message.error(response.message + '\n' + response.tip);
                })
            // this.xAxisData1 = iso_info.map(item => (item["date"]))
            // this.xAxisData2 = iso_info.filter((item) => {
            //     if(item['build_time'] !== 0){
            //        return item
            //     }
            // }).map((item) => (item['date'])).slice(-5)
        },
        querySearchPkg(queryString, cb) {
          if(queryString.length === 0 || queryString.split(" ").join("").length === 0) {
               let results = []
               cb(results)
            } else {
               getObsSuggests(queryString)
              .then(response => {
                    if(response.code === '200') {
                        let dataList = []
                        for(let i = 0; i < response.resp.length; i++) {
                            dataList.push({ value: response.resp[i] })
                        }
                        let results = queryString ? dataList : [];
                        cb(results)
                    } else {
                        this.$message.error(response.message + '\n' + response.tip);
                    }
                })
                .catch(response => {
                    this.$message.error(response.message + '\n' + response.tip);
                });
            }
        },
        querySearchBrh(queryString, cb){
            if(queryString.length === 0 || queryString.split(" ").join("").length === 0) {
               let results = []
               cb(results)
            } else {
               getBranchSuggests(queryString)
              .then(response => {
                    if(response.code === '200') {
                        let dataList = []
                        for(let i = 0; i < response.resp.length; i++) {
                            dataList.push({ value: response.resp[i] })
                        }
                        let results = queryString ? dataList : [];
                        cb(results)
                    } else {
                        this.$message.error(response.message + '\n' + response.tip);
                    }
                })
                .catch(response => {
                    this.$message.error(response.message + '\n' + response.tip);
                });
            }
        },
        initData() {
            this.getTablePage()
        },
        closelineChart() {
            this.data2 = []
            this.queryIf = false
            this.pieVisible = false
        },
        changeStatic(val) {
            if (val) {
               this.showFlag = true
            } else {
               this.showFlag = false
            } 
        },
        excelDownload() {
            this.loading = true;
            let listRes = {
                pkg_name: this.formData.pkg_name,
                gitee_branch: this.formData.gitee_branch,
                architecture: this.formData.architecture,
                build_state: this.formData.build_state,
                sig_name: this.formData.sig_name
            };
            this.getObsInfoDown(listRes);
        },
        getObsInfoDown(require) {
            getObsDown (require)
                .then(response => {
                    this.loading = false;
                    let blob = response;
                    let objectUrl = URL.createObjectURL(blob);
                    this.$refs.srcDown.href = objectUrl;
                })
                .catch(response => {
                    this.loading = false;
                    this.$message.error(response.message + '\n' + response.tip);
                });
        },
    }
}
</script>

<style lang="less">
.package-info .el-form-item:nth-child(2) {
    margin-left: 8px!important;
}
.package-info .el-button+.el-button {
    margin-left: 20px;
}
.column-button .el-checkbox-button__inner,
.column-button .el-checkbox-button:first-child .el-checkbox-button__inner,
.column-button .el-checkbox-button:last-child .el-checkbox-button__inner {
    border: 1px solid;
    padding: 8px 20px;
    color: #000;
    box-shadow: 0px 4px 20px 0px rgba(0, 0, 0, 0.1);
    border-radius: 16px;
    border: 1px solid rgba(0, 0, 0, 0.1);
}
.column-button .el-dialog__body {
    text-align: center;
}
.column-button .el-checkbox-button {
    display: inline-block;
    margin: 30px 20px 0;
}
.package-container label {
    font-size: 18px;
    font-family: Roboto-Regular,Roboto;
    font-weight: 400;
    color: #000;
    line-height: 40px;
}
.package-container .el-input__inner {
    line-height: 40px;
    border: 1px solid rgba(0, 0, 0, 0.5);
}
.package-container .el-input__inner:hover {
    border: 1px solid #002FA7;
}
.package-container .el-select:hover .el-input__inner {
    border: 1px solid #002FA7;
}
.package-container .el-table th, .has-gutter tr {
    background: rgba(0, 0, 0, 0.05);
}
.package-container .has-gutter th>.cell {
    color: #000;
    font-size: 16px;
    font-family: Roboto-Regular,Roboto;
    font-weight: 400;
    word-break: normal;
}
.package-container .el-table .cell {
    font-size: 14px;
    font-family: Roboto-Light,Roboto;
    font-weight: 300;
    color: rgba(0,0,0,0.85);
}
.package-container .el-table td {
    border: none;
}
.package-container .el-checkbox-button.is-checked .el-checkbox-button__inner {
    background-color: #fff;
    box-shadow: 0px 4px 20px 0px rgba(0, 0, 0, 0.1);
    border: 1px solid #002FA7;
    color: #000;
}
.package-info .el-button--primary {
    background-color: #002FA7;
    border-color: #002FA7;
}
.package-info .el-button--primary.is-active, .el-button--primary:active {
    color: #fff;
    background: #002FA7;
    border-radius: 4px;
}
.package-info .el-button--primary:focus, .el-button--primary:hover {
    background: #002FA7;
}
@media screen and (max-width: 1000px) {
    .package-info .el-form--inline .el-form-item__label {
        display: none;
    }
}
</style>
<style scoped>
.el-tooltip__popper{
    max-width:20%;
}
.el-tooltip__popper,.el-tooltip__popper.is-dark{
  background:rgb(48, 65, 86) !important;
  color: #fff !important;
  line-height: 24px;
}
.text-hidden{

overflow:hidden;

text-overflow:ellipsis;

white-space:nowrap;

}
.isomsg{
    float: left;
    margin-left: 418px;
    font-family: "Hiragino Sans GB"!important;
    font-size: 20px;
}
.el-table__body-wrapper::-webkit-scrollbar {
    width: 8px; /*滚动条宽度*/
    height: 8px; /*滚动条高度*/
}
.el-table__body-wrapper::-webkit-scrollbar-track {
   border-radius: 10px; /*滚动条的背景区域的圆角*/
   -webkit-box-shadow: inset 0 0 6px rgba(238,238,238, 0.3);
   box-shadow: inset 0 0 6px rgba(238,238,238, 0.3);
   background-color: #eeeeee; /*滚动条的背景颜色*/
}
.el-table__body-wrapper::-webkit-scrollbar-thumb {
  border-radius: 10px; /*滚动条的圆角*/
  -webkit-box-shadow: inset 0 0 6px rgba(145, 143, 0143, 0.3);
  box-shadow: inset 0 0 6px rgba(145, 143, 0143, 0.3);
  background-color: rgb(145, 143, 143); /*滚动条的背景颜色*/
}
.dropdownbutton{
    width:40px!important;
    height:25px;
}
.dropdownbutton span{
    font-size: 14px;
    position: relative;
    left: -14px;
    top: -6px;
}
.el-dropdown-buttom{
    display: flex;
    height: 30px;
    justify-content: space-around;
}
.el-dropdown-link{
    cursor: pointer;
    font-size: 18px;
    font-family: Roboto-Regular, Roboto;
    font-weight: 400;
    color: #000;
    line-height: 40px;
}
.listinfo{
    display: flex;
    width: 420px;
    height: 40px;
    justify-content: space-around;
    align-items: center;
}
.map-container {
    display: flex;
    flex-wrap: wrap;
    width: 1800px;
    height: 1000px;
    margin-bottom: 50px;
}
.map-left {
    width: 800px;
    height: 500px;
}
.map-right {
    width: 1000px;
    height: 500px;
} 
.form-inputs{
    display: flex!important;
    justify-content: space-between!important;
    width: 1033px;
}
h1 {
    font-size: 36px;
    font-family: HuaweiSans-Medium;
    margin: 60px 0;
}
.export-default-explain{
    position: relative;
    left: 1px;
    top: -29px;
}
.tool-tips {
    position: absolute;
    left: -9px;
    top: 12px;
}
.pc-search, .pc-select {
    left: 19px;
    display: block;
}
.form-btns {
    display: inline-block;
    text-align: right;
}
.form-button {
    display: inline-block;
    text-decoration: none;
    color: #000;
    height: 40px;
    line-height: 40px;
    border-radius:4px;
    border: 1px solid rgba(0, 0, 0, 0.5);
    padding: 0 20px;
    margin-right: 20px;
    cursor: pointer;
}
.form-button img {
    width: 19px;
    height: 15px;
    vertical-align: middle;
}
.el-table .cell a {
    color: #002FA7;
    cursor: pointer;
    text-decoration: none;
}
.safety-bulletin-pagination {
    display: block;
    margin: 60px 0 60px 0;
}
.mobile-safety-bulletin-pagination {
    display: none;
}
.package-info form {
    display: flex;
    justify-content: space-between;
}
.pc-search,
.pc-select {
    display: block;
}
.mobile-search,
.mobile-select {
    display: none;
}
.pc-pkg-table {
    width: 100%;
    display: block;
}
.mobile-pkg-table {
    display: none;
}
.icon-search {
    cursor: pointer;
}
@media screen and (max-width: 1000px) {
    .pc-select,
    .pc-search {
        display: none;
    }
    .mobile-select,
    .mobile-search {
        display: block;
        width: 315px;
    }
    .form-btns {
        display: none;
    }
    .safety-bulletin-pagination {
        display: none;
    }
    .pc-pkg-table {
        display: none;
    }
    .mobile-pkg-table {
        display: block;
    }
    .package-info .el-form-item:nth-child(2) {
        margin:0 0 40px;
    }
    .mobile-pkg-table:nth-child(even) {
        background: rgba(0, 0, 0, 0.05);
    }
    .mobile-pkg-table {
        padding: 20px;
    }
    .mobile-pkg-table:last-child {
        padding-bottom: 0;
    }
    .pkg-line li {
        display: inline;
        font-size: 12px;
        line-height: 16px;
    }
    .pkg-line {
        margin-bottom: 10px;
    }
    .pkg-line li:first-child {
        font-family: Roboto-Regular;
        font-weight: 400;
    }
    .pkg-line li:last-child {
        font-family: Roboto-Light;
        font-weight: 300;
        color: rgba(0, 0, 0, 0.5);
    }
    .mobile-pkg-table .pkg-line .detail-notice {
        color: #002FA7;
    }
}
</style>