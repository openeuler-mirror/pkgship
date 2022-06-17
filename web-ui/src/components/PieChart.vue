<template>
    <div class="container" :id="echarts"></div>
</template>

<script>
export default {
    name: 'PieChart',
    props: {
       title: {
         type: String,
         default: undefined
       },
       pieData: {
         type: Array,
         default: () => []
       }
    },
    data (){
      return {
          charts: "",
          opinionData: [
            { value: 12, name: "及格人数" },
            { value: 18, name: "未及格人数" }
          ]
      }
    },
    watch: {
       title(newVal, oldVal){
          this.drawPie(this.pieData, newVal)
          console.log(oldVal);
       },
       pieData(newVal, oldVal){
          this.drawPie(newVal, this.title)
          console.log(oldVal);
       }
    },
    methods: {
       drawPie(a,b) {
         this.charts = this.$echarts.init(document.getElementById(this.echarts));
         var option = {
           title: {
             text: b,
             left: "center",
             top: "bottom"
           },
           tooltip: {
             trigger: "item",
             formatter: "{a}<br/>{b}:{c} ({d}%)"
           },
           legend: {
             orient: 'vertical',
             left: "left",
             formatter: function(name) {
                  // 获取legend显示内容
                  let data = option.series[0].data;
                  let total = 0;
                  let tarValue = 0;
                  for (let i = 0, l = data.length; i < l; i++) {
                      total += data[i].value;
                      if (data[i].name == name) {
                          tarValue = data[i].value;
                      }
                  }
                  if(total != 0){
                    let p = (tarValue / total * 100).toFixed(2);
                    return name + ' ' + ' ' + p + '%';
                  } else {
                    let p = 0
                    return name + ' ' + ' ' + p + '%';
                  }
                  
             },
           },
           series: [
             {
                name: "状态",
                type: "pie",
                radius: "65%",
                center: ["50%", "50%"],
                avoidLabelOverlap: false,
                itemStyle: {
                  emphasis: {
                    shadowBlur: 10,
                    shadowOffsetX: 0,
                    shadowColor: "rgba(0, 0, 0, 0.5)"
                  },
                  color: function(params) {
                    //自定义颜色
                    console.log(params);
                    if(params.data.name === "无数据"){
                      return "#999d9c"
                    }else {
                      var colorList = ["#1ab394","#ed1941","#ffd400","#426ab3","#afb4db","#f391a9","#8552a1","#C0FF3E","#40E7E7"];
                      return colorList[params.dataIndex];
                    }
                  }
                },
                data: a
             }
           ]
         }
         this.charts.setOption(option, true);
       },
    },
    computed: {
      echarts() {
        return 'echarts' + Math.random()*100000
      }
    },
    mounted () {
      this.$nextTick(function() {
        this.drawPie(this.pieData,this.title);
      });
    },
    created () {
      console.log(this.pieData);
    }
}
</script>

<style scoped>
  .container{
      /* display: flex!important;
      justify-content: center!important;
      align-items: center!important; */
      width: 800px;
      height: 500px;
  }
</style>