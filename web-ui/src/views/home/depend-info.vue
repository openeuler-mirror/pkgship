<template>
    <div class="depend" v-loading="loading">
        <div class="depend-type">
            <span class="h5-type">Type</span>
            <div class="type-btns">
                <el-tooltip content="Query the installation dependencies of the binary package" placement="top" effect="light">
                   <button :class="{'active': currentButton === 'Install'}" @click="clickButton($event)">Install Depend</button>
                </el-tooltip>
                <el-tooltip content="Query the build dependencies of the source code package" placement="top" effect="light">
                   <button :class="{'active': currentButton === 'Build'}" @click="clickButton($event)">Build Depend</button>
                </el-tooltip>
                <el-tooltip content="Query all dependencies of the binary package or source code package,including the installation and build dependencies" placement="top" effect="light">
                   <button :class="{'active': currentButton === 'Self'}" @click="clickButton($event)">Self Depend</button>
                </el-tooltip>
                <el-tooltip content="Query dependents of the binary package or source code package" placement="top" effect="light">
                   <button :class="{'active': currentButton === 'Bedepend'}" @click="clickButton($event)">Bedepend</button>
                </el-tooltip>
            </div>
            <div class="self-checkBox" :class="{'show': currentButton === 'Self'}">
                <template>
                    <el-checkbox-group v-model="checkList">
                        <el-checkbox label="source" @change="sourceChange"></el-checkbox>
                        <el-tooltip class="checked-explain" effect="light" :content="sourceMsg" placement="top">
                           <img src="@/assets/images/question.svg" alt="">
                        </el-tooltip>
                        <el-checkbox label="Self-build" @change="selfChange"></el-checkbox>
                        <el-tooltip class="checked-explain" effect="light" 
                        :content="selfMsg" 
                        placement="top">
                           <img src="@/assets/images/question.svg" alt="">
                        </el-tooltip>
                        <el-checkbox label="with-subpack" @change="withChange"></el-checkbox>
                        <el-tooltip style="position: relative;top: 2px;left: 3px;" effect="light" 
                        :content="withMsg" 
                        placement="top">
                           <img src="@/assets/images/question.svg" alt="">
                        </el-tooltip>
                    </el-checkbox-group>
                </template>
            </div>
            <div class="be-select" :class="{'show': currentButton === 'Bedepend'}">
                <template>
                    <el-select class="type-select" v-model="typeName" clearable>
                        <el-option v-for="(item, index) in productV" :key="index"
                                   :label="item"
                                   :value="item">
                        </el-option>
                    </el-select>
                    <el-tooltip style="position: relative;top: 3px;left: 3px;" effect="light" 
                        content="Repository to be searched.Only one repository can be selected" 
                        placement="top">
                           <img src="@/assets/images/question.svg" alt="">
                    </el-tooltip>
                    <el-checkbox-group v-model="typeList" class="type-radio">
                        <el-checkbox label="with-subpack" @change="subChange"></el-checkbox>
                        <el-tooltip style="position: relative;top: 3px;left: 3px;" effect="light" 
                        :content="subMsg" 
                        placement="top">
                           <img src="@/assets/images/question.svg" alt="">
                        </el-tooltip>
                    </el-checkbox-group>
                </template>
            </div>
            <div class="be-select" :class="{'show': currentButton === 'Install' || currentButton === 'Build'}">
                <template>
                    <span>Level: </span>
                    <el-tooltip class="item" effect="light" content="Depth of the dependencies to be searched.All indicates that all dependencies are queried" placement="top">
                        <img src="@/assets/images/question.svg" alt="">
                    </el-tooltip>
                    <el-select class="type-select" v-model="typeLevel">
                        <el-option v-for="(item, index) in levelList" :key="index"
                                   :label="item"
                                   :value="item">
                        </el-option>
                    </el-select>
                </template>
            </div>
        </div>
        <div class="depend-search">
            <el-form
                :inline="true"
                class="form">
                <el-form-item label="Search" class="searching">
                    <el-tooltip class="tool-tips" content="The package name is case-sensitive" placement="bottom" effect="light">
                        <el-button><img src="@/assets/images/question.svg" alt=""></el-button>
                    </el-tooltip>
                    <el-input
                        v-model="searchName"
                        class="pc-search"
                        @keyup.enter.native="searchEvent"
                        :placeholder="searchTitle">
                        <i slot="suffix" class="icon-search" @click="initData"></i>
                    </el-input>
                </el-form-item>
                <el-form-item class="mobile-search">
                    <el-input
                        v-model="searchName"
                        class="mobile-search"
                        placeholder="Search">
                        <i slot="suffix" class="icon-search"  @click="initData"></i>
                    </el-input>
                </el-form-item>
            </el-form>
            <div class="be-select source" :class="{'show': currentButton === 'Bedepend'}">
                <template>
                    <el-select class="type-select" v-model="searchType" clearable>
                        <el-option v-for="(item, index) in searchBe" :key="index"
                                   :label="item"
                                   :value="item">
                        </el-option>
                    </el-select>
                    <el-tooltip style="position: relative;top: 3px;left: 3px;" effect="light" 
                        content="install indicates that the installation dependents of the binary package are queried,and build indicates that the build dependents of the source code package are quired" 
                        placement="top">
                           <img src="@/assets/images/question.svg" alt="">
                    </el-tooltip>
                    <el-checkbox-group v-model="searchSource" class="type-radio">
                        <el-checkbox label="source" @change="sourceChange2"></el-checkbox>
                        <el-tooltip style="position: relative;top: 3px;left: 3px;" effect="light" 
                        :content="sourceMsg2" 
                        placement="top">
                           <img src="@/assets/images/question.svg" alt="">
                        </el-tooltip>
                    </el-checkbox-group>
                </template>
            </div>
        </div>
        <div class="click-transfer" v-if="currentButton !== 'Bedepend'">
            <p>
                Search Priority:
                <span ref="transTitle"></span>
                ,
                <el-button class="click-btn" type="text" @click="dialogVisible = true">click here</el-button>
                to change.
            </p>
            <el-tooltip class="bottom-explain" effect="light" content="Repository to be searched" placement="top">
                        <img src="@/assets/images/question.svg" alt="">
            </el-tooltip>
            <el-dialog
                title="Set Search Priority"
                :visible.sync="dialogVisible"
                width="60%"
                center>
                <template>
                  <el-scrollbar>
                    <el-transfer
                        :data="washTableData(transData)"
                        :props="{key: 'id',label: 'fileName'}"
                        :titles="['Select from Here', 'Set in Here']"
                        :render-content="renderFunc"
                        class="transfer-box"
                        target-order="push"
                        v-model="selectedData"
                        :right-default-checked="defaultVersion"
                    ></el-transfer>
                  </el-scrollbar>
                </template>
                <span slot="footer" class="dialog-footer">
                    <el-button type="primary" @click="transSelect">OK</el-button>
                    <el-button @click="dialogVisible = false">Clear</el-button>
                </span>
            </el-dialog>
        </div>
        <div class="depend-info" v-if="isShowTable">
            <div class="excel-button">
                <el-form
                    :inline="true"
                    class="form">
                    <a class="form-button" @click="excelDownload" ref="download">
                        <img src="@/assets/images/dowmload.svg" alt="">
                        Export Excel
                    </a>
                </el-form>
            </div>
            <div class="package-table">
                <div class="pkg-tables">
                    <div class="table-content binary">
                        <h4>Binary Package List</h4>
                        <ul class="table-title binary">
                            <li>
                                <a>Binary Name
                                    <img class="filter" src="@/assets/images/depend/filterSearch.svg" @click="clickFilter('binary')">
                                </a>
                                <div class="table-select" v-if="isShowBinary">
                                    <el-row class="table-autocomplete">
                                        <el-col>
                                            <el-autocomplete
                                                class="inline-input"
                                                v-model="stateBinary"
                                                :fetch-suggestions="querySearchBinary"
                                                placeholder="Search"
                                                :trigger-on-focus="false"
                                                @select="handleSelectBinary"
                                            ></el-autocomplete>
                                        </el-col>
                                    </el-row>
                                </div>
                            </li>
                            <li>Source Name</li>
                            <li>Version</li>
                            <li>Database</li>
                        </ul>
                        <el-scrollbar class="scrollbar">
                            <ul class="table-item binary" v-for="(item, index) in binaryList" :key="index">
                                <li class="table-name" :title="item.binary_name"><a @click="drawNodeGraph(item.binary_name, 'binary')">{{ item.binary_name }}</a></li>
                                <li class="table-name" :title="item.source_name">{{ item.source_name }}</li>
                                <li>{{ item.version }}</li>
                                <li>{{ item.database }}</li>
                            </ul>
                        </el-scrollbar>
                    </div>
                    <div class="table-content source">
                        <h4>Source Package List</h4>
                        <ul class="table-title source">
                            <li>
                                <a>Source Name
                                    <img class="filter" src="@/assets/images/depend/filterSearch.svg" @click="clickFilter('source')"></a>
                                <div class="table-select"  v-if="isShowSource">
                                    <el-row class="table-autocomplete">
                                        <el-col>
                                            <el-autocomplete
                                                class="inline-input"
                                                v-model="stateSource"
                                                :fetch-suggestions="querySearchSource"
                                                placeholder="Search"
                                                :trigger-on-focus="false"
                                                @select="handleSelectSource"
                                            ></el-autocomplete>
                                        </el-col>
                                    </el-row>
                                </div>
                            </li>
                            <li>Version</li>
                            <li>Database</li>
                        </ul>
                        <el-scrollbar class="scrollbar">
                            <ul class="table-item source" v-for="(item, index) in sourceList" :key="index">
                                <li class="table-name" :title="item.source_name">
                                    <a @click="drawNodeGraph(item.source_name, 'source')">{{ item.source_name }}</a>
                                </li>
                                <li>{{ item.version }}</li>
                                <li>{{ item.database }}</li>
                            </ul>
                        </el-scrollbar>
                    </div>
                    <div class="table-content statis">
                        <h4>Statistics</h4>
                        <ul class="statis">
                            <li>database</li>
                            <li>binarySum</li>
                            <li>sourceSum</li>
                        </ul>
                        <ul class="statis" v-for="(item, index) in statistics" :key="index">
                            <div v-if="item.sum">
                                <li>{{ item.sum }}</li>
                                <li>{{ item.binarys_sum }}</li>
                                <li>{{ item.sources_sum }}</li>
                            </div>
                            <div v-else>
                                <li>{{ item.database }}</li>
                                <li>{{ item.binary_sum }}</li>
                                <li>{{ item.source_sum }}</li>
                            </div>
                        </ul>
                    </div>
                </div>
                <div class="pkg-diagram" id="main" ref="diagram"></div>
            </div>
        </div>
        <div class="depend-info-h5">
            <div class="binary-table">
                <h4>Binary Package List</h4>
                <ul class="binary-h5" v-for="(item, index) in binaryList" :key="index">
                    <li>
                        <span> Binary Name: </span>
                        <a>{{ item.binary_name }}</a>
                    </li>
                    <li>
                        <span>Source Name: </span>
                        {{ item.source_name }}
                    </li>
                    <li>
                        <span>Version: </span>
                        {{ item.version }}
                    </li>
                    <li>
                        <span>Database</span>
                        {{ item.database }}
                    </li>
                </ul>
            </div>
            <div class="table-content source-h5">
                <h4>Source Package List</h4>
                <ul class="table-title source">
                    <li>Source Name</li>
                    <li>Version</li>
                    <li>Database</li>
                </ul>
                <ul class="table-item source" v-for="(item, index) in sourceList" :key="index">
                    <li><a>{{ item.source_name }}</a></li>
                    <li>{{ item.version }}</li>
                    <li>{{ item.database }}</li>
                </ul>
            </div>
            <div class="table-content statis-h5">
                <h4>Statistics</h4>
                <ul class="statis" v-for="(item, index) in statistics" :key="index">
                    <li>{{ item.database }}</li>
                    <li>{{ item.binary_sum }}</li>
                    <li>{{ item.source_sum }}</li>
                </ul>
            </div>
        </div>
    </div>
</template>

<script>
import {
    dependList,
    dependDown,
    dependGraph
} from '../../api/depend';
import {
    dbPriority,
} from "../../api/repo";
export default {
    name: "depend-info",
    data () {
        return {
            formData: {
                queryPkgName: [],
                dependType: "installdep",
            },
            parameter: {
                db_priority: [],
                level: 'ALL',
                search_type: ''
            },
            msgFlag: true,
            subFlag: false,
            sourceMsg: 'If this option is selected,the dependencies of the source code package are queried',
            selfMsg: 'For the source code package:Query all build dependencies and the first level installation dependencies of each dependency package',
            withMsg: 'If this option is not selected,the dependencies of the binary package are queried',
            sourceMsg2: 'If this option is not selected,the dependents of the binary package are queried',
            subMsg: 'For the binary package:Query the dependents of the binary package,the associated source code package,and other binary packages generated by the source code package',
            searchName: "",
            searchTitle: 'Please enter a binary package name',
            currentButton: 'Install',
            isShowBinary: false,
            isShowSource: false,
            isShowTable: false,
            checkList: ['source'],
            typeName: "",
            typeLevel: 'ALL',
            levelList: ['ALL', 1, 2, 3, 4, 5, 6 , 7, 8, 9, 10],
            searchType: '',
            searchBe: ['install', 'build'],
            searchSource: false,
            typeList: true,
            isAll: true,
            transData: [],
            selectedData: [],
            tableName: [],
            dialogVisible: false,
            loading: false,
            downloadRequire: '',
            queryNames: [],
            stateBinary: '',
            stateSource: '',
            productV: [],
            binaryList: [],
            binaryQueryList: [],
            sourceList: [],
            sourceQueryList: [],
            statistics: [],
            Ddata: null,
            defaultVersion: []
        }
    },
    mounted() {
        this.formData.queryPkgName = this.changePkgQueryName(this.searchName);
        this.getDbPriority();
    },
    methods: {
        renderFunc(h, option) {
          return <el-tooltip class="item" effect="dark" content="option.fileName" placement="top">
                   <div slot="content">{ option.fileName }</div>
                   <span>{ option.fileName }</span>
                 </el-tooltip>
        },
        sourceChange(val){
            console.log(this.checkList);
            console.log(this.checkList.length);
            if(val){
               this.msgFlag = true
               if(this.checkList.includes('Self-build')){
                  this.selfMsg = 'For the source code package:Query all build dependencies and the installation dependencies of each dependency package'
               }else{
                  this.selfMsg = 'For the source code package:Query all build dependencies and the first level installation dependencies of each dependency package'
               }
               this.sourceMsg = 'If this option is selected,the dependencies of the source code package are queried'
            }else{
               this.msgFlag = false
               if(this.checkList.includes('Self-build')){
                  this.selfMsg = 'For the binary package:Query all installation dependencies and the build dependencies of each dependency package'
               }else{
                  this.selfMsg = 'For the binary package:Query all installation dependencies and the first level build dependencies of each dependency package'
               }
               this.sourceMsg = 'If this option is not selected,the dependencies of the binary package are queried'
            }
        },
        selfChange(val){
            if(val){
                if(this.msgFlag){
                   this.selfMsg = 'For the source code package:Query all build dependencies and the installation dependencies of each dependency package'
                }else{
                   this.selfMsg = 'For the binary package:Query all installation dependencies and the build dependencies of each dependency package'
                }
            }else{
                if(this.msgFlag){
                   this.selfMsg = 'For the source code package:Query all build dependencies and the first level installation dependencies of each dependency package' 
                }else{
                   this.selfMsg = 'For the binary package:Query all installation dependencies and the first level build dependencies of each dependency package'
                }
            }
        },
        withChange(val){
            if(val){
                this.withMsg = 'Selected:Query the dependencies of the binary package,the associated source code package,and other binary packages generated by the source code package'
            }else{
                this.withMsg = 'Deselected:Query only the dependencies of the binary package and the associated source code package'
            }
        },
        sourceChange2(val){
            if(val){
                this.sourceMsg2 = 'If this option is selected,the dependents of the source code package are queried'
                if(this.searchSource){
                    this.subMsg = 'For the source code package:Query only the dependents of the source code package and the binary packages generated by the source code package'
                }else{
                    this.subMsg = 'For the source code package:Query only the dependents of the source code package'
                }
                this.subFlag = true
            }else{
                this.sourceMsg2 = 'If this option is not selected,the dependents of the binary package are queried'
                if(this.searchSource){
                    this.subMsg = 'For the binary package:Query the dependents of the binary package,and other binary packages generated by the source code package'
                }else{
                    this.subMsg = 'For the binary package:Query only the dependents of the binary package and the associated source code package'
                }
                this.subFlag = false
            }
        },
        subChange(val){
            if(val){
                if(this.subFlag){
                    this.subMsg = 'For the source code package:Query only the dependents of the source code package and the binary packages generated by the source code package'
                }else{
                    this.subMsg = 'For the binary package:Query the dependents of the binary package,and other binary packages generated by the source code package'
                }
            }else{
                if(this.subFlag){
                    this.subMsg = 'For the source code package:Query only the dependents of the source code package'
                }else{
                    this.subMsg = 'For the binary package:Query only the dependents of the binary package and the associated source code package'
                }
            }
        },
        changePkgQueryName(name) {
            let n = [];
            n.push(name);
            return n;
        },
        searchEvent(e) {
            var keyCode = e.keyCode;
            if (keyCode === 13) {
                this.initData();
            }
        },
        initData() {
            this.isAll = false;
            this.loading = true;
            this.isShowTable = false;
            this.formData.queryPkgName = this.changePkgQueryName(this.searchName);
            let current = this.currentButton.toLowerCase();
            if(current=== 'install' || current === 'build') {
                this.typeLevel === 'ALL' ? delete this.parameter.level : this.parameter.level =  Number(this.typeLevel);
            } else {
                delete this.parameter.level;
            }
            let required = this.updateParamter();
            this.getdependList(required);
        },
        updateParamter() {
            let required = {};
            required.parameter = this.parameter;
            let data = this.formData;
            let current = this.currentButton.toLowerCase();
            required.parameter.db_priority = this.tableName;
            if (current === 'self') {
                current += 'dep';
                let checked = this.checkList;
                required.parameter.self_build = false;
                if (checked.includes('Self-build')) {
                    required.parameter.self_build = true;
                }
                required.parameter.packtype = checked.includes('source') ? 'source' : 'binary';
                required.parameter.with_subpack = false;
                if (checked.includes('with-subpack')) {
                    required.parameter.with_subpack = true;
                }
                required.parameter.search_type = ''
            } else if (current !== 'bedepend') {
                current += 'dep';
                required.parameter.packtype = '';
                required.parameter.search_type = '';
                required.parameter.with_subpack = false;
            } else {
                current = 'bedep';
                required.parameter.db_priority = [];
                required.parameter.search_type = this.searchType;
                required.parameter.db_priority.push(this.typeName);
                required.parameter.with_subpack = this.typeList;
                delete required.parameter.self_build;
                required.parameter.packtype = this.searchSource ? 'source' : 'binary';
            }
            data.dependType = current;
            required.queryPkgName = data.queryPkgName;
            required.dependType = data.dependType;
            return required
        },
        toggleData(current) {
            let btnList = {
                Install: 'getInstallData',
                Self: 'getSelfData',
                Build: 'getBuildData',
                Bedepend: 'getBedependData'
            };
            let func = btnList[current];
            this[func]();
        },
        clickButton(event) {
            let text = event.currentTarget.innerHTML;
            text = text.split(' ', 1)[0];
            this.currentButton = text;
            this.typeLevel = 'ALL';
            if (text === 'Install') {
                this.searchTitle = 'Please enter a binary package name';
            }else if (text === 'Self') {
                this.searchTitle = 'Please enter a source/binary package name';
            } else {
                this.searchTitle = 'Please enter a source package name';
            }
            this.isShowTable = false;

            this.getDbPriority();
        },
        clickFilter(filter) {
            if (filter === 'binary') {
                this.isShowBinary = !this.isShowBinary;
            } else {
                this.isShowSource = !this.isShowSource;
            }
        },
        initDraw() {
            let _self = this;
            let echarts = require('echarts');
            let id = this.$refs.diagram;
            let myChart = echarts.init(id);
            let data = this.Ddata;
            let option = {
                animationDurationUpdate: 1500,
                animationEasingUpdate: 'quinticInOut',
                series : [
                    {
                        type: 'graph',
                        layout: 'none',
                        edgeSymbol: ['none', 'arrow'],
                        hoverAnimation: false,
                        data: data.nodes.map(function (node) {
                            return {
                                x: node.x,
                                y: node.y,
                                id: node.id,
                                name: node.label,
                                symbolSize: node.size,
                                edgeSymbol: ['arrow'],
                                itemStyle: {
                                    color: node.color
                                }
                            };
                        }),
                        edges: data.edges.map(function (edge) {
                            return {
                                source: edge.sourceID,
                                target: edge.targetID
                            };
                        }),
                        emphasis: {
                            label: {
                                position: 'right',
                                show: true
                            }
                        },
                        roam: true,
                        focusNodeAdjacency: true,
                        lineStyle: {
                            width: 0.5,
                            curveness: 0.3,
                            opacity: 0.7
                        },
                    }
                ],
            };
            myChart.setOption(option);
            myChart.off('click');
            myChart.on('click', function (params) {
                let current = params.data.id;
                _self.formData.node_name = current;
                _self.getGraphData(true, 'binary');
            });
        },
        drawNodeGraph(value, isSource) {
            this.formData.node_name = value;
            this.loading = true;
            this.getGraphData(true, isSource);
        },
        excelDownload() {
            this.loading = true;
            let listRes = this.formData;
            listRes.parameter = this.parameter;
            this.getdependDown(listRes);
        },
        transSelect() {
            this.dialogVisible = false;
            let keys = this.selectedData;
            let t = '';
            let tableList = [];
            keys.forEach(key => {
                t += ' ' + key + ' >';
                tableList.push(key);
            });
            t = t.slice(0, t.length - 1);
            this.$refs.transTitle.innerHTML = t;
            this.tableName = tableList;
        },
        washTableData(data) {
            let newData = [];
            let keys = Object.keys(data);
            for (let key of keys) {
                let item = {};
                item.id = data[key];
                item.fileName = data[key];
                newData.push(item);
            }
            return newData;
        },
        filterTableData(data, key, keyword) {
            data = data.filter(item => item[key] === keyword);
            if (key.includes('binary')) {
                this.binaryList = data;
            } else {
                this.sourceList = data;
            }
        },
        autocompleteData(data, valueName) {
            let result = [];
            data.forEach(item => {
                let el = {};
                el.value = item[valueName];
                result.push(el);
            });
            return result;
        },
        querySearchBinary(queryString, cb) {
            let queryNames = this.autocompleteData(this.binaryQueryList, "binary_name");
            let results = queryString ? queryNames.filter(this.createFilter(queryString)) : queryNames;
            cb(results);
        },
        querySearchSource(queryString, cb) {
            let queryNames = this.autocompleteData(this.sourceQueryList, "source_name");
            let results = queryString ? queryNames.filter(this.createFilter(queryString)) : queryNames;
            cb(results);
        },
        createFilter(queryString) {
            return (queryName) => {
                return (queryName.value.toLowerCase().indexOf(queryString.toLowerCase()) === 0);
            };
        },
        handleSelectBinary(item) {
            let binaryList = this.binaryQueryList;
            this.filterTableData(binaryList, 'binary_name', item.value);
            this.loadAll(binaryList, 'binary_name');

        },
        handleSelectSource(item) {
            let sourceList = this.sourceQueryList;
            this.filterTableData(this.sourceQueryList, 'source_name', item.value);
            this.loadAll(sourceList, 'source_name');
        },
        loadAll(value, valueName) {
            let result = this.autocompleteData(value, valueName);
            this.queryNames = result;
        },
        getdependList(require) {
            dependList(require)
                .then(response => {
                    this.loading = false;
                    if(response.code === '200') {
                        this.isShowTable = true;
                        this.binaryList = response.resp.binary_list;
                        this.sourceList = response.resp.source_list;
                        this.statistics = response.resp.statistics;
                        this.binaryQueryList = response.resp.binary_list;
                        this.sourceQueryList = response.resp.source_list;
                        this.getGraphData(false);
                        this.excelDownload();
                    } else {
                        this.$message.error(response.message + '\n' + response.tip);
                    }
                })
                .catch(response => {
                    this.loading = false;
                    this.$message.error(response.message + '\n' + response.tip);
                });
        },
        getdependDown(require) {
            dependDown (require)
                .then(response => {
                    this.loading = false;
                    let blob = response;
                    let objectUrl = URL.createObjectURL(blob);
                    this.$refs.download.href = objectUrl;
                })
                .catch(response => {
                    this.loading = false;
                    this.$message.error(response.message + '\n' + response.tip);
                });
        },
        getGraphData(isCLicked, isSource) {
            let required = {};
            required.parameter = this.parameter;
            let data = this.formData;
            let current = this.currentButton.toLowerCase();
            required.parameter.db_priority = this.tableName;
            if (current === 'self') {
                current += 'dep';
                let checked = this.checkList;
                required.parameter.self_build = false;
                if (checked.includes('Self-build')) {
                    required.parameter.self_build = true;
                }
                required.parameter.packtype = checked.includes('source') ? 'source' : 'binary';
                required.node_type = isSource ||'binary';
                required.parameter.with_subpack = false;
                if (checked.includes('with-subpack')) {
                    required.parameter.with_subpack = true;
                }
            } else if (current !== 'bedepend') {
                current += 'dep';
                required.node_type = current.includes('install') ? isSource || 'binary' : isSource || 'source';
                // required.node_type = 'binary'
                required.parameter.packtype = '';
                required.parameter.search_type = '';
                required.parameter.with_subpack = false;
            } else {
                current = 'bedep';
                required.parameter.db_priority = [];
                required.parameter.search_type = this.searchType;
                required.parameter.db_priority.push(this.typeName);
                required.parameter.with_subpack = this.typeList;
                delete required.parameter.self_build;
                if (this.searchSource) {
                    required.parameter.packtype = 'source';
                } else {
                    required.parameter.packtype = 'binary';
                }
                required.node_type = isSource ||'binary';
            }
            data.dependType = current;
            required.queryPkgName = data.queryPkgName;
            required.dependType = data.dependType;
            if (isCLicked) {
                required.node_name = data.node_name;
            } else {
                required.node_name = this.searchName;
            }
            dependGraph (required)
                .then(response => {
                    this.isShowTable = true;
                    this.loading = false;
                    if (response.code === '200') {
                        this.Ddata = response.resp;
                        this.initDraw();
                    } else {
                        this.$message.error(response.message + '\n' + response.tip);
                    }
                })
                .catch(response => {
                    this.loading = false;
                    this.$message.error(response.message + '\n' + response.tip);
                });
        },
        getDbPriority() {
            dbPriority()
                .then(response => {
                    this.loading = false;
                    if(response.code === '200') {
                        this.transData = response.resp;
                        this.productV = response.resp;
                        this.defaultVersion.push(response.resp[0]);
                        this.selectedData.pop();
                        this.selectedData.push(response.resp[0]);
                        this.typeName = response.resp[0];
                        if(this.currentButton !== 'Bedepend') {
                            this.transSelect();
                        }
                    } else {
                        this.loading = false;
                        this.$message.error(response.message + '\n' + response.tip);
                    }
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
.tool-tips {
    position: absolute;
    left: -12px;
    top: 12px;
}
.el-scrollbar__wrap {
    overflow-y: scroll !important;
    overflow-x: hidden;
}
.el-loading-mask {
    z-index: 5;
}
.depend {
    margin-bottom: 120px;
}
.depend .el-form-item__label {
    padding-right: 15px;
    font-size: 16px;
}
.depend .el-checkbox__inner::after {
    border: 1px solid #252C32;
    border-left: 0;
    border-top: 0;
}
.depend .el-checkbox__input.is-checked+.el-checkbox__label {
    color: #000;
}
.depend .el-checkbox__inner:hover {
    border-color: #252C32;
}
.depend .el-checkbox__input.is-focus .el-checkbox__inner {
    border-color: #252C32;
}
.depend .el-checkbox__input.is-checked .el-checkbox__inner,
.depend .el-checkbox__input.is-indeterminate .el-checkbox__inner {
    background-color: #fff;
    border-color: #252C32;
}
.depend .el-checkbox__label {
    font-size: 16px;
}
.depend .el-transfer-panel:last-child .el-transfer-panel__item {
    color: #002fa7
}
.depend-search .el-input__icon,
.depend-type .el-input__inner {
    height: 30px;
}
.depend-search .el-input__icon,
.depend-type .el-input__icon {
    line-height: 30px;
}
.depend-search .el-form--inline .el-form-item {
    height: 30px;
    line-height: 40px;
    margin-right: 0;
}
.depend-search .el-form.el-form--inline {
    display: inline-block;
}
.el-select .el-input.is-focus .el-input__inner {
    border-color: #002fa7;
}
.el-select-dropdown.is-multiple .el-select-dropdown__item.selected {
    color: #002fa7;
}
.el-select-dropdown__list .el-select-dropdown__item {
    display: block;
}
.el-select-dropdown__item.selected {
    color: #002fa7;
}
.el-select .el-input__inner:focus {
    border-color: #002fa7;
}
.el-select-dropdown__list li:first-child {
    margin-left: 0!important;
}
.dialog-footer .el-button {
    display: inline-block;
    width: 80px;
    height: 40px;
}
.dialog-footer .el-button--primary {
    background: #002fa7;
}
.dialog-footer .el-button--default {
    border: 1px solid rgba(0, 0, 0, 0.5);
}
.dialog-footer .el-button--default:hover {
    color: #000;
    background: #fff;
}
.click-transfer .el-dialog--center .el-dialog__body {
    text-align: center;
}
.click-transfer .el-transfer-panel {
    text-align: left;
}
.click-transfer .el-transfer-panel__item:hover {
    color: #002fa7;
}
@media screen and (max-width: 1000px){
    .product-v .el-form-item__label {
        display: none;
    }
    .depend .el-checkbox__label {
        font-size: 14px;
    }
    .depend .el-checkbox__input.is-checked + .el-checkbox__label {
        color: rgba(0, 0, 0, 0.5);
    }
    .el-checkbox {
        margin-right: 20px;
    }
}
</style>
<style scoped>
/deep/.el-transfer-panel{
    display:inline-block;
    width: 270px!important;
    height:100%;
}
.checked-explain{
    position: relative;
    top: 2px;
    left: -26px;
}
.bottom-explain{
    position: relative;
    top: 4px;
    left: 4px;
}
.item{
    position: relative;
    left: -31px;
    top: 2px;
}
.click-transfer>p{
    display: inline-block;
}
h4 {
    font-size: 20px;
    font-family: Roboto-Bold, Roboto;
    font-weight: bold;
    margin-bottom: 20px;
}
button {
    margin: 0;
    padding: 0;
    border: 0;
    outline: none;
    background: none;
}
ul {
    width: 530px;
    height: 60px;
    line-height: 60px;
}
ul:nth-child(even) {
    background-color: rgba(0, 0, 0, 0.05);
}
li {
    display: inline-block;
}
li:first-child {
    margin-left: 20px;
}
.depend-type span {
    margin-right: 30px;
}
.type-btns {
    display: inline-block;
    margin-bottom: 25px;
    line-height: 32px;
}
.type-btns button {
    width: 140px;
    height: 30px;
    padding: 5px 0;
    font-size: 16px;
    border: 1px solid #B8BECC;
    border-right: none;
}
.type-btns button:first-child {
    border-radius: 4px 0px 0px 4px;
}
.type-btns button:last-child {
    border-right: 1px solid #B8BECC;
    border-radius: 0px 4px 4px 0px;
}
.type-btns .active {
    background: #002FA7;
    color: #fff;
    border: 1px solid #002FA7;
}
.type-radio {
    display: inline-block;
    margin-left: 25px;
}
.self-checkBox {
    display: inline-block;
    margin-left: 55px;
}
.pc-search {
    width: 562px;
}
.pc-select {
    width: 500px;
}
.pc-search,
.pc-select {
    display: inline-block;
    margin-left: 20px;
}
.icon-search {
    cursor: pointer;
}
.mobile-search,
.mobile-select {
    display: none;
}
.searching {
    display: block;
}
#package-diagram {
    width: 600px;
    height: 600px;
}
.depend-info-h5 {
    display: none;
}
.table-item .table-name {
    cursor: pointer;
}
.binary li {
    width: 24%;
    height: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.statis li,
.source li {
    width: 32%;
    height: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.self-checkBox {
    display: none;
}
.self-checkBox.show {
    display: inline-block;
}
.be-select {
    display: none;
    margin-left: 50px;
}
.be-select.show {
    display: inline-block;
}
.be-select.source {
    /* height: 40px; */
}
.filter {
    width: 14px;
    height: 14px;
    vertical-align: middle;
    cursor: pointer;
}
.table-title {
    position: relative;
}
.table-item {
    font-family: Roboto-Light;
}
.table-item a {
    color: #002fa7;
}
.table-select {
    position: absolute;
    top: 50px;
    left: 120px;
    line-height: 30px;
    z-index: 1;
}
.table-content {
    margin-top: 35px;
}
.table-content .scrollbar {
    width: 530px;
    height: 280px;
}
.depend-info {
    margin-top: 15px;
    border-top: 1px solid rgba(0, 0, 0, 0.5);
}
.excel-button {
    float: right;
}
.form-button {
    display: inline-block;
    text-decoration: none;
    color: #000;
    height: 30px;
    line-height: 30px;
    border-radius: 4px;
    border: 1px solid rgba(0, 0, 0, 0.5);
    padding: 0 20px;
    cursor: pointer;
    margin-top: 25px;
}
.form-button img {
    width: 19px;
    height: 15px;
}
.table-content.binary {
    margin-top: 75px;
}
.click-transfer {
    height: 45px;
    line-height: 40px;
    margin-bottom: 22px;
}
.click-btn {
    color: #002fa7;
    font-size: 16px;
}
.package-table {
    position: relative;
}
.pkg-diagram {
    width: 600px;
    height: 846px;
    position: absolute;
    right: 0;
    top: 0;
}
@media screen and (max-width: 1000px) {
    .is-pc {
        display: none;
    }
    .pc-search,
    .pc-select {
        display: none;
    }
    .mobile-search,
    .mobile-select {
        display: block;
        width: 315px;
    }
    .excel-button {
        display: none;
    }
    .h5-type {
        display: none;
    }
    .searching {
        display: none;
    }
    .click-transfer {
        display: none;
    }
    ul {
        width: 100%;
        height: unset;
        font-size: 12px;
        font-family: Roboto-Light;
    }
    li {
        margin-left: 20px;
    }
    li a {
        color: #002fa7;
    }
    h4 {
        font-size: 16px;
    }
    .depend-info-h5 {
        margin-top: 40px;
        display: block;
    }
    .binary-h5 {
        padding: 20px 0;
    }
    .binary-h5:nth-child(even) {
        background-color: rgba(0, 0, 0, 0.05);
    }
    .binary-h5:nth-child(odd) {
        background-color: #fff;
    }
    .binary-h5 li {
        display: block;
        height: 30px;
        line-height: 30px;
    }
    .binary-h5 li span {
        display: inline-block;
        width: 85px;
        font-size: 12px;
        font-family: Roboto-Regular;
    }
    .statis li {
        width: 26%;
    }
    .source li {
        width: 26.8%
    }
    .statis-h5 ul{
        font-size: 14px;
        font-family: Roboto-Regular;
        line-height: 40px;
        background-color: rgba(0, 0, 0, 0.05);
    }
    .table-title {
        font-size: 14px;
        font-family: Roboto-Regular;
    }
    .pkg-diagram {
        width: 100%;
        height: 600px;
    }
    .type-btns button {
        font-size: 12px;
        width: 78px;
        font-family: Roboto-Condensed;
    }
    .type-btns button:last-child {
        width: 64px;
    }
    .type-btns button:nth-child(3){
        width: 95px;
    }
    .depend-info {
        border: none;
        display: none;
    }
    .self-checkBox {
        margin-left: 0;
    }
    .package-container label {
        font-size: 14px;
        font-family: Roboto-Light;
    }
    .be-select {
        margin-left: 0;
    }
    .type-select {
        width: 105px;
    }
    .type-radio {
        margin-left: 35px;
    }
    .be-select {
        margin-bottom: 20px;
    }
}
</style>