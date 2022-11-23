(function($) {

    // $('#paralax-container').hover(function(){
    //     $('#carousel').css('background-position', '10px 10px');
    // }, function(){
    //     $('#carousel').css('background-position', '');
    // });
    if ($( ".parallax-container" ).length){
        var temp=$(".parallax-container").css('background-position').split(" ");
        var backgroundX = parseFloat(temp[0].replace("%",""));
        var backgroundY = parseFloat(temp[1].replace("%",""));
        var screenHeight = screen.height ;
        var pl_step = 0.1;
        var scrollTop = $(window).scrollTop();
        var newY = backgroundY;
        $(window).on('scroll', {
            previousTop: 0
          },
          function() {
            // var currentTop = $(window).scrollTop();
            // //check if user is scrolling up
            // if (currentTop < this.previousTop) {
            //   //if scrolling up...
            //   if (currentTop > 0 && $('#mainNav').hasClass('is-fixed')) {
            //     $('#mainNav').addClass('is-visible');
            //   } else {
            //     $('#mainNav').removeClass('is-visible is-fixed');
            //   }
            // } else if (currentTop > this.previousTop) {
            //   //if scrolling down...
            //   $('#mainNav').removeClass('is-visible');
            //   if (currentTop > headerHeight && !$('#mainNav').hasClass('is-fixed')) $('#mainNav').addClass('is-fixed');
            // }
            // this.previousTop = currentTop;
            scrollTop = $(this).scrollTop();
            newY = backgroundY + 10*(scrollTop/screenHeight);

            // console.log("newx" + backgroundX);
            // console.log("newy" + newY);

            $(".parallax-container").css('background-position', backgroundX + "% " + newY + "%" );
            // console.log(scrollTop);
        });
    };
})(jQuery);
