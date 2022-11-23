$(document).ready(function(){

// INIT MAP
// initmap for google maps###################################################
    function initMap(lat,lng){
        var myLatlng = new google.maps.LatLng(lat,lng);
        var mapOptions = {
          zoom: 13,
          center: myLatlng,
          scrollwheel: false, //we disable de scroll over the map, it is a really annoing when you scroll through page
          styles: [{"featureType":"water","stylers":[{"saturation":43},{"lightness":-11},{"hue":"#0088ff"}]},{"featureType":"road","elementType":"geometry.fill","stylers":[{"hue":"#ff0000"},{"saturation":-100},{"lightness":99}]},{"featureType":"road","elementType":"geometry.stroke","stylers":[{"color":"#808080"},{"lightness":54}]},{"featureType":"landscape.man_made","elementType":"geometry.fill","stylers":[{"color":"#ece2d9"}]},{"featureType":"poi.park","elementType":"geometry.fill","stylers":[{"color":"#ccdca1"}]},{"featureType":"road","elementType":"labels.text.fill","stylers":[{"color":"#767676"}]},{"featureType":"road","elementType":"labels.text.stroke","stylers":[{"color":"#ffffff"}]},{"featureType":"poi","stylers":[{"visibility":"off"}]},{"featureType":"landscape.natural","elementType":"geometry.fill","stylers":[{"visibility":"on"},{"color":"#b8cb93"}]},{"featureType":"poi.park","stylers":[{"visibility":"on"}]},{"featureType":"poi.sports_complex","stylers":[{"visibility":"on"}]},{"featureType":"poi.medical","stylers":[{"visibility":"on"}]},{"featureType":"poi.business","stylers":[{"visibility":"simplified"}]}]

        }
        var map = new google.maps.Map(document.getElementById("map"), mapOptions);

        var marker = new google.maps.Marker({
            position: myLatlng,
            title:"Company !"
        });

        // To add the marker to the map, call setMap();
        marker.setMap(map);
    };
    // end init map #########################################################3
    if (!is_admin && (typeof latitude_org !== 'undefined') && (typeof longitude_org !== 'undefined') && (parseFloat(latitude_org)!=='NaN') && (parseFloat(longitude_org)!=='NaN')){
        console.log(longitude_org);
        console.log(latitude_org);
        initMap(latitude_org, longitude_org);
    };
// END INIT MAP







// UPLOAD PROFILE PICTURE###########################################################

    $("#profile_pic_form").dropzone({
        url: "/digital/account/upload-profile-pic/",
        paramName: "profile_pic", // The name that will be used to transfer the file
        maxFiles: 1,
        maxFilesize: 2, // MB
        createImageThumbnails: false,
        clickable: true,
        acceptedFiles:".png,.jpg,.gif",
        accept: function(file, done) {
            if (file.name == "justin.jpg") {
              done("Naha, you don't.");
            }
            else { done(); }
        },
        init: function () {
            var $form = $("#profile_pic_form");
            this.on("sending", function(file, xhr, formData) {
            //    formData.append("csrfmiddlewaretoken", csrftoken);
                $form.find(".progressBar-inner").css("background-color","#6dbad8");
                $form.find(".progressBar").css("opacity",1);
                $form.find(".remove-file").removeClass("visible");
            });
            this.on('uploadprogress',function(file, progress, bytesSent){
                $form.find(".progressBar-inner").css("width", progress + "%");
            });
            this.on('complete', function () {
                setTimeout(function(){$form.find(".progressBar").css("opacity",0)}, 1000);
                setTimeout(function(){$form.find(".progressBar-inner").css("width","0%")}, 1200);
            });
            this.on("success", function(file, response) {
                console.log(response);
                $('#modalProfilePic').modal('hide');
                if (response.success){
                    $form.find(".progressBar-inner").css("background-color","green");
                    $('.user-pic,.user .avatar').css('background-image', "url(" + response.thumbnail + ")");
                } else {
                    $form.find(".progressBar-inner").css("background-color","red");
                    $.notify({
                        icon: 'ti-face-sad',
                        message: "Picture Upload failed"
                    },{
                        type: 'danger',
                        timer: 1000,
                        delay: 1000,
                    });
                };
            });
        },
        error:function(file, response){
            console.log(response);
            $('#modalProfilePic').modal('hide');
            $("#profile_pic_form").find(".progressBar-inner").css("background-color","red");
            $.notify({
                icon: 'ti-face-sad',
                message: "Picture Upload failed"
            },{
                type: 'danger',
                timer: 1000,
                delay: 1000,
            });
        },
    });

    $("#modalProfilePic .modal-body").click(function(){
        $(this).closest(".dropzone").click();
    });


// END UPLOAD PROFILE PICTURE###########################################################




// UPLOAD COMPANY LOGO###########################################################

    $("#company_logo_form").dropzone({
        url: "/digital/account/upload-company-logo/",
        paramName: "logo", // The name that will be used to transfer the file
        maxFiles: 1,
        maxFilesize: 2, // MB
        createImageThumbnails: false,
        clickable: true,
        acceptedFiles:".png,.jpg,.gif",
        accept: function(file, done) {
            if (file.name == "justin.jpg") {
              done("Naha, you don't.");
            }
            else { done(); }
        },
        init: function () {
            var $form = $("#company_logo_form");
            this.on("sending", function(file, xhr, formData) {
            //    formData.append("csrfmiddlewaretoken", csrftoken);
                $form.find(".progressBar-inner").css("background-color","#6dbad8");
                $form.find(".progressBar").css("opacity",1);
                $form.find(".remove-file").removeClass("visible");
            });
            this.on('uploadprogress',function(file, progress, bytesSent){
                $form.find(".progressBar-inner").css("width", progress + "%");
            });
            this.on('complete', function () {
                setTimeout(function(){$form.find(".progressBar").css("opacity",0)}, 1000);
                setTimeout(function(){$form.find(".progressBar-inner").css("width","0%")}, 1200);
            });
            this.on("success", function(file, response) {
                console.log(response);
                $('#modalCompanyLogo').modal('hide');
                if (response.success){
                    $form.find(".progressBar-inner").css("background-color","green");
                    $(".organisation-logo").find("img").attr("src", response.thumbnail);
                    $('.logo-company-container').css('background-image', "url(" + response.thumbnail + ")");
                } else {
                    $form.find(".progressBar-inner").css("background-color","red");
                    $.notify({
                        icon: 'ti-face-sad',
                        message: "Picture Upload failed"
                    },{
                        type: 'danger',
                        timer: 1000,
                        delay: 1000,
                    });
                };
            });
        },
        error:function(file, response){
            console.log(response);
            $('#modalCompanyLogo').modal('hide');
            $("#company_logo_form").find(".progressBar-inner").css("background-color","red");
            $.notify({
                icon: 'ti-face-sad',
                message: "Picture Upload failed"
            },{
                type: 'danger',
                timer: 1000,
                delay: 1000,
            });
        },
    });

    $("#modalCompanyLogo .modal-body").click(function(){
        $(this).closest(".dropzone").click();
    });


// END UPLOAD COMPANY LOGO###########################################################





// UPDATE USER DATA###########################################################
    $("#form-update-profile").submit(function(event){
        event.preventDefault();
        var $form = $(this);
        var data = new FormData(this);
        // console.log("received");
        $.ajax({
            url: '/digital/account/update-profile/',
            data: data,
            cache: false,
            contentType: false,
            processData: false,
            method: 'POST',
            type: 'POST', // For jQuery < 1.9
            beforeSend:function(XMLHttpRequest, settings){
                // $form.find(".progressBar-inner").css("background-color","blue");
                // $form.find(".progressBar").css("opacity",1);
            },
            xhr: function() {
                var myXhr = $.ajaxSettings.xhr();
                if(myXhr.upload){
                    // myXhr.upload.addEventListener('progress',uploadProgress, false);
                }
                return myXhr;
            },
            success: function(data){
                console.log(data);
                if (data.success){
                    $.notify({
                        icon: 'ti-check',
                        message: "Profile updated successfully"
                    },{
                        type: 'success',
                        timer: 1000,
                        delay: 1000,
                    });
                } else {
                    $.notify({
                        icon: 'ti-face-sad',
                        message: "Sorry, update failed"
                    },{
                        type: 'danger',
                        timer: 1000,
                        delay: 1000,
                    });
                }
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                $.notify({
                    icon: 'ti-face-sad',
                    message: "Sorry, update failed"
                },{
                    type: 'danger',
                    timer: 1000,
                    delay: 1000,
                });
                console.log("Status: " + textStatus); console.log("Error: " + errorThrown);
            },
            complete:function(jqXHR, textStatus){
                // setTimeout(function(){$form.find(".progressBar").css("opacity",0)}, 1000);
                // setTimeout(function(){$form.find(".progressBar-inner").css("width","0%")}, 1200);
            },

        });
    });
// END UPDATE USER DATA###########################################################




// UPDATE COMPANY DATA###########################################################
    $("#form-update-company").submit(function(event){
        event.preventDefault();
        var $form = $(this);
        var data = new FormData(this);
        console.log(data);
        // console.log("received");
        $.ajax({
            url: '/digital/account/update-organisation/',
            data: data,
            cache: false,
            contentType: false,
            processData: false,
            method: 'POST',
            type: 'POST', // For jQuery < 1.9
            beforeSend:function(XMLHttpRequest, settings){
                // $form.find(".progressBar-inner").css("background-color","blue");
                // $form.find(".progressBar").css("opacity",1);
            },
            xhr: function() {
                var myXhr = $.ajaxSettings.xhr();
                if(myXhr.upload){
                    // myXhr.upload.addEventListener('progress',uploadProgress, false);
                }
                return myXhr;
            },
            success: function(data){
                console.log(data);
                if (data.success){
                    $.notify({
                        icon: 'ti-check',
                        message: "Organisation updated successfully"
                    },{
                        type: 'success',
                        timer: 1000,
                        delay: 1000,
                    });
                } else {
                    $.notify({
                        icon: 'ti-face-sad',
                        message: "Sorry, update failed"
                    },{
                        type: 'danger',
                        timer: 1000,
                        delay: 1000,
                    });
                }
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) {
                $.notify({
                    icon: 'ti-face-sad',
                    message: "Sorry, update failed"
                },{
                    type: 'danger',
                    timer: 1000,
                    delay: 1000,
                });
                console.log("Status: " + textStatus); console.log("Error: " + errorThrown);
            },
            complete:function(jqXHR, textStatus){
                // setTimeout(function(){$form.find(".progressBar").css("opacity",0)}, 1000);
                // setTimeout(function(){$form.find(".progressBar-inner").css("width","0%")}, 1200);
            },

        });
    });
// END UPDATE COMPANY DATA###########################################################







// SEND NOTIFICATION TO TEAM MEMBER##########################################################
    $(".btn-notif-team").click(function(){
        $("#form_notification").find("input[name='notif-verb']").attr("value",$(this).data("verb"));
        $("#form_notification").find("input[name='notif-recipient']").attr("value",$(this).data("recipient"));
    });
    $("#form_notification").submit(function(event){
        event.preventDefault();
        var $modal = $(this).closest(".modal");
        var $form = $(this);
        var id_recipient = $form.find("input[name='notif-recipient']").val();
        var verb = $form.find("input[name='notif-verb']").val();
        console.log(id_recipient);
        console.log(verb);
        if (id_recipient && verb){
            var data = new FormData(this);
            // console.log("received");
            $.ajax({
                url: '/digital/notifications/team-notification/',
                data: data,
                cache: false,
                contentType: false,
                processData: false,
                method: 'POST',
                type: 'POST', // For jQuery < 1.9
                beforeSend:function(XMLHttpRequest, settings){
                },
                success: function(data){
                    console.log(data);
                    if (data.success){
                        $.notify({
                            icon: 'ti-check',
                            message: "Message Sent"
                        },{
                            type: 'success',
                            timer: 1000,
                            delay: 1000,
                        });
                    } else {
                        $.notify({
                            icon: 'ti-face-sad',
                            message: "Sorry, message failed"
                        },{
                            type: 'danger',
                            timer: 1000,
                            delay: 1000,
                        });
                    }
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    $.notify({
                        icon: 'ti-face-sad',
                        message: "Sorry, update failed"
                    },{
                        type: 'danger',
                        timer: 1000,
                        delay: 1000,
                    });
                    console.log("Status: " + textStatus); console.log("Error: " + errorThrown);
                },
                complete:function(jqXHR, textStatus){
                    $form.find("input[name='notif-recipient']").val("");
                    $form.find("input[name='notif-description']").val("");
                    $modal.modal('hide');
                },
            });
        };
    });


    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
// END SEND NOTIFICATION TO TEAM MEMBER###########################################################

});
