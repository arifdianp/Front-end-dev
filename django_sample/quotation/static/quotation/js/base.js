(function($) {
    /////////////////////////////////////////////SET DJ FABSTER WHEN FINISHED LOADING///////////////////////////////

    jQuery(window).ready(function () {
        // alert('page is loaded');

        setTimeout(function () {
            // alert('page is loaded and 1s  has passed');
            $("#df-widget-btn-text span").text("Get a Quote !");
            $("#df-widget-btn").addClass("hidden-xs-down");
            $("#df-widget-btn-circle").css("background-color","rgb(196,50,53)");

        }, 100);

    });
    /////////////////////////////////////////////NAVBAR EFFECT////////////////////////////////////////////////////////

  // Show the navbar when the page is scrolled up
  var MQL = 992;

  //primary navigation slide-in effect
  if ($(window).width() > MQL) {
    var headerHeight = $('#mainNav').height();
    $(window).on('scroll', {
        previousTop: 0
      },
      function() {
        var currentTop = $(window).scrollTop();
        //check if user is scrolling up
        if (currentTop < this.previousTop) {
          //if scrolling up...
          if (currentTop > 0 && $('#mainNav').hasClass('is-fixed')) {
            $('#mainNav').addClass('is-visible');
          } else {
            $('#mainNav').removeClass('is-visible is-fixed');
          }
        } else if (currentTop > this.previousTop) {
          //if scrolling down...
          $('#mainNav').removeClass('is-visible');
          if (currentTop > headerHeight && !$('#mainNav').hasClass('is-fixed')) $('#mainNav').addClass('is-fixed');
        }
        this.previousTop = currentTop;
      });
  }
 ////////////////////////////////////////////MARGIN CHANGE ON RESIZE/////////////////////////////////////////////////////////////////

    // initialize isMarged
    if ($(window).width()>= MQL){
        var isMarged_init = true;
    } else {
        var isMarged_init = false;
    }
    // on resize listener
    $( window ).resize({isMarged : isMarged_init},function() {
        if ($(window).width() < MQL && this.isMarged) {
            $("#mainNav").removeClass('is-marged');
            this.isMarged = false;
        }
        else if ($(window).width() >= MQL && !this.isMarged){
            $("#mainNav").addClass('is-marged');
            this.isMarged = true;
        }
    });

//////////////////////////////////////////////////////TECHNO CARDS EFFECTS/////////////////////////////////////////////////////////////////////
    $(".techno-card").hover(
        function(){
            var $this = $(this);
            $this.find(".card-block").css("padding","1.25rem 1.25rem 1.25rem 1.25rem");
            var longTitle = $this.find(".card-title").data("long-title");
            $this.find(".card-title").text(longTitle);
            $this.find(".card-img-top").css("opacity", "0");
            $this.find(".card-img-bottom").css("opacity", "1");
            $this.find(".btn").show();
        },
        function(){
            var $this = $(this);
            $this.find(".card-block").css("padding","0.5rem 1.25rem 0.5rem 1.25rem");
            var shortTitle = $this.find(".card-title").data("short-title");
            $this.find(".card-title").text(shortTitle);
            $this.find(".card-img-top").css("opacity", "1");
            $this.find(".card-img-bottom").css("opacity", "0");
            $this.find(".btn").hide();
            });


/////////////////////////////////////////////////////////SERVICE CARDS EFFECT/////////////////////////////////////////////////////////////

    $(".service-card").hover(
        function(){
            var $this = $(this);
            $this.find(".card-block").removeClass("parked").addClass("unparked");
            $this.addClass("sc-zoomed-in");
            // $this.find(".card-block").css("height","100%");
            // $this.find(".card-block").css('background', convertHex('#8c2325', 65));
            // $this.css("background-size","auto 115%");
        },
        function(){
            var $this = $(this);
            $this.find(".card-block").removeClass("unparked").addClass("parked");
            $this.removeClass("sc-zoomed-in");
            // $this.find(".card-block").css("height","25%");
            // $this.find(".card-block").css('background', convertHex('#c43235', 90));
            // $this.css("background-size","auto 100%");
            });

/////////////////////////////////////////////////////////MATERIAL CARDS EFFECT/////////////////////////////////////////////////////////////

    $(".material-card").hover(
        function(){
            var $this = $(this);
            $this.find(".card-block").removeClass("parked").addClass("unparked");
            $this.addClass("mc-zoomed-in");
            // $this.find(".card-block").css("left","0%");
            // $this.find(".card-block").css('background', convertHex('#c43235', 75));
            // $this.find(".card-block").css("color","#ffffff");
            // $this.css("background-size","auto 120%");
        },
        function(){
            var $this = $(this);
            $this.find(".card-block").removeClass("unparked").addClass("parked");
            $this.removeClass("mc-zoomed-in");
            // $this.find(".card-block").css("left","50%");
            // $this.find(".card-block").css("background-color",convertHex('#00000', 0));
            // $this.find(".card-block").css("color","#300032");
            // $this.css("background-size","auto 100%");
        });

    function convertHex(hex,opacity){
        hex = hex.replace('#','');
        r = parseInt(hex.substring(0,2), 16);
        g = parseInt(hex.substring(2,4), 16);
        b = parseInt(hex.substring(4,6), 16);
        result = 'rgba('+r+','+g+','+b+','+opacity/100+')';
        return result;
        }
////////////////////////////////////////////FOR QUOTE HANDLING///////////////////////////////////////////////

    $("#contact-us-banner").click(function(){
        $('input:radio[name="request-type"][value="contact"]').closest(".btn").click();
    });

    $('input:radio[name="request-type"]').change(
        function(){
            $(".quote-form").find(".form-group").hide();
            if ($(this).is(':checked') && $(this).val() == 'prototype') {
                $(".quote-form").find(".f-g-all").show();
                $(".quote-form").find(".f-g-prototype").show();
            } else if ($(this).is(':checked') && $(this).val() == 'service') {
                $(".quote-form").find(".f-g-all").show();
                $(".quote-form").find(".f-g-service").show();
            } else if ($(this).is(':checked') && $(this).val() == 'contact') {
                $(".quote-form").find(".f-g-all").show();
                $(".quote-form").find(".f-g-contact-email").show();
            }

        });
    // initialiaze state service on form
    if (typeof form_section !== 'undefined' && form_section){
        if (form_section=='contact'){
            $('input:radio[name="request-type"][value="contact"]').closest(".btn").click();
        } else if (form_section=='service'){
            $('input:radio[name="request-type"][value="service"]').closest(".btn").click();
        } else if (form_section=='prototype'){
            $('input:radio[name="request-type"][value="prototype"]').closest(".btn").click();
        };
    };
    // initialiaze state techno on form
    if (typeof form_techno !== 'undefined' && form_techno){
        if (form_techno=='40_fdm'){
            $('#fmd_live_quote_btn').click();
        };
    };
    // HANDLE SUCCESS
    if (typeof request_success !== 'undefined' && request_success){
        var counter = 6;
        var interval = setInterval(function() {
            counter--;
            $(".timer").text(counter);
            if (counter == 0) {
                $("#request-success").css('display','none');
                $("#quotation-container").show();
                clearInterval(interval);
            }
        }, 1000);

    }

    // validate form
    var fileInput = $('.size-check');
    var maxSize = fileInput.data('max-size');
    $('#quote-form-global').submit(function(e){
        console.log("CHECKING SIZE");
        console.log(fileInput);
        var form_files = fileInput.get(0).files;
        var fileSize = 0;
        if(form_files.length){
            for (var i = 0; i < form_files.length; i++) {
                fileSize += form_files[i].size
            }
            if(fileSize>maxSize){
                alert('file size is more than' + maxSize + ' bytes, or 100MB');
                // alert('total file is more than' + maxSize + ' bytes');
                return false;
            }else{
               console.log('file size is correct- '+fileSize+' bytes');
               $(".loading-wheel").show();
               console.log("file size passes test");
            }
        }else{
            $(".loading-wheel").show();
        //    alert('choose file, please');
        //    return false;
        }
    });



})(jQuery);
