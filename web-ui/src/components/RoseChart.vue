<template>
    <div class="container" :id="rosecharts"></div>
</template>

<script>
export default {
    name: 'RoseChart',
    props: {
      title: {
         type: String,
         default: ''
      },
      roseData: {
         type: Array,
         default: () => []
      }
    },
    data (){
      return {
      }
    },
    methods: {
        drawPie(){
          this.charts = this.$echarts.init(document.getElementById(this.rosecharts))
          this.charts.setOption({
            title: {
             text: this.title,
             left: "center",
             top: "bottom"
            },
            legend: {
             orient: 'vertical',
             left: "left"
            },
            tooltip: {
             trigger: "item",
             formatter: "{a}<br/>{b}:{c} ({d}%)"
            },
            toolbox: {
              show: false,
              feature: {
                mark: { show: true },
                dataView: { show: true, readOnly: false },
                restore: { show: true },
                saveAsImage: { show: true }
              }
            },
            series: [
              {
                name: '状态分布',
                type: 'pie',
                radius: [40, 200],
                center: ['50%', '50%'],
                roseType: 'area',
                itemStyle: {
                  borderRadius: 8
                },
                //自定义颜色
                color: ["#1ab394", "#afb4db", "#426ab3", "#f391a9"],
                data: this.roseData
              }
            ]
          })
        }
    },
    computed: {
        rosecharts(){
            return 'rosecharts' + Math.random()*5000
        }
    },
    mounted () {
        this.$nextTick(function() {
        this.drawPie();
      });
    }
}
</script>

<style scoped>
  .container{
      width: 800px;
      height: 500px;
  }
</style>