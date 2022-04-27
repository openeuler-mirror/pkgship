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
    methods: {
       drawPie() {
         this.charts = this.$echarts.init(document.getElementById(this.echarts));
         this.charts.setOption({
           title: {
             text: this.title,
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
                    var colorList = ["#1ab394","#ed1941","#ffd400","#426ab3","#afb4db","#f391a9","#8552a1","#C0FF3E","#E0FFFF"];
                    return colorList[params.dataIndex];
                  }
                },
                data: this.pieData
             }
           ]
         });
       },
    },
    computed: {
      echarts() {
        return 'echarts' + Math.random()*100000
      }
    },
    mounted () {
      this.$nextTick(function() {
        this.drawPie();
      });
    },
    created () {
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