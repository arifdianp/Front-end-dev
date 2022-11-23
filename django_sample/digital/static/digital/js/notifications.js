$(document).ready(function(){


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




// NOTIFICATION READ##############################################################
    $('.notification').click(function(){
        var id_notif = $(this).data("notif-id");
        $notif = $(".notification[data-notif-id='" + id_notif + "']");
        console.log("notif id: " + id_notif);
        if (id_notif && $(this).hasClass("new-notif")){
            console.log("ajax-sent");
            $.ajax({
                url: '/digital/notifications/mark-as-read/',
                data:{
                    'id_notif':id_notif,
                },
                dataType:'json',
                success:function(data){
                    if (data.success){
                        console.log("success: " + data.success);
                        $notif.removeClass("new-notif");
                        $notif.find("i.fa-circle").removeClass("fa-circle text-success").addClass("fa-circle-o");
                        var new_count = parseInt($('.notification-count').text()) - 1;
                        $('.notification-count').text(new_count);

                    } else if (data.error){
                        console.log("error: " + data.error);
                    }
                },
                error: function(XMLHttpRequest, textStatus, errorThrown) {
                    console.log("Status: " + textStatus); console.log("Error: " + errorThrown);
                }

            });
        }
    });
// END NOTIFICATION READ##############################################################


});
