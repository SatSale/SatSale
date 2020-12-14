# BTCPYSERVER
BTCPayserver is incredibly bloated. The goal of BTCpyserver is to act as a lightweight bitcoin payment system for your website.

# Installation
This should be easy to install.

# Architecture
btcpysever
-site/
--website.php
-invoice/
--main.py
--database.py
--price_feed.py
-btc_pay/
--bitcoind.py
--clightning.py
-success/
--success.py
-failure
--failure.py
-main.py


# Minimum requirements for proof of concept
Requires end-to-end payment, handling both success and failure
- PHP invoice page, could everything be php...?
- Not PHP, need something that can dynamically show the progress!
- Feedback: timeleft, confirmations, etc.
- integrate with bitcoind, monitor transactions
- 



# On php post, 
# Call btcpy with invoice commands
# Invoice is in USD (default) and converts automatically to BTC
# conversion_to_usd.py
# Call bitcoind to create a new address
# Save invoice with address to database
	- Pandas
	- SQL?
	- Other?
# read address form database back:
# Pass address back to website
# Wait for user send...

# btc_pay
# Check bitcoind mempool every 5 seconds for incoming transactions,
# wait for x confirmations (x also determines invoice_timeout)
# After x confirmations, return as paid to website and unlock/call any other function. This could even be a custom script like sale_success_command.sh (link to digital good, call other APIs)
# Need to integrate with at least 1 shop, woocommerce, as a proof of concept.

# lighting_pay
# Same but integrate c_lightning.py for proof of concept.


# success/ 
Payment success
Display on website as successfuly paid, write to database to confirm payment.
Navigate elsewhere by calling script from `sales/*.py`
This script will control what happens after payment confirmation, can integate many shops / styles.

# failure/
Also customisable!
Times out after XX minutes, (depend on confirmations required).
Default:
	- Add button to recreate invoice
		- Recalculates value request.
	-
