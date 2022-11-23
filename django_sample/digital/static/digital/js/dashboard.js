$(document).ready(function(){
    
    
    
    // PIE CHART APPLIANCE FAMILY DISTRIB######################################################
        
        var app_fam_labels = [];
        var serie = [];
        var total_parts_1 = 0;
        for (var i = 0; i<appliance_fam_distrib.length; i++){
            total_parts_1 += appliance_fam_distrib[i].count;
        };
        var various_value = 0;
        var various_title = "";
        var i = appliance_fam_distrib.length
        while (i--){
            var value = (appliance_fam_distrib[i].count*100)/total_parts_1;
            if (value>5){
                appliance_fam_distrib[i].value = value;
                app_fam_labels.unshift(appliance_fam_distrib[i].type__appliance_family__name);
                // serie.push(appliance_fam_distrib[i].count);
            }else{
                various_value += value; //increment various count
                various_title += appliance_fam_distrib[i].type__appliance_family__name + "--";
                appliance_fam_distrib.splice(i,1); //remove elemt from list
            }
        };
        // add the other accumulated category
        // var various_value = (various_count*100)/total_parts_1;
        if (various_value){
            app_fam_labels.push("Various: ");
            appliance_fam_distrib.push({type__appliance_family__name:various_title, value:various_value})
        }
        
        var dataPreferences = {
            series:appliance_fam_distrib,
            labels: app_fam_labels
        };

        var optionsPreferences = {
            donut: true,
            showLabel: false,
            donutWidth: 60,
            startAngle: 0,
            total: 100,
            showLabel: true,
        };

        var chartApplianceFamily = Chartist.Pie('#ApplianceFamilyPieChart', dataPreferences, optionsPreferences);
        // add special data attributes for further use of charts
        chartApplianceFamily.on('draw', function(data) {
            if(data.type === 'slice') {
                if (searchParams.appliance == data.series.type__appliance_family__name){
                    data.element.addClass("active");
                }
                // Set a dasharray that matches the path length as prerequisite to animate dashoffset
                data.element.attr({
                  'data-type':"appliance_family",
                  'data-appliance':data.series.type__appliance_family__name,
                  'data-toggle':"tooltip",
                  'data-placement':"right",
                  'title':parseFloat(data.element.attr('ct:value')).toFixed(0) + " %",
                });

            } 
        });
        
        chartApplianceFamily.on("created", function () {
            $('#ApplianceFamilyPieChart .ct-slice-donut').tooltip({
                trigger : 'hover',
                container: '#ApplianceFamilyPieChartContainer',            
            });
            $('#ApplianceFamilyPieChart .ct-slice-donut').click(function () {
                var $this = $(this);
                var appliance = $this.data("appliance");
                var $popover = $('#ApplianceFamilyPieChart').closest('[data-toggle="popover"]');
                $popover.popover('toggle');
                setTimeout(function(){
                    var $ppvButtons = $popover.siblings('.popover').find("button");
                    $ppvButtons.click(function(){
                        var dic = {appliance:appliance};
                        if (searchParams['catalogue']){
                            dic['catalogue'] = searchParams['catalogue'];
                        }
                        if ($(this).hasClass('btn-refresh-charts')){
                            refresh_with_parameter(dic);
                        } else if ($(this).hasClass('btn-show-parts')){
                            dic['redirection']='part';
                            refresh_with_parameter(dic);
                        }
                    })
                },100)
            });
        });
        
    // END PIE CHART APPLIANCE FAMILY DISTRIB######################################################
    
    
    
    
    
    
    
    
    
    // BAR CHART FOR PART TYPE DISTRIB#####################################################
        var parttype_labels = [];
        for (var i = 0; i<parttype_distrib.length; i++){
            parttype_labels.push(parttype_distrib[i].type__name);
            parttype_distrib[i].value=parttype_distrib[i].count;
        };

        var height = (parttype_distrib.length)*30;
        height += "px";

        var dataViews = {
            labels: parttype_labels,
              series: [parttype_distrib]
        };
        var optionsViews = {
            height: height,
            seriesBarDistance: 10,
            reverseData: true,
            horizontalBars: true,
          classNames: {
            bar: 'ct-bar'
          },
          axisY: {
              offset: 70
          },
          axisX: {
            showGrid: true,
            onlyInteger: true
          },

        };
        var responsiveOptionsViews = [
          ['screen and (max-width: 640px)', {
            seriesBarDistance: 5,
            axisX: {
              labelInterpolationFnc: function (value) {
                return value[0];
              }
            }
          }]
        ];
        var chart_parttype = Chartist.Bar('#partTypeBarChart', dataViews,optionsViews, responsiveOptionsViews);
        chart_parttype.on('draw', function(data) {
            if(data.type === 'bar') {
                // highlight active bar from url parameters
                if (searchParams.parttype == data.series[data.index].type__name){
                    data.element.addClass("active");
                }
                
                data.element.attr({
                  'data-type':"part_type",
                  'data-parttype':data.series[data.index].type__name,
                  'data-toggle':"tooltip",
                  'data-placement':"right",
                  'title':"" + data.element.attr('ct:value'),
                });
            }
        });
        
        chart_parttype.on("created", function () {
            $('#partTypeBarChart .ct-bar').tooltip({
                trigger : 'hover',
                container: '#partTypeBarChartContainer',            
            });
            $('#partTypeBarChart .ct-bar').click(function () {
                var parttype = $(this).data("parttype");
                var $popover = $('#partTypeBarChart').closest('[data-toggle="popover"]');
                $popover.popover('toggle');
                setTimeout(function(){
                    var $ppvButtons = $popover.siblings('.popover').find("button");
                    $ppvButtons.click(function(){
                        var dic = {parttype:parttype};
                        if (searchParams['catalogue']){
                            dic['catalogue'] = searchParams['catalogue'];
                        }
                        if ($(this).hasClass('btn-refresh-charts')){
                            refresh_with_parameter(dic);
                        } else if ($(this).hasClass('btn-show-parts')){
                            dic['redirection'] = 'part';
                            refresh_with_parameter(dic);
                        }
                    })
                },100)
            });
        });
        


        
    // END BAR CHART FOR PART TYPE DISTRIB#####################################################
    
    
    
    
    
});
