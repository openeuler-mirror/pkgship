<template>
    <div class="package-info">
        <el-form
            :inline="true"
            class="form">
            <div class="form-inputs">
                <el-form-item label="软件包:">
                    <el-input
                        v-model="formData.pkg_name"
                        class="pc-search"
                        placeholder="请输入包名"
                        @keyup.enter.native="initData()">
                        <i slot="suffix" class="icon-search" @click="initData()"></i>
                    </el-input>
                </el-form-item>
                <el-form-item label="sig组:">
                    <el-input
                        v-model="formData.sig_name"
                        class="pc-search"
                        placeholder="请输入sig组名称"
                        @keyup.enter.native="initData()">
                        <i slot="suffix" class="icon-search" @click="initData()"></i>
                    </el-input>
                </el-form-item>
                <el-form-item label="maintainer:">
                    <el-input
                        v-model="formData.maintainer_id"
                        class="pc-search"
                        placeholder="请输入maintainer名称"
                        @keyup.enter.native="initData()">
                        <i slot="suffix" class="icon-search" @click="initData()"></i>
                    </el-input>
                </el-form-item>
            </div>
            <div class="listinfo">
              <el-dropdown :hide-on-click="false" ref="messageDrop">
                <span class="el-dropdown-link">
                  展示信息<i class="el-icon-arrow-down el-icon--right"></i>
                </span>
                <el-dropdown-menu slot="dropdown">
                  <el-dropdown-item>
                      <el-checkbox label="所在分支" v-model="checked1"></el-checkbox>
                  </el-dropdown-item>
                  <el-dropdown-item>
                      <el-checkbox label="提交人" v-model="checked2"></el-checkbox>
                  </el-dropdown-item>
                  <el-dropdown-item>
                      <el-checkbox label="提交时间" v-model="checked3"></el-checkbox>
                  </el-dropdown-item>
                  <el-dropdown-item>
                      <el-checkbox label="门禁结果" v-model="checked4"></el-checkbox>
                  </el-dropdown-item>
                  <el-dropdown-item>
                      <el-checkbox label="开启时长(支持排序)" v-model="checked5"></el-checkbox>
                  </el-dropdown-item>
                  <el-dropdown-item>
                      <el-checkbox label="门禁链接" v-model="checked6"></el-checkbox>
                  </el-dropdown-item>
                  <!-- <div class="el-dropdown-buttom"> -->
                      <!-- <el-button class="dropdownbutton" type="primary" @click="dropListChange"><span>确定</span></el-button> -->
                      <!-- <el-button class="dropdownbutton" type="warning" @click="resetdrop"><span>重置</span></el-button>
                  </div> -->
                </el-dropdown-menu>
              </el-dropdown>
              <el-button type="primary" style="background-color: #002fa7;width:120px;font-size: 18px;border:none;">搜索</el-button>
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
                v-loading.fullscreen="tableLoading"
                class="pc-pkg-table"
                stripe
                style="width: 100%">
                <el-table-column
                    prop="repo_name"
                    label="仓库名称"
                    width="180">
                </el-table-column>
                <el-table-column
                    prop="pr_title"
                    label="pr标题"
                    width="300">
                </el-table-column>
                <el-table-column
                    prop="pr_build_link"
                    label="pr链接"
                    width="350">
                </el-table-column>
                <el-table-column
                    prop="pr_state"
                    label="pr状态"
                    width="180">
                </el-table-column>
                <el-table-column
                    v-if="checked1"
                    prop="gitee_branch"
                    label="分支"
                    width="180">
                </el-table-column>
                <el-table-column
                    v-if="checked2"
                    prop="submitter"
                    label="提交人"
                    width="200"
                    :show-overflow-tooltip="true">
                </el-table-column>
                <el-table-column
                    v-if="checked3"
                    prop="submit_time"
                    label="提交时间"
                    width="200">
                </el-table-column>
                <el-table-column
                    v-if="checked5"
                    prop="open_time"
                    label="开启时长(支持排序)"
                    width="200">
                </el-table-column>
                <el-table-column
                    v-if="checked4"
                    prop="access_result"
                    label="门禁结果"
                    width="200">
                </el-table-column>
                <el-table-column
                    v-if="checked6"
                    prop="access_build_link"
                    label="门禁链接"
                    width="350">
                </el-table-column>
                <el-table-column
                    prop="sig_name"
                    label="sig组"
                    width="300">
                </el-table-column>
                <el-table-column
                    prop="mainttainer"
                    label="maintainer"
                    width="400">
                    <template slot-scope="scope">
                        <span v-for="(item, index) in scope.row.mainttainer" :key="index">
                            姓名:{{item.id}}  邮箱:{{item.email}} <br/>
                        </span>
                    </template>
                </el-table-column>
                <el-table-column
                    prop="relation_issue"
                    label="关联issue"
                    width="300">
                </el-table-column>
                <el-table-column
                    prop="mentor"
                    label="相关人员"
                    width="400">
                    <template slot-scope="scope">
                        <span v-for="(item, index) in scope.row.mentor" :key="index">
                            姓名:{{item.id}}  邮箱:{{item.email}} <br/>
                        </span>
                    </template>
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
            <div class="map-left">
                <pie-chart :title="title1" :pieData="pieData1"></pie-chart>
            </div>
            <div class="map-right">
                <pie-chart :title="title2" :pieData="pieData2"></pie-chart>
            </div>
        </div>
    </div>
</template>

<script>
import { dependDown } from '../../api/depend';
import PieChart from '@/components/PieChart.vue'

//测试数据
import { pr_build_states,pr_build_times,pr_infos } from '@/mock/testData';

export default {
    name: "pr-info",
    components: {
      PieChart,
    },
    data() {
        return {
            formData: {
                pkg_name: "",
                sig_name: "",
                maintainer_id: "",
                page_index: 0,
                page_size: 100,
                tableName: '',
            },
            title1: 'Pr状态数量饼图',
            title2: 'Pr开启时间数量饼图',
            pieData1: [],
            pieData2: [],
            checked1:false,
            checked2:false, 
            checked3:false, 
            checked4:false, 
            checked5:false, 
            checked6:false,
            total: 0,
            tableData: [],
            excelUrl: "",
            tableLoading: false,
        }
    },
    mounted() {
        this.initData()
    },
    methods: {
        getTablePage () {
            // this.tableLoading = true;
            this.tableData = pr_infos
            this.pieData1 = Object.keys(pr_build_states).map(item => ({ name: item, value: pr_build_states[item] }))
            this.pieData2 = Object.keys(pr_build_times).map(item => ({ name: item, value: pr_build_times[item] }))
            console.log(this.pieData1);
        },
        initData() {
            this.getTablePage();
            // this.excelDownload();
        },
        go (pkg_name, database_name){
            this.$router.push({
                path: '/source-detail',
                query: {pkg_name, database_name}
            })
        },
        excelDownload() {
            this.loading = true;
            let priority = [];
            priority.push(this.formData.tableName);
            let listRes = {
                dependType: 'src',
                parameter: {
                    db_priority: priority
                }
            };
            this.getdependDown(listRes);
        },
        getdependDown(require) {
            dependDown (require)
                .then(response => {
                    this.loading = false;
                    let blob = new Blob([response], { type: 'application/vnd.ms-excel' })
                    let objectUrl = URL.createObjectURL(blob);
                    var oA = document.createElement("a");
                    oA.href = objectUrl;
                    oA.click();
                    this.$message({
                      message: '导出成功!',
                      type: 'success'
                    });
                })
                .catch(response => {
                    this.loading = false;
                    this.$message.error(response.message + '\n' + response.tip);
                });
        }
    }
}
</script>

<style lang="less">
.package-info .el-form-item:nth-child(2) {
    margin-left: 50px;
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
.map-container {
    display: flex;
    flex-wrap: wrap;
    width: 1800px;
    height: 500px;
    margin-bottom: 50px;
}
.map-left {
    width: 900px;
    height: 500px;
}
.map-right {
    width: 900px;
    height: 500px;
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
    margin: 60px 0 200px 0;
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
    .mobile-safety-bulletin-pagination {
        display: block;
        margin: 40px 0 90px;
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