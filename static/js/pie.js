// var dom = document.getElementById('container');
// var myChart = echarts.init(dom, null, {
//   renderer: 'canvas',
//   useDirtyRect: false
// });
// var app = {};
//
// var option;
//
// option = {
// tooltip: {
// trigger: 'item'
// },
// legend: {
// top: '5%',
// left: 'center'
// },
// series: [
// {
//   name: 'Days',
//   type: 'pie',
//   radius: ['20%', '70%'],
//   avoidLabelOverlap: false,
//   itemStyle: {
//     borderRadius: 10,
//     borderColor: '#fff',
//     borderWidth: 2
//   },
//   label: {
//     show: false,
//     position: 'center'
//   },
//   emphasis: {
//     label: {
//       show: true,
//       fontSize: 40,
//       fontWeight: 'bold'
//     }
//   },
//   labelLine: {
//     show: false
//   },
//   data: [
//     { value: 3, name: 'Angry', itemStyle: { color: '#FF8686' } },
//     { value: 4, name: 'Happy', itemStyle:{color:'#FACA82'} },
//     { value: 5, name: 'Neutral', itemStyle:{color:'#BDEFA5'} },
//     { value: 2, name: 'Sad', itemStyle:{color:'#9DD6FF'} },
//     { value: 3, name: 'Fear', itemStyle:{color:'#C9C6FF'} }
//   ]
// }
// ]
// };
//
// if (option && typeof option === 'object') {
//   myChart.setOption(option);
// }
//
// window.addEventListener('resize', myChart.resize);


// $.ajax({
//     url: '/analysis/weather_emotion_counts',  // 后端接口的URL
//     type: 'GET',
//     success: function(week_emotion) {
//         // 成功获取数据后的处理
//         console.log(week_emotion);  // 打印返回的数据
//         // 在这里可以将数据进行进一步处理或展示在页面上
//         renderPieChart('sunny', week_emotion.sunny); // 渲染默认选项卡中的图表
//             renderPieChart('rainy', week_emotion.rainy);
//             renderPieChart('snowy', week_emotion.snowy);
//             renderPieChart('cloudy', week_emotion.cloudy);
//             renderPieChart('overcast', week_emotion.overcast);
//             renderPieChart('extreme', week_emotion.extreme);
//         console.log(week_emotion.cloudy)
//     },
//     error: function(xhr, status, error) {
//         // 请求失败时的处理
//         console.error(xhr, status, error);  // 打印错误信息
//     }
// });


document.addEventListener('DOMContentLoaded', function () {
    fetch('/analysis/weather_emotion_counts')
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to load chart data: ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            console.log(data);
            renderPieChart('sunny', data.sunny); // 渲染默认选项卡中的图表
            renderPieChart('rainy', data.rainy);
            renderPieChart('snowy', data.snowy);
            renderPieChart('cloudy', data.cloudy);
            renderPieChart('overcast', data.overcast);
            renderPieChart('extreme', data.extreme);

        })
        .catch(error => {
            console.error(error); // 输出错误信息
        });
});


// 渲染饼图函数
function renderPieChart(tabId, data) {
    var dom = document.getElementById(tabId + 'Chart');
    var myChart = echarts.init(dom, null, {
        renderer: 'canvas',
        useDirtyRect: false
    });

    var option = {
        tooltip: {
            trigger: 'item'
        },
        legend: {
            top: '5%',
            left: 'center'
        },
        series: [
            {
                name: 'Days',
                type: 'pie',
                radius: ['20%', '70%'],
                avoidLabelOverlap: false,
                itemStyle: {
                    borderRadius: 10,
                    borderColor: '#fff',
                    borderWidth: 2
                },
                label: {
                    show: false,
                    position: 'center'
                },
                emphasis: {
                    label: {
                        show: true,
                        fontSize: 40,
                        fontWeight: 'bold'
                    }
                },
                labelLine: {
                    show: false
                },
                data: data
            }
        ]
    };

    if (option && typeof option === 'object') {
        myChart.setOption(option);
    }

    window.addEventListener('resize', myChart.resize);
}

// 自定义颜色函数
function getColor(emotion) {
    // 在这里根据情绪名称返回对应的颜色
    // 例如，你可以使用一个预定义的颜色映射表
    // 或者根据不同的情绪类型生成随机颜色
    // 这里只是一个简单的示例，你可以根据实际需求进行调整
    if (emotion === 'Angry') {
        return '#FF8686';
    } else if (emotion === 'Happy') {
        return '#FACA82';
    } else if (emotion === 'Neutral') {
        return '#BDEFA5';
    } else if (emotion === 'Sad') {
        return '#9DD6FF';
    } else if (emotion === 'Fear') {
        return '#C9C6FF';
    } else {
        // 其他情绪类型的默认颜色
        return '#cccccc';
    }
}


// document.addEventListener('DOMContentLoaded', function() {
//     // 获取所有选项卡的链接元素
//     var tabLinks = document.querySelectorAll('.nav-link');
//
//     // 获取所有选项卡内容的元素
//     var tabContents = document.querySelectorAll('.tab-pane');
//
//
//     // 为每个选项卡链接添加点击事件监听器
//     tabLinks.forEach(function(tabLink) {
//         tabLink.addEventListener('click', function(event) {
//             // 阻止默认行为，以防止链接跳转
//             event.preventDefault();
//
//             // 获取当前被点击的选项卡的 href 属性值
//             var tabId = this.getAttribute('href').substring(1);
//
//             tabContents.forEach(function(tabContent) {
//                 if (tabContent.id === tabId) {
//                     tabContent.classList.add('show', 'active');
//                     console.log(tabContent.classList)
//                 } else {
//                     tabContent.classList.remove('show', 'active');
//                 }
//             });
//
//             // 输出所点击的选项卡的标识
//             console.log('Clicked tab ID:', tabId);
//
//             // 在这里可以根据所点击的选项卡执行相应的操作
//         });
//     });
// });


document.addEventListener('DOMContentLoaded', function () {
    var isFirstLoad = localStorage.getItem('isFirstLoad');

    if (!isFirstLoad) {
        // 第一次加载页面的操作
        console.log('第一次加载页面');

        // 设置标志位为已存在
        localStorage.setItem('isFirstLoad', 'true');
    } else {
        // 非第一次加载页面的操作
        console.log('非第一次加载页面');
    }
});
document.addEventListener('DOMContentLoaded', function () {
    var isFirstLoad = localStorage.getItem('isFirstLoad');

    if (!isFirstLoad) {
        // 第一次加载页面的操作
        console.log('第一次加载页面');

        // 设置标志位为已存在
        localStorage.setItem('isFirstLoad', 'true');
    } else {
        // 非第一次加载页面的操作
        console.log('非第一次加载页面');
    }
});


document.addEventListener('DOMContentLoaded', function () {
    var isFirstLoad = localStorage.getItem('isFirstLoad');


    // 获取所有选项卡的链接元素
    var tabLinks = document.querySelectorAll('.nav-link');

    // 获取所有选项卡内容的元素
    var tabContents = document.querySelectorAll('.tab-pane');


    // 为每个选项卡链接添加点击事件监听器
    tabLinks.forEach(function (tabLink) {
        tabLink.addEventListener('click', function (event) {
            // 阻止默认行为，以防止链接跳转
            event.preventDefault();

            // 获取当前被点击的选项卡的 href 属性值
            var tabId = this.getAttribute('href').substring(1);

            // 隐藏所有选项卡内容
            tabContents.forEach(function (tabContent) {
                tabContent.classList.remove('show', 'active');
            });

            // 显示所点击的选项卡对应的内容
            var selectedTabContent = document.getElementById(tabId);
            if (selectedTabContent) {
                selectedTabContent.classList.add('show', 'active');
            }

            // 在这里可以根据所点击的选项卡执行相应的操作
        });
    });

    // if (!isFirstLoad) {
    //     // 第一次加载页面的操作
    //     console.log('第一次加载页面');
    //
    //     // 设置标志位为已存在
    //     localStorage.setItem('isFirstLoad', 'true');
    //
    //     // 隐藏除了 id 为 sunny 的选项卡内容之外的其他选项卡内容
    //     // var tabContents = document.querySelectorAll('.tab-pane');
    //     tabContents.forEach(function (tabContent) {
    //         if (tabContent.id !== 'sunny') {
    //             tabContent.classList.remove('show', 'active');
    //         }
    //     });
    //
    //     // 显示 id 为 sunny 的选项卡内容
    //     var sunnyTabContent = document.getElementById('sunny');
    //     if (sunnyTabContent) {
    //         sunnyTabContent.classList.add('show', 'active');
    //     }
    // } else {
    //     // 非第一次加载页面的操作
    //     console.log('非第一次加载页面');
    // }
});
