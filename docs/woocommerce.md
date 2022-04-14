# Woocommerce Payment Gateway

To install the Woocommerce payment gateway plugin, first copy [/gateways/woo_satsale.php](/gateways/woo_satsale.php) to your Wordpress site in `wp-content/plugins/`. If you're using the browser interface, you'll need to compress the file before uploading.

Next, in your Wordpress admin area, go to the plugins section and activate SatSale. Then go to the Woocommerce settings and the "Payments" tab. Enable SatSale as a payment gateway.
![Woocommerce Settings](https://user-images.githubusercontent.com/24557779/104807944-c74b2100-5836-11eb-8dba-dfaf8b5f5e1f.png)

Click 'Set Up'/'Manage' and fill out the required fields and point towards your SatSale instance. You will need to copy the contents of `SatSale/SatSale_API_key` into your API key field. This is generated after running SatSale for the first time.
![SatSale Settings](https://user-images.githubusercontent.com/24557779/105259537-164ed880-5be0-11eb-9785-9b2208ad04cb.png)

Now you should be able to view SatSale as an option in your checkout:
![SatSale in Checkout](https://user-images.githubusercontent.com/24557779/105259742-7776ac00-5be0-11eb-82fd-9d82a7f1316b.png)

That's it! Please reach out if there are some further features you desire in this plugin.
