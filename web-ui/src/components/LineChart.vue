<template>
  <div>
     <!-- <span>12345</span> -->
     <div class="container" :id="linecharts"></div>
  </div>
</template>

<script>
export default {
    name: 'LineChart',
    props: {
      title: {
        type: String,
        default: ''
      },
      xAxisData: {
        type: Array,
        default:() => []
      },
      linedata: {
        type: Array,
        default:() => []
      }
    },
    watch: {
       title(newVal, oldVal){
          this.drawPie(newVal, this.xAxisData, this.linedata)
          console.log(oldVal);
       },
       xAxisData(newVal, oldVal){
          this.drawPie(this.title, newVal, this.linedata)
          console.log(oldVal);
       },
       linedata(newVal, oldVal){
          this.drawPie(this.title, this.xAxisData, newVal)
          console.log(oldVal);
       }
    },
    data (){
      return {
        timer: null
      }
    },
    methods: {
        drawPie(a,b,c){
          this.charts = this.$echarts.init(document.getElementById(this.linecharts))
          this.charts.setOption({
              title: {
               text: a,
               left: "center",
               top: "bottom"
              },
              tooltip: {
               trigger: 'axis',
              //  formatter: function(params){
              //    if (params.data === 0) {
              //     const msg = 'failed'
              //    } else {
              //     const msg = 'success'
              //    }
              //    return 
              //  }
              },
              toolbox: {
              },
              xAxis: {
                name: '天数',
                type: 'category',
                data: b
              },
              yAxis: {
                name: '时间',
                type: 'value',
                axisLabel:{
                  formatter: '{value}min'
                }
              },
              series: [
                { 
                  itemStyle : {  
                                normal : {  
                                    color: function(params) {
                                      //自定义折线点颜色
                                      if(params.data === 0){
                                        return '#ed1941'
                                      } else {
                                        return '#1d953f'
                                      }
                                    },
                                    lineStyle:{  
                                        color:'#6950a1'  
                                    }  
                                }  
                              }, 
                  data: c,
                  type: 'line'
                }
              ]
          })
        }
    },
    computed: {
        linecharts(){
            return 'linecharts' + Math.random()*5000
        }
    },
    mounted () {
        this.$nextTick(function() {
            this.drawPie(this.title,this.xAxisData,this.linedata);
        });
    },
    created () {
      console.log(this.linedata);
    },
    beforeDestroy() {
      this.$emit('closepop');
    }
}
</script>

<style scoped>
  .container{
      /* display: flex!important;
      justify-content: center!important;
      align-items: center!important; */
      width: 1000px;
      height: 500px;
  }
</style>