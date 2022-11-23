$(document).ready(function(){


// REFRESH PAGE WHEN CHANGE CATALOGUE//////////////////////////////////////  
    $('select[name="analysis-catalogue"]').change(function(){
        refresh_with_parameter({catalogue:$(this).val()});
    });
// END REFRESH PAGE WHEN CHANGE CATALOGUE//////////////////////////////////////


    
    
    
    


// SHOW/HIDE FILE INPUT TEMPLATE HELP###########################################
    $("#button-upload-file-help,#upload-file-help").click(
        function(){
            $("#upload-file-help").toggle();
        },
    )
        
    
// END SHOW/HIDE FILE INPUT TEMPLATE HELP##########################################
    
    
    
    
    
    
    
    
// UPDATE APPLIANCE PRICES################################################
    $("#form_appliance_details").submit(function(event){
        event.preventDefault();
        var $form = $(this);
        // $form.closest(".modal").modal('hide');
        $form.find('select').prop('disabled', false);
        var $wait_screen = $(".wait-screen");
        var data = new FormData(this);
        $.ajax({
            url: '/digital/analysis/update-appliance-prices/',
            data: data,
            cache: false,
            contentType: false,
            processData: false,
            method: 'POST',
            type: 'POST', // For jQuery < 1.9
            beforeSend:function(XMLHttpRequest, settings){
                // $wait_screen.css("display", "flex");
            },
            success: function(data){
                console.log(data);
                if (data.success){
                    $.notify({
                        icon: 'ti-check',
                        message: "Succesfully Updated"
                    },{
                        type: 'success',
                        timer: 1000,
                        delay: 1000,
                    });
                }else{
                    $.notify({
                        icon: 'ti-face-sad',
                        message: "Update Failed"
                    },{
                        type: 'danger',
                        timer: 1000,
                        delay: 1000,
                    });
                }
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                console.log("Status: " + textStatus); console.log("Error: " + errorThrown);
            },
            complete:function(jqXHR, textStatus){
                $form.find('select').prop('disabled', true);
            },
        });
    });

// END UPLOAD CSV PRINTABILITY PREDICTION################################################
    
    
    
    
    
    
// SHOW ALERTS IF FILTERS ARE APPLIED########################################
    // show warnings if filters here
    if (!isEmpty(searchParams)){
        $('.alert-filters').show();
    };
    var filters_hr = "";
    for (var key in searchParams){
        if (key == 'obsolete' || key == 'longtail' || key == 'shortage' || key == 'pex'){
            filters_hr += key + " | ";
            $('.alert-filters.alert-financial-section').hide();
            $(".tabs-financial-analysis a[href='#" + key + "-parts-analysis']").tab('show');
        }else if (key=='catalogue'){
            filters_hr += key + " | ";
        }else{
            filters_hr += key + ": " + searchParams[key] + " | ";
        }
        
    };
    // add human readalble filters to warning
    $(".filter-hr").text(filters_hr);
    
    
    function isEmpty(obj) {
        for(var key in obj) {
            if(obj.hasOwnProperty(key))
                return false;
        }
        return true;
    }
    
// END SHOW ALERTS IF FILTERS ARE APPLIED########################################







// UPLOAD CSV PRINTABILITY PREDICTION################################################
    $("#form_printability_analysis, #form_financial_analysis").submit(function(event){
        event.preventDefault();
        var $form = $(this);
        $form.closest(".modal").modal('hide');
        var $wait_screen = $(".wait-screen");
        var data = new FormData(this);
        $.ajax({
            url: '/digital/analysis/bulk-part-upload/',
            data: data,
            cache: false,
            contentType: false,
            processData: false,
            method: 'POST',
            type: 'POST', // For jQuery < 1.9
            beforeSend:function(XMLHttpRequest, settings){
                $wait_screen.css("display", "flex");
            },
            success: function(data){
                console.log(data);
                if (data.success){
                    $wait_screen.css("background-color", "rgba(170, 255, 203, 0.7)");
                    setTimeout(function(){refresh_with_parameter({catalogue:data.catalogue})}, 1000);
                }else{
                    $wait_screen.css("background-color", "rgba(255, 207, 207,0.7)");
                }
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                console.log("Status: " + textStatus); console.log("Error: " + errorThrown);
                $wait_screen.css("background-color", "rgba(255, 207, 207,0.7)");
            },
            complete:function(jqXHR, textStatus){
                setTimeout(function(){
                    $wait_screen.css("background-color", "rgba(255, 255, 255,0.7)");
                    $wait_screen.css("display", "none");
                },2000);
            },
        });
    });

// END UPLOAD CSV PRINTABILITY PREDICTION################################################




// CHECK STATUS OF ANALYSIS#####################################################
    if ($("#currently-analysed-part").length !== 0){
        function refreshAnalysisStatus(){
            var current_level = parseInt($("#currently-analysed-part").text());
            $.ajax({
                url: '/digital/analysis/analysis-status/',
                data: {},
                method: 'GET',
                type: 'GET', // For jQuery < 1.9
                beforeSend:function(XMLHttpRequest, settings){
                },
                success: function(data){
                    console.log(data);
                    if (data.analysed_parts){
                        $("#currently-analysed-part").text(data.analysed_parts);
                        if (data.analysed_parts%1100 >= 800 && data.analysed_parts != current_level){
                            location.reload();
                        }
                        // if (data.analysed_parts % 1000 > 600){
                        //     location.reload();
                        // }
                        if (data.finished){
                            location.reload();
                        }
                    }
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    console.log("Status: " + textStatus); console.log("Error: " + errorThrown);
                },
            });
        };
        refreshAnalysisStatus();
        setInterval(function() {
            refreshAnalysisStatus();
        }, 10 * 1000);
    }
// END CHECK STATUS OF ANALYSIS#####################################################





// REFRESH FINANCIAL ANALYSIS######################################################
    $("#refresh-financial").click(function(){
        var $wait_screen = $(".wait-screen");
        var catalogue = searchParams.catalogue ? searchParams.catalogue : null;
        $.ajax({
            url: '/digital/analysis/refresh-financial-analysis/',
            data: {catalogue: catalogue},
            method: 'GET',
            type: 'GET', // For jQuery < 1.9
            beforeSend:function(XMLHttpRequest, settings){
                $wait_screen.css("display", "flex");
            },
            success: function(data){
                console.log(data);
                if (data.success){
                    $wait_screen.css("background-color", "rgba(170, 255, 203, 0.7)");
                    setTimeout(function(){location.reload();}, 1000);
                }else{
                    $wait_screen.css("background-color", "rgba(255, 207, 207,0.7)");
                }
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                console.log("Status: " + textStatus); console.log("Error: " + errorThrown);
                $wait_screen.css("background-color", "rgba(255, 207, 207,0.7)");
            },
            complete:function(jqXHR, textStatus){
                setTimeout(function(){
                    $wait_screen.css("background-color", "rgba(255, 255, 255,0.7)");
                    $wait_screen.css("display", "none");
                },2000);
            },
        });
    });
// END REFRESH FINANCIAL ANALYSIS######################################################








// EXPORT ANALYSIS######################################################
    $(".export-analysis").click(function(){
        var $wait_screen = $(".wait-screen");
        var catalogue = searchParams.catalogue ? searchParams.catalogue : "";
        $.ajax({
            url: '/digital/analysis/export-analysis/',
            data: {catalogue:catalogue},
            method: 'GET',
            type: 'GET', // For jQuery < 1.9
            beforeSend:function(XMLHttpRequest, settings){
                $wait_screen.css("display", "flex");
            },
            success: function(data){
                console.log(data);
                if (data.success){
                    $wait_screen.css("background-color", "rgba(170, 255, 203, 0.7)");
                    saveFile(data.file);
                }else{
                    $wait_screen.css("background-color", "rgba(255, 207, 207,0.7)");
                }
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                console.log("Status: " + textStatus); console.log("Error: " + errorThrown);
                $wait_screen.css("background-color", "rgba(255, 207, 207,0.7)");
            },
            complete:function(jqXHR, textStatus){
                setTimeout(function(){
                    $wait_screen.css("background-color", "rgba(255, 255, 255,0.7)");
                    $wait_screen.css("display", "none");
                },2000);
            },
        });
    });
    
    function saveFile(url) {
        // Get file name from url.
        var filename = url.substring(url.lastIndexOf("/") + 1).split("?")[0];
        var xhr = new XMLHttpRequest();
        xhr.responseType = 'blob';
        xhr.onload = function() {
            var a = document.createElement('a');
            a.href = window.URL.createObjectURL(xhr.response); // xhr.response is a blob
            a.download = filename; // Set the file name.
            a.style.display = 'none';
            document.body.appendChild(a);
            a.click();
            delete a;
        };
        xhr.open('GET', url);
        xhr.send();
    }
// END EXPORT ANALYSIS######################################################






// POPOVERS############################################################
    
    $('.indicator [data-toggle="popover"]').each(function(){
        var parameter = ($(this).data("parameter") ? $(this).data("parameter") : "#");
        $(this).popover(
            {template: '<div class="popover">\
                            <div class="arrow"></div>\
                            <h3 class="popover-title"></h3>\
                            <a href="' + parameter + '"><button class="btn btn-sm btn-success btn-refresh-charts" style="display:block;">refresh charts</button></a>\
                            <a href="' + parameter + '&redirection=parts"><button class="btn btn-sm btn-info btn-show-parts" style="display:block;">show parts</button></a>\
                            <div class="popover-content" style="display:none;">\
                            </div>\
                        </div>'
            }
        );
    });
    
    function InitChartPopover(chartID){
        $('#' + chartID).closest('[data-toggle="popover"]').popover({
            template: '<div class="popover">\
                            <div class="arrow"></div>\
                            <h3 class="popover-title"></h3>\
                            <button class="btn btn-sm btn-success btn-refresh-charts" style="display:block;">refresh charts</button>\
                            <button class="btn btn-sm btn-info btn-show-parts" style="display:block;">show parts</button>\
                            <div class="popover-content" style="display:none;">\
                            </div>\
                        </div>'
        });
    };

// END POPOVERS############################################################




// FINANCIAL ANALYSIS: HANDLE TYPE CHANGE######################################################
    $('.analysis-type').click(function(){
        $('[type="radio"][name="analysis-type"][value="' + $(this).data("value") + '"]').prop('checked', true);
    });
// END FINANCIAL ANALYSIS: HANDLE TYPE CHANGE######################################################




// YEARLY ANALYSIS################################################
    $("#form_yearly_margin").submit(function(event){
        event.preventDefault();
        var $form = $(this);
        var $wait_screen = $(".wait-screen");
        var data = new FormData(this);
        if (searchParams.catalogue){
            data.append('catalogue',searchParams.catalogue);
        }
        $.ajax({
            url: '/digital/analysis/yearly-margin-analysis/?' + window.location.search.substring(1),
            data: data,
            cache: false,
            contentType: false,
            processData: false,
            method: 'POST',
            type: 'POST', // For jQuery < 1.9
            beforeSend:function(XMLHttpRequest, settings){
                $wait_screen.css("display", "flex");
            },
            success: function(data){
                console.log(data);
                if (data.success){
                    $wait_screen.css("background-color", "rgba(170, 255, 203, 0.7)");
                    fillYearlyMarginChart(data.yearly_margin_list, data.currency);
                    // fill5yMargin(data.yearly_margin_list);
                    // setTimeout(function(){location.reload();}, 1000);
                }else{
                    $wait_screen.css("background-color", "rgba(255, 207, 207,0.7)");
                }
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                console.log("Status: " + textStatus); console.log("Error: " + errorThrown);
                $wait_screen.css("background-color", "rgba(255, 207, 207,0.7)");
            },
            complete:function(jqXHR, textStatus){
                setTimeout(function(){
                    $wait_screen.css("background-color", "rgba(255, 255, 255,0.7)");
                    $wait_screen.css("display", "none");
                },2000);
            },
        });
    });


    function fillYearlyMarginChart(yearly_margin_list, currency){
        var N = yearly_margin_list.length;
        var year_labels = Array.apply(null, {length: N}).map(function(value, index){return index + 1;});
        var serie = yearly_margin_list.map(function(value){return value / 1000;});
        var dataViews = {
            labels: year_labels,
            series: [serie]
        };
        var optionsViews = {
            height: '250px',
            seriesBarDistance: 10,
          classNames: {
            bar: 'ct-bar bar-green'
          },
          axisY: {
              offset: 70
          },
          axisX: {
            showGrid: true,
            onlyInteger: true
          },

        };
        var chart_yearlymargin = Chartist.Bar('#yearlyMarginBarChart', dataViews,optionsViews, responsiveOptionsViews);
        $("#yearlyMarginBarChart").show();
        chart_yearlymargin.on('draw', function(data) {
            if(data.type === 'bar') {
                data.element.attr({
                  'data-toggle':"tooltip",
                  'data-placement':"top",
                  'title':"" + parseFloat(data.element.attr('ct:value')).toFixed(0) + " k",
                });
            } 
        });
        
        chart_yearlymargin.on("created", function () {
            $('#yearlyMarginBarChart .ct-bar').tooltip({
                trigger : 'hover',
                container: '#yearlyMarginBarChartContainer',            
            });
        });
        $('#yearlyMarginBarChart').attr('data-y-axis','k' + currency);
        

    };
    
    function fill5yMargin(yearly_margin_list){
        
        var sum = yearly_margin_list.reduce(add,0);
        $('#margin_5y .result').text(numberWithCommas(Math.round(sum)) + " $");
    }
    function add(a, b) {
        return a + b;
    }
    const numberWithCommas = function(x){
        var parts = x.toString().split(".");
        parts[0] = parts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
        return parts.join(".");
    }


// YEARLY ANALYSIS################################################











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
    
    InitChartPopover("partTypeBarChart");


    
// END BAR CHART FOR PART TYPE DISTRIB#####################################################








// BAR CHART FOR TECHNOMATERIAL DISTRIB#####################################################
    var technomaterial_labels = [];
    for (var i = 0; i<techno_material_distrib.length; i++){
        technomaterial_labels.push(techno_material_distrib[i].final_card__techno_material__technology__name + " + " + techno_material_distrib[i].final_card__techno_material__material__name);
        techno_material_distrib[i].value = techno_material_distrib[i].count;
    };
    var dataViews = {
        labels: technomaterial_labels,
          series: [
             techno_material_distrib
          ]
    };
    var optionsViews = {
        height: "250px",
        seriesBarDistance: 10,
        reverseData: true,
        horizontalBars: true,
      classNames: {
        bar: 'ct-bar bar-red'
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
    var chart_technomaterial = Chartist.Bar('#TechnoMaterialDistrib', dataViews,optionsViews, responsiveOptionsViews);
    chart_technomaterial.on('draw', function(data) {
        if(data.type === 'bar') {
            // highlight active bar from url parameters
            if (searchParams.technology == data.series[data.index].final_card__techno_material__technology__name
            && searchParams.material == data.series[data.index].final_card__techno_material__material__name){
                data.element.addClass("active");
            }
            data.element.attr({
              'data-type':"techno_material",
              'data-technology':data.series[data.index].final_card__techno_material__technology__name,
              'data-material':data.series[data.index].final_card__techno_material__material__name,
              'data-toggle':"tooltip",
              'data-placement':"right",
              'title':"" + data.element.attr('ct:value'),
            });
        } 
    });
    
    chart_technomaterial.on("created", function () {
        $('#TechnoMaterialDistrib .ct-bar').tooltip({
            trigger : 'hover',
            container: '#TechnoMaterialDistribContainer',            
        });
        $('#TechnoMaterialDistrib .ct-bar').click(function () {
            var technology = $(this).data("technology");
            var material = $(this).data("material");
            var $popover = $('#TechnoMaterialDistrib').closest('[data-toggle="popover"]');
            $popover.popover('toggle');
            setTimeout(function(){
                var $ppvButtons = $popover.siblings('.popover').find("button");
                $ppvButtons.click(function(){
                    var dic = {technology:technology, material:material};
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
    
    InitChartPopover("TechnoMaterialDistrib");
// END BAR CHART FOR PART TYPE DISTRIB#####################################################







// PIE CHART APPLIANCE FAMILY DISTRIB######################################################
    
    var app_fam_labels = [];
    var serie = [];
    if (total_parts == 0){total_parts=1};//safety
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
    
    InitChartPopover("ApplianceFamilyPieChart");
// END PIE CHART APPLIANCE FAMILY DISTRIB######################################################







    // URL PARAMETER REDIRECTION////////////////////////////////////////
    function refresh_with_parameter(params){
        showWaitScreen(); //NOT WORKING
        $('.wait-screen').css('display','flex');//NOT WORKING
        
        var printable = "&printable=" + searchParams.printable;
        var restock = "&restock=" + searchParams.restock;
        var appliance = "";
        var parttype = "";
        var technology = "";
        var material = "";
        var redirection = "";
        var catalogue = "&catalogue=" + searchParams.catalogue;
        
        for (var param_name in params){
            value = params[param_name];
            if (param_name == 'appliance'){
                appliance = "&appliance=" + value;
            } else if (param_name == "parttype") {
                parttype = "&parttype=" + value;
            } else if (param_name == "technology") {
                technology = "&technology=" + value;
            } else if (param_name == "material") {
                material = "&material=" + value;
            } else if (param_name == "redirection") {
                redirection = "&redirection=" + value;
            } else if (param_name == "catalogue") {
                catalogue = "&catalogue=" + value;
            }
        }

        var params_list = [printable, restock, appliance, parttype, technology, material, redirection, catalogue]
        var param_string=""
        for (var i in params_list) {
            console.log(params_list[i]);
            console.log(!params_list[i].match(/undefined/));
            if (!params_list[i].match(/null/) && !params_list[i].match(/undefined/) && params_list[i]){
                param_string += params_list[i];
            }
        };
        console.log("params:" + param_string);
        console.log( window.location.pathname + "?" + param_string);
        document.location.href = window.location.pathname + "?" + param_string;
    }
});
