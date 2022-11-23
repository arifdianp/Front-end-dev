// EXTEND JQUERY FOR ANIMATION##################################################
$.fn.extend({
    animateCss: function (animationName, callback) {
        callback =  callback || null;
        var animationEnd = 'webkitAnimationEnd mozAnimationEnd MSAnimationEnd oanimationend animationend';
        this.addClass('animated ' + animationName).one(animationEnd, function() {
            $(this).removeClass('animated ' + animationName);
            if (typeof callback == 'function'){
                callback.call(this);
            }
        });
        return this;
    }
});

$(document).ready(function(){

    // SEND RECAP TO CLIENT ON PART STATUS####################################
    $('.recap-mail-button').off();
    $('.recap-mail-button').click(function(){
        $(this).addClass("disabled");
        $.ajax({
            url: '/digital/parts/send-recap-mail/',
            data:{
            },
            dataType:'json',
            success:function(data){
                if (data.success){
                    console.log(data.success);
                    $(this).animateCss('tada');
                    $(this).removeClass("disabled");
                };
                if (data.error){
                    console.log(data.error);
                };
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                console.log("Status: " + textStatus); console.log("Error: " + errorThrown);
            }
        });
    });
    // END SEND RECAP TO CLIENT ON PART STATUS####################################
});

type = ['','info','success','warning','danger'];
demo = {
    initPickColor: function(){
        $('.pick-class-label').click(function(){
            var new_class = $(this).attr('new-class');
            var old_class = $('#display-buttons').attr('data-class');
            var display_div = $('#display-buttons');
            if(display_div.length) {
            var display_buttons = display_div.find('.btn');
            display_buttons.removeClass(old_class);
            display_buttons.addClass(new_class);
            display_div.attr('data-class', new_class);
            }
        });
    },

    initChartist: function(){

        var dataSales = {
          labels: ['9:00AM', '12:00AM', '3:00PM', '6:00PM', '9:00PM', '12:00PM', '3:00AM', '6:00AM'],
          series: [
             [287, 385, 490, 562, 594, 626, 698, 895, 952],
            [67, 152, 193, 240, 387, 435, 535, 642, 744],
            [23, 113, 67, 108, 190, 239, 307, 410, 410]
          ]
        };

        var optionsSales = {
          lineSmooth: false,
          low: 0,
          high: 1000,
          showArea: true,
          height: "245px",
        //   axisX: {
        //     showGrid: false,
        //   },
          lineSmooth: Chartist.Interpolation.simple({
            divisor: 3
          }),
          showLine: true,
        //   showPoint: false,
        };

        var responsiveSales = [
          ['screen and (max-width: 640px)', {
            axisX: {
              labelInterpolationFnc: function (value) {
                return value[0];
              }
            }
          }]
        ];

        var chart1 = Chartist.Line('#chartHours', dataSales, optionsSales, responsiveSales);
        var seq = 0,delays = 50,durations = 200;
        // Once the chart is fully created we reset the sequence
        chart1.on('created', function() {
          seq = 0;
        });
        // On each drawn element by Chartist we use the Chartist.Svg API to trigger SMIL animations
        chart1.on('draw', function(data) {
          seq++;
          if(data.type === 'line') {
            // If the drawn element is a line we do a simple opacity fade in. This could also be achieved using CSS3 animations.
            data.element.animate({
              opacity: {
                // The delay when we like to start the animation
                begin: seq * delays *0.5,
                // Duration of the animation
                dur: durations * 1.5,
                // The value where the animation should start
                from: 0,
                // The value where it should end
                to: 1
              }
            });
        } else if(data.type === 'area'){
            // If the drawn element is an area we do a simple opacity fade in. This could also be achieved using CSS3 animations.
            data.element.animate({
              opacity: {
                // The delay when we like to start the animation
                begin: seq * delays + 1000,
                // Duration of the animation
                dur: durations*5,
                // The value where the animation should start
                from: 0,
                // The value where it should end
                to: 1
              }
            });
        } else if(data.type === 'label' && data.axis === 'x') {
            data.element.animate({
              y: {
                begin: seq * delays,
                dur: durations,
                from: data.y + 100,
                to: data.y,
                // We can specify an easing function from Chartist.Svg.Easing
                easing: 'easeOutQuart'
              }
            });
          } else if(data.type === 'label' && data.axis === 'y') {
            data.element.animate({
              x: {
                begin: seq * delays,
                dur: durations,
                from: data.x - 100,
                to: data.x,
                easing: 'easeOutQuart'
              }
            });
          } else if(data.type === 'point') {
            data.element.animate({
              x1: {
                begin: seq * delays* 0.7,
                dur: durations,
                from: data.x - 10,
                to: data.x,
                easing: 'easeOutQuart'
              },
              x2: {
                begin: seq * delays * 0.7,
                dur: durations,
                from: data.x - 10,
                to: data.x,
                easing: 'easeOutQuart'
              },
              opacity: {
                begin: seq * delays* 0.7,
                dur: durations,
                from: 0,
                to: 1,
                easing: 'easeOutQuart'
              }
            });
          } else if(data.type === 'grid') {
            // Using data.axis we get x or y which we can use to construct our animation definition objects
            var pos1Animation = {
              begin: seq * delays,
              dur: durations*0.2,
              from: data[data.axis.units.pos + '1'] - 30,
              to: data[data.axis.units.pos + '1'],
              easing: 'easeOutQuart'
            };

            var pos2Animation = {
              begin: seq * delays,
              dur: durations*0.2,
              from: data[data.axis.units.pos + '2'] - 100,
              to: data[data.axis.units.pos + '2'],
              easing: 'easeOutQuart'
            };

            var animations = {};
            animations[data.axis.units.pos + '1'] = pos1Animation;
            animations[data.axis.units.pos + '2'] = pos2Animation;
            animations['opacity'] = {
              begin: seq * delays,
              dur: durations * 0.2,
              from: 0,
              to: 1,
              easing: 'easeOutQuart'
            };

            data.element.animate(animations);
          }
        });

// SECOND CHART#######################################################################
        var data = {
          labels: ['Jan', 'Feb', 'Mar', 'Apr', 'Mai', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
          series: [
            [542, 543, 520, 680, 653, 753, 326, 434, 568, 610, 756, 895],
            [230, 293, 380, 480, 503, 553, 600, 664, 698, 710, 736, 795]
          ]
        };

        var options = {
            seriesBarDistance: 10,
            axisX: {
                showGrid: false
            },
            height: "245px"
        };

        var responsiveOptions = [
          ['screen and (max-width: 640px)', {
            seriesBarDistance: 5,
            axisX: {
              labelInterpolationFnc: function (value) {
                return value[0];
              }
            }
          }]
        ];

        var chart2 = Chartist.Line('#chartActivity', data, options, responsiveOptions);
        var seq = 0,delays = 50,durations = 200;
        // Once the chart is fully created we reset the sequence
        chart2.on('created', function() {
          seq = 0;
        });
        // On each drawn element by Chartist we use the Chartist.Svg API to trigger SMIL animations
        chart2.on('draw', function(data) {
          seq++;
          if(data.type === 'line') {
            // If the drawn element is a line we do a simple opacity fade in. This could also be achieved using CSS3 animations.
            data.element.animate({
              opacity: {
                // The delay when we like to start the animation
                begin: seq * delays *0.5,
                // Duration of the animation
                dur: durations * 1.5,
                // The value where the animation should start
                from: 0,
                // The value where it should end
                to: 1
              }
            });
        } else if(data.type === 'area'){
            // If the drawn element is an area we do a simple opacity fade in. This could also be achieved using CSS3 animations.
            data.element.animate({
              opacity: {
                // The delay when we like to start the animation
                begin: seq * delays + 1000,
                // Duration of the animation
                dur: durations*5,
                // The value where the animation should start
                from: 0,
                // The value where it should end
                to: 1
              }
            });
        } else if(data.type === 'label' && data.axis === 'x') {
            data.element.animate({
              y: {
                begin: seq * delays,
                dur: durations,
                from: data.y + 100,
                to: data.y,
                // We can specify an easing function from Chartist.Svg.Easing
                easing: 'easeOutQuart'
              }
            });
          } else if(data.type === 'label' && data.axis === 'y') {
            data.element.animate({
              x: {
                begin: seq * delays,
                dur: durations,
                from: data.x - 100,
                to: data.x,
                easing: 'easeOutQuart'
              }
            });
          } else if(data.type === 'point') {
            data.element.animate({
              x1: {
                begin: seq * delays* 0.7,
                dur: durations,
                from: data.x - 10,
                to: data.x,
                easing: 'easeOutQuart'
              },
              x2: {
                begin: seq * delays * 0.7,
                dur: durations,
                from: data.x - 10,
                to: data.x,
                easing: 'easeOutQuart'
              },
              opacity: {
                begin: seq * delays* 0.7,
                dur: durations,
                from: 0,
                to: 1,
                easing: 'easeOutQuart'
              }
            });
          } else if(data.type === 'grid') {
            // Using data.axis we get x or y which we can use to construct our animation definition objects
            var pos1Animation = {
              begin: seq * delays,
              dur: durations*0.2,
              from: data[data.axis.units.pos + '1'] - 30,
              to: data[data.axis.units.pos + '1'],
              easing: 'easeOutQuart'
            };

            var pos2Animation = {
              begin: seq * delays,
              dur: durations*0.2,
              from: data[data.axis.units.pos + '2'] - 100,
              to: data[data.axis.units.pos + '2'],
              easing: 'easeOutQuart'
            };

            var animations = {};
            animations[data.axis.units.pos + '1'] = pos1Animation;
            animations[data.axis.units.pos + '2'] = pos2Animation;
            animations['opacity'] = {
              begin: seq * delays,
              dur: durations * 0.2,
              from: 0,
              to: 1,
              easing: 'easeOutQuart'
            };

            data.element.animate(animations);
          }
        });
// 
// // PIE CHART###################################################################################################
//         parts_plastic = parseInt(parts_plastic);
//         parts_metal = parseInt(parts_metal);
//         parts_total = parseInt(parts_total);
//         if (parts_total == 0){parts_total=1};//safety
//         // console.log(parts_plastic);
//         // console.log(parts_metal);
//         // console.log(parts_plastic);
//         var dataPreferences = {
//             series:[parts_plastic, parts_metal],
//             labels: [((parts_plastic*100.0)/parts_total).toFixed(0) + "%", ((parts_metal*100.0)/parts_total).toFixed(0) +'%']
//         };
// 
//         var optionsPreferences = {
//             donut: true,
//             showLabel: false,
//             donutWidth: 60,
//             startAngle: 0,
//             total: parts_total,
//             showLabel: true,
//         };
// 
//         var chart3 = Chartist.Pie('#chartPreferences', dataPreferences, optionsPreferences);
// 
//         chart3.on('draw', function(data) {
//           if(data.type === 'slice') {
//             // Get the total path length in order to use for dash array animation
//             var pathLength = data.element._node.getTotalLength();
// 
//             // Set a dasharray that matches the path length as prerequisite to animate dashoffset
//             data.element.attr({
//               'stroke-dasharray': pathLength + 'px ' + pathLength + 'px',
//               'id':"thibault"
//             });
// 
//             // Create animation definition while also assigning an ID to the animation for later sync usage
//             var animationDefinition = {
//               'stroke-dashoffset': {
//                 id: 'anim' + data.index,
//                 dur: 350,
//                 from: -pathLength + 'px',
//                 to:  '0px',
//                 easing: Chartist.Svg.Easing.easeInOutSine,
//                 // We need to use `fill: 'freeze'` otherwise our animation will fall back to initial (not visible)
//                 fill: 'freeze'
//               }
//             };
// 
//             // If this was not the first slice, we need to time the animation so that it uses the end sync event of the previous animation
//             if(data.index !== 0) {
//               animationDefinition['stroke-dashoffset'].begin = 'anim' + (data.index - 1) + '.end';
//             }
// 
//             // We need to set an initial value before the animation starts as we are not in guided mode which would do that for us
//             data.element.attr({
//               'stroke-dashoffset': -pathLength + 'px'
//             });
// 
//             // We can't use guided mode as the animations need to rely on setting begin manually
//             // See http://gionkunz.github.io/chartist-js/api-documentation.html#chartistsvg-function-animate
//             data.element.animate(animationDefinition, false);
//         } else if (data.type == "label"){
//             var to_opacity = 1;
//             if (data.text == "0%"){to_opacity=0};
//             // console.log(data.text);
//             // If the drawn element is an area we do a simple opacity fade in. This could also be achieved using CSS3 animations.
//             data.element.animate({
//               opacity: {
//                 // The delay when we like to start the animation
//                 begin: 1200,
//                 // Duration of the animation
//                 dur: 200,
//                 // The value where the animation should start
//                 from: 0,
//                 // The value where it should end
//                 to: to_opacity
//               }
//             });
//         }
//         });
// 


        // // APPLIANCE FAMILY BAR CHART##############################################################################
        // var app_fam_labels = [];
        // var serie = [];
        // for (var i = 0; i<appliance_family_distribution.length; i++){
        //     app_fam_labels.push(appliance_family_distribution[i].type__appliance_family__name);
        //     serie.push(appliance_family_distribution[i].count);
        // };
        // var dataViews = {
        //     labels: app_fam_labels,
        //       series: [
        //          serie
        //       ]
        // };
        // 
        // var optionsViews = {
        //     height: "250px",
        //     seriesBarDistance: 10,
        //     reverseData: true,
        //     horizontalBars: true,
        //   classNames: {
        //     bar: 'ct-bar'
        //   },
        //   axisY: {
        //       offset: 70
        //   },
        //   axisX: {
        //     showGrid: true,
        //     divisor:2
        //   },
        // 
        // };
        // 
        // var responsiveOptionsViews = [
        //   ['screen and (max-width: 640px)', {
        //     seriesBarDistance: 5,
        //     axisX: {
        //       labelInterpolationFnc: function (value) {
        //         return value[0];
        //       }
        //     }
        //   }]
        // ];
        // 
        // var chart_family = Chartist.Bar('#applianceFamilyBarChart', dataViews,optionsViews, responsiveOptionsViews);
        // // END APPLIANCE FAMILY BAR CHART##############################################################################

    },
	showNotification: function(from, align){
    	color = Math.floor((Math.random() * 4) + 1);

    	$.notify({
        	icon: "ti-gift",
        	message: "Welcome to <b>Paper Dashboard</b> - a beautiful freebie for every web developer."

        },{
            type: type[color],
            timer: 4000,
            placement: {
                from: from,
                align: align
            }
        });
	},
    initDocumentationCharts: function(){
    //     	init single simple line chart
        var dataPerformance = {
          labels: ['6pm','9pm','11pm', '2am', '4am', '8am', '2pm', '5pm', '8pm', '11pm', '4am'],
          series: [
            [1, 6, 8, 7, 4, 7, 8, 12, 16, 17, 14, 13]
          ]
        };

        var optionsPerformance = {
          showPoint: false,
          lineSmooth: true,
          height: "200px",
          axisX: {
            showGrid: false,
            showLabel: true
          },
          axisY: {
            offset: 40,
          },
          low: 0,
          high: 16,
          height: "250px"
        };

        Chartist.Line('#chartPerformance', dataPerformance, optionsPerformance);

    //     init single line with points chart
        var dataStock = {
          labels: ['\'07','\'08','\'09', '\'10', '\'11', '\'12', '\'13', '\'14', '\'15'],
          series: [
            [22.20, 34.90, 42.28, 51.93, 62.21, 80.23, 62.21, 82.12, 102.50, 107.23]
          ]
        };

        var optionsStock = {
          lineSmooth: false,
          height: "200px",
          axisY: {
            offset: 40,
            labelInterpolationFnc: function(value) {
                return '$' + value;
              }

          },
          low: 10,
          height: "250px",
          high: 110,
            classNames: {
              point: 'ct-point ct-green',
              line: 'ct-line ct-green'
          }
        };

        Chartist.Line('#chartStock', dataStock, optionsStock);

    //      init multiple lines chart
        var dataSales = {
          labels: ['9:00AM', '12:00AM', '3:00PM', '6:00PM', '9:00PM', '12:00PM', '3:00AM', '6:00AM'],
          series: [
             [287, 385, 490, 562, 594, 626, 698, 895, 952],
            [67, 152, 193, 240, 387, 435, 535, 642, 744],
            [23, 113, 67, 108, 190, 239, 307, 410, 410]
          ]
        };

        var optionsSales = {
          lineSmooth: false,
          low: 0,
          high: 1000,
          showArea: true,
          height: "245px",
          axisX: {
            showGrid: false,
          },
          lineSmooth: Chartist.Interpolation.simple({
            divisor: 3
          }),
          showLine: true,
          showPoint: false,
        };

        var responsiveSales = [
          ['screen and (max-width: 640px)', {
            axisX: {
              labelInterpolationFnc: function (value) {
                return value[0];
              }
            }
          }]
        ];

        Chartist.Line('#chartHours', dataSales, optionsSales, responsiveSales);

    //      pie chart
        Chartist.Pie('#chartPreferences', {
          labels: ['62%','32%','6%'],
          series: [62, 32, 6]
        });


    }

}

function post(path, params, method) {
    method = method || "post"; // Set method to post by default if not specified.

    // The rest of this code assumes you are not using a library.
    // It can be made less wordy if you use one.
    var form = document.createElement("form");
    form.setAttribute("method", method);
    form.setAttribute("action", path);

    for(var key in params) {
        if(params.hasOwnProperty(key)) {
            var hiddenField = document.createElement("input");
            hiddenField.setAttribute("type", "hidden");
            hiddenField.setAttribute("name", key);
            hiddenField.setAttribute("value", params[key]);

            form.appendChild(hiddenField);
        }
    }

    document.body.appendChild(form);
    form.submit();
}

function logout(){
    post("/account/logout/",{csrfmiddlewaretoken:csrftoken});
};
