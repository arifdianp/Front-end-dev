$(function(){
    $('input.address').each(function(){
        var self = $(this);
	    var cmps = $('#' + self.attr('name') + '_components');
	    var fmtd = $('input[name="' + self.attr('name') + '_formatted"]');
        self.val(address_org);
        self.keydown(function(){self.closest("form").find("button[type='submit']").attr("disabled", '')});
        self.geocomplete({
            map: "#map",
            mapOptions: {
                zoom: 10
            },
            markerOptions: {
                draggable: false
            },
            details: cmps,
            detailsAttribute: 'data-geo'
        }).change(function(){
            if(self.val() != fmtd.val()) {
        	var cmp_names = ['country', 'country_code', 'locality', 'postal_code',
        			 'route', 'street_number', 'state', 'state_code',
        			 'formatted', 'latitude', 'longitude'];
        	for(var ii = 0; ii < cmp_names.length; ++ii)
        	    $('input[name="' + self.attr('name') + '_' + cmp_names[ii] + '"]').val('');
            }
	    }).bind("geocode:result", function(event, result){
            self.closest("form").find("button[type='submit']").removeAttr('disabled');
            var state_input = self.closest("form").find('input[name="'+ self.attr('name') +'_state"]');
            var state_code_input = self.closest("form").find('input[name="'+ self.attr('name') +'_state_code"]');
            if (!state_input.val() || !state_code_input.val()){
                state_input.attr("value", "N/A");
                state_code_input.attr("value", "N/A");
            };
            console.log("result");
        });
        self.geocomplete("find", address_org);
    });
});
