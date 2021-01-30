# Woocommerce Payment Gateway
To install the woocommerce payment gateway plugin, first copy [/gateways/woo_btcpyment.php](/gateways/woo_btcpyment.php) to your Wordpress site in `wp-content/plugins/`.

Next, in your Wordpress admin area, go to the plugins section and activate BTCPyment. Then go to the Woocommerce settings and the "Payments" tab. Enable BTCPyment as a payment gateway.
![Woocommerce Settings](https://user-images.githubusercontent.com/24557779/104807944-c74b2100-5836-11eb-8dba-dfaf8b5f5e1f.png)

Click 'Manage' and fill out the required fields and point towards your BTCPyment instance. You will need to copy the contents of `BTCPyment/BTCPyment_API_key` into your API key field. This is generated after running BTCPyment for the first time.
![BTCPyment Settings](https://user-images.githubusercontent.com/24557779/105259537-164ed880-5be0-11eb-9785-9b2208ad04cb.png)

Now you should be able to view BTCPyment as an option in your checkout:
![BTCPyment in Checkout](https://user-images.githubusercontent.com/24557779/105259742-7776ac00-5be0-11eb-82fd-9d82a7f1316b.png)

That's it! Please reach out if there are some further features you desire in this plugin.
