
$(document).ready(function(){

    //ON OPEN NOTIFICATIONS ##############################################
    $.notify({
        icon: 'ti-bell',
        message: "SP3D is waiting for you to complete Qualification <b>Step 1</b>."

    },{
        type: 'warning',
        delay:1200,
        timer: 1000,
        showProgressbar:false,
    });
    //END ON OPEN NOTIFICATIONS#############################################




    // QUALIFIFACTION CARD CLICK#########################################
    $(".card-qualif").click(function(){
        $(".card-qualif").removeClass('active');
        $(this).addClass("active");
    });
    //END QUALIFIFACTION CARD CLICK#########################################
});
