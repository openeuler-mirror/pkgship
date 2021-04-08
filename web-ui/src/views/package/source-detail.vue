<template>
    <div class="package-detail" v-loading.fullscreen="loading">
        <h1>{{ detailData.src_name }}</h1>
        <div class="pkg-info">
            <ul class="pkg-line">
                <li class="detail-title">Version：</li>
                <li>{{ detailData.version }}</li>
            </ul>
            <ul class="pkg-line">
                <li class="detail-title">URL：</li>
                <li>{{ detailData.url }}</li>
            </ul>
            <ul class="pkg-line">
                <li class="detail-title">License：</li>
                <li>{{ detailData.license }}</li>
            </ul>
            <ul class="pkg-line">
                <li class="detail-title">Summary：</li>
                <li>{{ detailData.summary }}</li>
            </ul>
            <ul class="pkg-line">
                <li class="detail-title">Description：</li>
                <li>{{ detailData.description }}</li>
            </ul>
            <ul class="pkg-line">
                <li class="detail-title">Subpack：</li>
                <li class="detail-item"><span v-for="(item, index) in detailData.subpacks" :key="index">{{ item.bin_name }} </span></li>
            </ul>
            <ul class="pkg-line">
                <li class="detail-title">Required：</li>
                <li class="detail-item"><span v-for="(item, index) in detailData.build_dep" :key="index">{{ item }} </span></li>
            </ul>
        </div>
        <div class="subpack" v-for="(tables, index) in detailData.subpacks" :key="index">
            <p class="subpack-title">{{ tables.bin_name }}</p>
            <div class="package-table">
                <div class="provided">
                    <el-table
                        :data="tables.provides"
                        stripe
                        height="500"
                        style="width: 100%">
                        <el-table-column
                            prop="component"
                            label="Provides"
                            width="180">
                        </el-table-column>
                        <el-table-column
                            prop="required_by_bin"
                            label="Install Required by"
                            width="180">
                            <template  slot-scope="scope">
                                <span v-for="(item, index) in scope.row.required_by_bin" :key="index">{{ item }}</span>
                            </template>
                        </el-table-column>
                        <el-table-column
                            prop="required_by_src"
                            label="Build Required by"
                            width="180">
                            <template  slot-scope="scope">
                                <span v-for="(item, index) in scope.row.required_by_src" :key="index">{{ item }}</span>
                            </template>
                        </el-table-column>
                    </el-table>
                </div>
                <div class="required">
                    <el-table
                        :data="tables.requires"
                        stripe
                        height="500"
                        style="width: 100%">
                        <el-table-column
                            prop="component"
                            label="Requires"
                            width="180">
                        </el-table-column>
                        <el-table-column
                            prop="provided_by"
                            label="Provided by"
                            width="180">
                            <template  slot-scope="scope">
                                <span v-for="(item, index) in scope.row.provided_by" :key="index">{{ item }}</span>
                            </template>
                        </el-table-column>
                    </el-table>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import { packageDetail } from "../../api/repo";
export default {
    name: "packageDetail",
    data() {
        return {
            detailData: {},
            subpacks: {},
            loading: true
        }
    },
    mounted() {
        this.getPackageDetail();
    },
    methods: {
        getPackageDetail () {
            packageDetail({
                pkgName: decodeURIComponent(this.$route.query.pkg_name),
                databaseName: decodeURIComponent(this.$route.query.database_name)
            })
                .then(response => {
                    if(response.code === '200') {
                        this.loading = false;
                        this.detailData = response.resp[this.$route.query.database_name][0];
                    } else {
                        this.loading = false;
                        this.$message.error(response.message + '\n' + response.tip);
                    }
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
.package-table .el-table th, .has-gutter tr {
    background: rgba(0, 0, 0, 0.05);
}
.package-table .has-gutter th>.cell {
    color: #000;
    font-size: 12px;
    font-family: Roboto-Regular,Roboto;
    font-weight: 400;
}
.package-table .el-table .cell {
    font-size: 12px;
    font-family: Roboto-Light,Roboto;
    font-weight: 300;
    color: #000;
}
.package-table .el-table td {
    border: none;
}
.package-table .el-table__body-wrapper::-webkit-scrollbar {
    width: 6px;
    background: #ebeef5;
}
.package-table .el-table__body-wrapper::-webkit-scrollbar-thumb {
    border-radius: 3px;
    background: #ccc;
}
.package-table .el-table__body-wrapper::-webkit-scrollbar-track {
    border-radius: 3px;
    background: #fff;
}
</style>
<style scoped>
h1 {
    font-size: 36px;
    font-family: HuaweiSans-Medium;
    margin: 60px 0;
}
.package-detail {
    max-width: 1200px;
    margin: 0 auto 120px;
}
.pkg-line .detail-title {
    font-size: 14px;
    font-family: Roboto-Bold,Roboto;
    font-weight: bold;
    margin-right: 20px;
    width: 105px;
}
.detail-item span {
    background: #D8D8D8;
    border-radius: 4px;
    line-height: 32px;
    margin-left: 10px;
    padding: 2px 5px;
}
.pkg-line {
    display: flex;
    justify-content: flex-start;
    margin-top: 20px;
}
.pkg-info li {
    width: 986px;
}
.subpack {
    margin-top: 60px;
}
.subpack-title {
    font-weight: 500;
    margin-bottom: 16px;
}
.package-table {
    display: flex;
}
.package-table p {
    font-size: 14px;
    font-family: Roboto-Regular;
}
.table-name {
    display: flex;
}
.subpack li {
    display: inline-block;
    float: left;
    line-height: 56px;
    font-size: 14px;
}
.provided,
.required {
    max-width: 545px;
}
.provided {
    margin-right: 60px;
}
.table-title {
    width: 50%;
}
.cell span {
    display: block;
}
@media screen and (max-width: 1000px) {
    .package-detail {
        padding: 0 30px;
        margin-bottom: 60px;
    }
    h1 {
        font-size: 18px;
        font-family: FZLTCHJW;
        margin: 40px 0;
    }
    .package-table {
        display: block;
        margin-top: 20px;
    }
    .pkg-line .detail-title {
        font-size: 12px;
        font-family: Roboto-Regular;
        font-weight: 400;
        color: #000;
        width: 300px;
        margin-right: 10px;
    }
    .pkg-info li {
        font-size: 12px;
        font-family: Roboto-Regular;
        font-weight: 400;
        color: rgba(0, 0, 0, 0.5);
    }
    .provided {
        margin: 0;
    }
    .required {
        margin-top: 20px;
    }
}
</style>