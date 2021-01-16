var successCallback = function(data) {

	var checkout_form = $( 'form.woocommerce-checkout' );

	// add a token to our hidden input field
	// console.log(data) to find the token
	checkout_form.find('#btcpyment_token').val(data.token);

	// deactivate the tokenRequest function event
	checkout_form.off( 'checkout_place_order', tokenRequest );

	// submit the form now
	checkout_form.submit();

};

var errorCallback = function(data) {
    console.log(data);
};

var tokenRequest = function() {

	// here will be a payment gateway function that process all the card data from your form,
	// maybe it will need your Publishable API key which is misha_params.publishableKey
	// and fires successCallback() on success and errorCallback on failure
	return false;

};

jQuery(function($){

	var checkout_form = $( 'form.woocommerce-checkout' );
	checkout_form.on( 'checkout_place_order', tokenRequest );

});
