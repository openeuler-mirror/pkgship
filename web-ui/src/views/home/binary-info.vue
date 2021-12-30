<template>
    <div class="package-info">
        <el-form
            :inline="true"
            class="form">
            <div class="form-inputs">
                <el-form-item label="Product Version">
                    <el-tooltip class="tool-tips" content="Repository to be searched" placement="bottom" effect="light">
                        <img src="@/assets/images/question.svg" alt="">
                    </el-tooltip>
                    <el-select class="pc-select" v-model="formData.tableName" @change="initData(1)">
                        <el-option v-for="(item, index) in productV" :key="index"
                                   :label="item"
                                   :value="item">
                        </el-option>
                    </el-select>
                    <el-select class="mobile-select" v-model="formData.tableName" @change="initData(1)" placeholder="Product Version">
                        <el-option v-for="(item, index) in productV" :key="index"
                                   :label="item"
                                   :value="item">
                        </el-option>
                    </el-select>
                </el-form-item>
                <el-form-item label="Search">
                    <el-tooltip class="tool-tips" content="Name of the binary package to be queried.Currently,only exact match is supported" placement="bottom" effect="light">
                        <img src="@/assets/images/question.svg" alt="">
                    </el-tooltip>
                    <el-input
                        v-model="formData.queryPkgName"
                        class="pc-search"
                        placeholder="Search Name"
                        @keyup.enter.native="initData(1)">
                        <i slot="suffix" class="icon-search" @click="initData(1)"></i>
                    </el-input>
                    <el-input
                        v-model="formData.queryPkgName"
                        class="mobile-search"
                        placeholder="Search Name">
                        <i slot="suffix" class="icon-search" @click="initData(1)"></i>
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
                    prop="pkg_name"
                    label="Name"
                    width="180">
                    <template slot-scope="scope" >
                        <a @click="go(scope.row.pkg_name, formData.tableName)">{{ scope.row.pkg_name }}</a>
                    </template>
                </el-table-column>
                <el-table-column
                    prop="version"
                    label="Version"
                    width="180">
                </el-table-column>
                <el-table-column
                    prop="url"
                    label="URL">
                    <template slot-scope="scope">
                        <a :href=scope.row.url >{{ scope.row.url }}</a>
                    </template>
                </el-table-column>
                <el-table-column
                    prop="license"
                    label="License">
                </el-table-column>
                <el-table-column
                    prop="source_name"
                    label="src-package">
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
                <ul class="pkg-line">
                    <li class="detail-title">src-package</li>
                    <li>{{ item.source_name }}</li>
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
import {
    packageBin
} from "../../api/issue";
import {
    dbPriority,
} from "../../api/repo";
import { dependDown } from '../../api/depend';
export default {
    name: "issue-list",
    data() {
        return {
            formData: {
                pageNum: 1,
                pageSize: 10,
                queryPkgName: "",
                tableName: '',
            },
            productV: [],
            tableData: [],
            total: 0,
            excelUrl: '',
            tableLoading: false
        }
    },
    mounted() {
        this.getDbPriority();
    },
    methods: {
        getTablePage (flag) {
            this.tableLoading = true;
            this.formData.pageNum = flag;
            this.getPkgBin(this.formData);
        },
        initData(flag) {
            this.getTablePage(flag);
            this.excelDownload();
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
        getPkgBin(require) {
            packageBin(require)
                .then(response => {
                    this.tableLoading = false;
                    if(response.code === '200') {
                        this.tableData = response.resp;
                        this.total = response.total_count;
                    } else {
                        this.$message.error(response.message + '\n' + response.tip);
                    }
                })
                .catch(response => {
                    this.tableLoading = false;
                    this.$message.error(response.message + '\n' + response.tip);
                });
        },
        getDbPriority() {
            dbPriority()
                .then(response => {
                    this.tableLoading = false;
                    if(response.code === '200') {
                        this.productV = response.resp;
                        this.formData.tableName = response.resp[0];
                        this.initData(1);
                    } else {
                        this.$message.error(response.message + '\n' + response.tip);
                    }
                })
                .catch(response => {
                    this.tableLoading = false;
                    this.$message.error(response.message + '\n' + response.tip);
                });
        },
        getdependDown(require) {
            dependDown (require)
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
        go (pkg_name, database_name){
            this.$router.push({
                path: '/binary-detail',
                query: {pkg_name, database_name}
            })
        },
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
