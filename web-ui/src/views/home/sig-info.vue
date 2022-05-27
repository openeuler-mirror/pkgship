<template>
    <div class="package-info">
        <el-form
            :inline="true"
            class="form">
            <div class="form-inputs">
                <el-form-item label="Sig组:">
                    <el-tooltip class="tool-tips" content="Name of the source code package to be queried.Currently,only exact match is supported" placement="bottom" effect="light">
                        <img src="@/assets/images/question.svg" alt="">
                    </el-tooltip>
                    <el-autocomplete
                        v-model="formData.sig_name"
                        class="pc-search"
                        placeholder="请输入sig组名称"
                        :fetch-suggestions="querySearchSig"
                        @keyup.enter.native="initData()"
                        @select="initData()">
                        <i slot="suffix" class="icon-search" @click="initData()"></i>
                    </el-autocomplete>
                    <el-input
                        v-model="formData.sig_name"
                        class="mobile-search"
                        placeholder="Search Name">
                        <i slot="suffix" class="icon-search" @click="initData()"></i>
                    </el-input>
                </el-form-item>
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
                    prop="name"
                    label="sig名称"
                    width="250">
                    <template slot-scope="scope">
                        <a :href="'https://gitee.com/openeuler/community/tree/master/sig/' + scope.row.name">{{ scope.row.name }}</a>
                    </template>
                </el-table-column>
                <el-table-column
                    prop="description"
                    label="描述"
                    width="1000"
                    :show-overflow-tooltip='true'>
                </el-table-column>
                <!-- <el-table-column
                    prop="mentors"
                    label="维护者"
                    width="400"
                    :show-overflow-tooltip='true'>
                    <template slot-scope="scope">
                        <span v-if="scope.row.mentors === undefined || scope.row.mentors.length <= 0 || scope.row.mentors[0].email === null || scope.row.mentors[0].id === null">暂无信息</span>
                        <div v-if="scope.row.mentors != undefined && scope.row.mentors.length > 0 && scope.row.mentors[0].email != null && scope.row.mentors[0].id != null">
                            <span v-for="(item, index) in scope.row.mentors" :key="index">id:{{item.id}} | 邮箱:<a @click="goEmail">{{item.email}}</a></span>
                        </div>
                    </template>
                </el-table-column> -->
                <el-table-column
                    prop="maintainer"
                    label="维护人"
                    width="400"
                    :show-overflow-tooltip="true">
                    <template slot-scope="scope">
                        <span v-if="scope.row.maintainer === undefined || scope.row.maintainer.length <= 0 || scope.row.maintainer[0].id === null">暂无信息</span>
                        <span v-for="(item, index) in scope.row.maintainer" :key="index">
                            <span v-if="scope.row.maintainer != undefined && scope.row.maintainer.length > 0 && scope.row.maintainer[0].id != null && index === 0">
                                id:{{item.id}} | 邮箱:<a @click="goEmail(item.email)">{{item.email}}</a>
                            </span>
                        </span>
                        <el-popover
                                  placement="right"
                                  width="400"
                                  trigger="hover">
                                  <ul v-for="(item, index) in scope.row.maintainer" :key="index">
                                      <li>id:{{item.id}} | 邮箱:<a @mouseover="putIn(index)" @mouseleave="putOut" :class="popActive === index? 'blue underline' : ''" @click="goEmail(item.email)" style="cursor: pointer;">{{item.email}}</a></li>
                                  </ul>
                                  <i slot="reference" @mouseover="mouseIn(scope.$index)" @mouseleave="mouseOut" :class="active === scope.$index? 'el-icon-more-outline blue' : 'el-icon-more-outline'" style="margin-left: 20px;cursor: pointer;"></i>
                        </el-popover>
                    </template>
                </el-table-column>
                <el-table-column
                    prop="repositories"
                    label="所属软件包"
                    :show-overflow-tooltip='true'>
                    <template slot-scope="scope" >
                        <img
                        src="../../../public/gather.png"
                        class="software-logo"
                        @click="jump(scope.row.name)"
                        />
                    </template>
                </el-table-column>
            </el-table>
            <div class="mobile-pkg-table" v-for="(item, index) in tableData" :key="index">
                <ul class="pkg-line">
                    <li class="detail-title">Name：</li>
                    <li class="detail-notice"><a @click="go(item.name, formData.tableName)">{{ item.name }}</a></li>
                </ul>
                <ul class="pkg-line">
                    <li class="detail-title">Version：</li>
                    <li>{{ item.version }}</li>
                </ul>
                <ul class="pkg-line">
                    <li class="detail-title">Release：</li>
                    <li>{{ item.release }}</li>
                </ul>
                <ul class="pkg-line">
                    <li class="detail-title">URL：</li>
                    <li>{{ item.url }}</li>
                </ul>
                <ul class="pkg-line">
                    <li class="detail-title">License：</li>
                    <li>{{ item.rpm_license }}</li>
                </ul>
            </div>
        </template>
        <el-pagination
            class="safety-bulletin-pagination"
            :current-page.sync="formData.pageNum"
            :page-size="formData.pageSize"
            layout="total, prev, pager, next, jumper"
            @current-change="initData"
            :total="total">
        </el-pagination>
        <el-pagination
            class="mobile-safety-bulletin-pagination"
            :current-page.sync="formData.pageNum"
            :page-size="formData.pageSize"
            layout="prev, pager, next"
            @current-change="initData"
            :total="total">
        </el-pagination>
    </div>
</template>

<script>
import { getSigInfo } from '../../api/sig'
import { getSigDown } from '../../api/sig'
import { getSigSuggests } from '../../api/sig'

//测试数据
// import { sig_infos } from '@/mock/testData'

export default {
    name: "sig-info",
    props:{
        sigName: {
         type: String,
         default: undefined
       },
    },
    data() {
        return {
            popActive: false,
            active: false,
            formData: {
                sig_name: "",
                pageNum: 1,
                pageSize: 10,
                tableName: '',
            },
            pkgName: "",
            total: 0,
            tableData: [],
            excelUrl: "",
            tableLoading: false,
        }
    },
    created() {
        this.formData.sig_name = this.sigName
    },
    mounted() {
        this.initData();
    },
    methods: {
        getTablePage () {
            this.tableLoading = true
            getSigInfo(this.formData.sig_name)
                .then(response => {
                    if(response.code === '200') {
                        // this.tableData = response.resp;
                        this.tableLoading = false
                        var dataLength = response.resp.length
                        this.total = dataLength
                        var PageMax = Math.ceil(dataLength/this.formData.pageSize)
                        if ( this.formData.pageNum != PageMax ) {
                          this.tableData = response.resp.slice(((this.formData.pageNum - 1) * this.formData.pageSize), ((this.formData.pageNum - 1) * this.formData.pageSize) + this.formData.pageSize)
                        } else {
                          this.tableData = response.resp.slice(this.formData.pageSize * (PageMax - 1), dataLength)
                        }
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
                console.log(this.tableData);
            // this.tableData = sig_infos
        },
        querySearchSig(queryString, cb) {
          if(queryString.length === 0 || queryString.split(" ").join("").length === 0) {
               let results = []
               cb(results)
            } else {
               getSigSuggests(queryString)
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
            // this.excelDownload();
        },
        go (pkg_name, database_name){
            this.$router.push({
                path: '/source-detail',
                query: {pkg_name, database_name}
            })
        },
        jump(sig_name){
            this.$router.push({
                path: '/sig-detail',
                query: {sig_name}
            })
        },
        goEmail(msg) {
            // window.open("mailto:huangtainhua@huawei.com?subject=lala&body=hahah");
            window.open("mailto:" + msg + "?subject=测试邮件&body=内容");
        },
        mouseIn(index){
            this.active = index
        },
        mouseOut(){
            this.active = false
        },
        putIn(index){
            this.popActive = index
        },
        putOut(){
            this.popActive = false
        },
        excelDownload() {
            this.loading = true;
            let listRes = {
                sig_name: this.formData.sig_name
            };
            this.getSigInfoDown(listRes);
        },
        getSigInfoDown(require) {
            getSigDown (require)
                .then(response => {
                    this.loading = false;
                    let blob = response;
                    let objectUrl = URL.createObjectURL(blob);
                    // this.$refs.srcDown.href = objectUrl;
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
    },
    beforeDestroy() {
        this.sigName = ''
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
.text-hidden{

overflow:hidden;

text-overflow:ellipsis;

white-space:nowrap;

}
h1 {
    font-size: 36px;
    font-family: HuaweiSans-Medium;
    margin: 60px 0;
}
.blue{
    color:#002FA7;
}
.underline{
    text-decoration:underline;
}
.software-logo {
    cursor: pointer;
    width: 15px;
    height: 15px;
    margin-left: 33px;
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