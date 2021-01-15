<?php
/*
 * Plugin Name: BTCPyment
 * Plugin URI: https://github.com/nickfarrow/BTCPyment
 * Description: Take credit card payments on your store.
 * Author: Nick Farrow
 * Author URI: https://nickfarrow.com
 * Version: 1.0.1
 *
*/

/* Based on https://rudrastyh.com/woocommerce/payment-gateway-plugin.html */

/*
 * This action hook registers our PHP class as a WooCommerce payment gateway
 */

 if (!function_exists('write_log')) {
     function write_log($log) {
         if (true === WP_DEBUG) {
             if (is_array($log) || is_object($log)) {
                 error_log(print_r($log, true));
             } else {
                 error_log($log);
             }
         }
     }

 }

add_filter( 'woocommerce_payment_gateways', 'btcpyment_add_gateway_class' );
function btcpyment_add_gateway_class( $gateways ) {
	$gateways[] = 'WC_Btcpyment_Gateway'; // your class name is here
	return $gateways;
}

/*
 * The class itself, please note that it is inside plugins_loaded action hook
 */
add_action( 'plugins_loaded', 'btcpyment_init_gateway_class' );
function btcpyment_init_gateway_class() {

	class WC_Btcpyment_Gateway extends WC_Payment_Gateway {

 		/**
 		 * Class constructor, more about it in Step 3
 		 */
 		public function __construct() {

           	$this->id = 'BTCPyment'; // payment gateway plugin ID
           	$this->icon = ''; // URL of the icon that will be displayed on checkout page near your gateway name
           	$this->has_fields = true; // in case you need a custom credit card form
           	$this->method_title = 'BTCPyment Gateway';
           	$this->method_description = 'Description of btcpyment payment gateway'; // will be displayed on the options page

           	// gateways can support subscriptions, refunds, saved payment methods,
           	// but in this tutorial we begin with simple payments
           	$this->supports = array(
           		'products'
           	);

           	// Method with all the options fields
           	$this->init_form_fields();

           	// Load the settings.
           	$this->init_settings();
           	$this->title = $this->get_option( 'title' );
           	$this->description = $this->get_option( 'description' );
           	$this->enabled = $this->get_option( 'enabled' );
            $this->btcpyment_server_url = $this->get_option( 'btcpyment_server_url' );
            $this->redirect_url = $this->get_option( 'redirect_url' );
           	$this->testmode = 'yes' === $this->get_option( 'testmode' );
           	$this->private_key = $this->testmode ? $this->get_option( 'test_private_key' ) : $this->get_option( 'private_key' );
           	$this->publishable_key = $this->testmode ? $this->get_option( 'test_publishable_key' ) : $this->get_option( 'publishable_key' );
            $this->callback_URL = str_replace( 'https:', 'http:', add_query_arg( 'wc-api', 'wc_btcpyment_gateway', home_url( '/' ) ) );
            // $this->callback_URL = home_url( '/' ) . 'wc-api/' . 'WC_Btcpyment_Gateway/';

           	// This action hook saves the settings
           	add_action( 'woocommerce_update_options_payment_gateways_' . $this->id, array( $this, 'process_admin_options' ) );

           	// We need custom JavaScript to obtain a token
           	add_action( 'wp_enqueue_scri6pts', array( $this, 'payment_scripts' ) );

           	// You can also register a webhook here
           	add_action( 'woocommerce_api_wc_btcpyment_gateway', array( $this, 'webhook' ) );
 		}

		/**
 		 * Plugin options, we deal with it in Step 3 too
 		 */
 		public function init_form_fields(){

            	$this->form_fields = array(
            		'enabled' => array(
            			'title'       => 'Enable/Disable',
            			'label'       => 'Enable btcpyment Gateway',
            			'type'        => 'checkbox',
            			'description' => '',
            			'default'     => 'no'
            		),
            		'title' => array(
            			'title'       => 'Title',
            			'type'        => 'text',
            			'description' => 'This controls the title which the user sees during checkout.',
            			'default'     => 'Bitcoin',
            			'desc_tip'    => true,
            		),
            		'description' => array(
            			'title'       => 'Description',
            			'type'        => 'textarea',
            			'description' => 'This controls the description which the user sees during checkout.',
            			'default'     => 'Pay with Bitcoin via BTCPyment',
            		),
                    'btcpyment_server_url' => array(
                        'title'       => 'BTCPyment URL',
                        'type'        => 'text',
                        'description' => 'Points towards your instance of BTCPyment, should be IP or https://SERVER.com'
                    ),
                    'redirect_url' => array(
                        'title'       => 'Redirect URL',
                        'type'        => 'text',
                        'description' => 'URL the user is redirected to after payment.'
                    ),
            		'testmode' => array(
            			'title'       => 'Test mode',
            			'label'       => 'Enable Test Mode',
            			'type'        => 'checkbox',
            			'description' => 'Place the payment gateway in test mode using test API keys.',
            			'default'     => 'yes',
            			'desc_tip'    => true,
            		),
            		'test_publishable_key' => array(
            			'title'       => 'Test Publishable Key',
            			'type'        => 'text'
            		),
            		'test_private_key' => array(
            			'title'       => 'Test Private Key',
            			'type'        => 'password',
            		),
            		'publishable_key' => array(
            			'title'       => 'Live Publishable Key',
            			'type'        => 'text'
            		),
            		'private_key' => array(
            			'title'       => 'Live Private Key',
            			'type'        => 'password'
            		)
            	);
	 	}


		/*
		 * Custom CSS and JS, in most cases required only when you decided to go with a custom credit card form
		 */
	 	public function payment_scripts() {

            	// we need JavaScript to process a token only on cart/checkout pages, right?
            	if ( ! is_cart() && ! is_checkout() && ! isset( $_GET['pay_for_order'] ) ) {
            		return;
            	}

            	// if our payment gateway is disabled, we do not have to enqueue JS too
            	if ( 'no' === $this->enabled ) {
            		return;
            	}

            	// no reason to enqueue JavaScript if API keys are not set
            	if ( empty( $this->private_key ) || empty( $this->publishable_key ) ) {
            		return;
            	}

            	// do not work with card detailes without SSL unless your website is in a test mode
            	if ( ! $this->testmode && ! is_ssl() ) {
            		return;
            	}
                //
            	// // let's suppose it is our payment processor JavaScript that allows to obtain a token
            	// wp_enqueue_script( 'btcpyment_js', 'https://btcpyment.nickfarrow.com' );
                //
            	// // and this is our custom JS in your plugin directory that works with token.js
            	// wp_register_script( 'woocommerce_btcpyment', plugins_url( 'btcpyment.js', __FILE__ ), array( 'jquery', 'btcpyment_js' ) );
                //
            	// // in most payment processors you have to use PUBLIC KEY to obtain a token
            	// wp_localize_script( 'woocommerce_btcpyment', 'btcpyment_params', array(
            	// 	'publishableKey' => $this->publishable_key
            	// ) );

            	wp_enqueue_script( 'woocommerce_btcpyment' );

	 	}


		/*
		 * We're processing the payments here, everything about it is in Step 5
		 */
         public function process_payment( $order_id ) {

         	global $woocommerce;

         	// we need it to get any order detailes
         	$order = wc_get_order( $order_id );

         	/*
          	 * Array with parameters for API interaction
         	 */
         	$args = array(
                'amount' => $order->get_total(),
                'id' => $order->get_id(),
                'webhook_url' => $this->callback_URL );
                // HASH??? FOR SECURE PAYMENTS?

         	/*
         	 * Your API interaction could be built with wp_remote_post()
          	 */
             $payment_url = add_query_arg(
                $args,
                $this->btcpyment_server_url . "/pay"
            );

            return [
                'result'   => 'success',
                'redirect' => $payment_url
            ];

         	// if( !is_wp_error( $response ) ) {
            //
         	// 	 $body = json_decode( $response['body'], true );
            //
         	// 	 // it could be different depending on your payment processor
         	// 	 if ( $body['response']['responseCode'] == 'APPROVED' ) {
            //
         	// 		// we received the payment
         	// 		$order->payment_complete();
         	// 		$order->reduce_order_stock();
            //
         	// 		// some notes to customer (replace true with false to make it private)
         	// 		$order->add_order_note( 'Hey, your order is paid! Thank you!', true );
            //
         	// 		// Empty cart
         	// 		$woocommerce->cart->empty_cart();
            //
         	// 		// Redirect to the thank you page
         	// 		return array(
         	// 			'result' => 'success',
         	// 			'redirect' => $this->get_return_url( $order )
         	// 		);
            //
         	// 	 } else {
         	// 		wc_add_notice(  'Please try again.', 'error' );
         	// 		return;
         	// 	}
            //
         	// } else {
            //     wc_add_notice(  'Connection error.', 'error' );
         	// 	return;
         	// }

         }

		/*
		 * In case you need a webhook, like PayPal IPN etc
		 */
         public function webhook() {
            header( 'HTTP/1.1 200 OK' );
         	$order = wc_get_order( $_GET['id'] );
            write_log($_GET['id'])
         	// $order->payment_complete();
         	// $order->reduce_order_stock();

         	update_option('webhook_debug', $_GET);
         }
 	}
}
