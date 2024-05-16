// var dom = document.getElementById('container_echart');
//     var myChart = echarts.init(dom, null, {
//       renderer: 'canvas',
//       useDirtyRect: false,
//       // locale: 'en'
//     });
//     var app = {};
// 页面加载完成后发送请求获取后端数据并渲染图表
document.addEventListener('DOMContentLoaded', function () {
    fetch('/analysis/week_data')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load chart data: ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            renderChart(data.sleep_duration, data.emotions); // 渲染图表
        })
        .catch(error => {
            console.error(error); // 输出错误信息
        });
});
    // 渲染图表函数
function renderChart(data_sleep,data_emotion) {
    var dom = document.getElementById('week_echart');
    var myChart = echarts.init(dom, null, {
        renderer: 'canvas',
        useDirtyRect: false,
        locale: 'en'
    });

    var option;

    option = {
  tooltip: {
    trigger: 'axis',
    axisPointer: {
      type: 'cross',
      crossStyle: {
        color: '#999'
      }
    }
  },
  toolbox: {
    feature: {
      magicType: { show: true, type: ['line', 'bar'] },
      restore: { show: true }
    },
      top: '3%',
  },
    grid: {
        top: '19%', // 设置图表区域在容器中的上边距为 25%
        left: '10%', // 设置图表区域在容器中的左边距为 10%
        right: '10%', // 设置图表区域在容器中的右边距为 10%
        bottom: '10%' // 设置图表区域在容器中的下边距为 10%
    },
  legend: {
    data: ['SleepDuration', 'Precipitation', 'Emotions']
  },
  xAxis: [
    {
      type: 'category',
      data: ['DAY1', 'DAY2', 'DAY3', 'DAY4', 'DAY5', 'DAY6', 'DAY7'],
      axisPointer: {
        type: 'shadow'
      }
    }
  ],
  yAxis: [
    {
      type: 'category',
      name: 'SleepDuration',
      data:['<3','3-4','4-5','5-6','6-7','7-8','8-9','9-10','>10']
    },
    {
      type: 'category',
      name: 'Emotions',
      data: ['Angry', 'Fear', 'Sad', 'Neutral', 'Happy']
    }
  ],
  series: [
    {
      name: 'SleepDuration',
      type: 'bar',
      itemStyle: {
        color: '#C9C6FF' // 修改柱状图颜色
      },
      tooltip: {
        valueFormatter: function (value) {
          return value + ' h';
        }
      },
      data: data_sleep
    },
    {
      name: 'Emotions',
      type: 'line',
      yAxisIndex: 1,
      lineStyle: {
        width: 3 // 设置线条粗细
      },
      symbolSize: 8,
      itemStyle: {
        color: '#6f6bd2', // 修改折线图颜色
      },
      tooltip: {
        valueFormatter: function (value) {
          return value;
        }
      },
      data: data_emotion
    }
  ]
};

    if (option && typeof option === 'object') {
      myChart.setOption(option);
    }

   window.addEventListener('resize', function () {
        myChart.resize();
    });
}