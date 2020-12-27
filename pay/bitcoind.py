import config
import subprocess
from invoice.payment_invoice import invoice

class btcd(invoice):
    def __init__(self, dollar_value, currency, label):
        super().__init__(dollar_value, currency, label)
        print(self.__dict__)
        # self.__dict__ = invoice.__dict__.copy()

        from bitcoinrpc.authproxy import AuthServiceProxy

        connection_str = "http://{}:{}@{}:{}".format(config.username, config.password, config.host, config.rpcport)
        print("Attempting to connect to {}.".format(connection_str))

        for i in range(config.connection_attempts):
            try:
                self.rpc = AuthServiceProxy(connection_str)
                info = self.rpc.getblockchaininfo()
                print("Successfully contacted bitcoind.")
                break

            except Exception as e:
                print(e)
                print("Attempting again... {}/{}...".format(i+1, config.connection_attempts))
        else:
            raise Exception("Could not connect to bitcoind. Check your RPC / port tunneling settings and try again.")

    def check_payment(self):
        self.address = self.get_address()
        transactions = self.rpc.listtransactions()
        relevant_txs = [tx for tx in transactions if tx['address'] == self.address]

        conf_paid = 0
        unconf_paid = 0
        for tx in relevant_txs:
            if tx['confirmations'] >= config.required_confirmations:
                conf_paid += tx['amount']
            else:
                unconf_paid += tx['amount']

        return conf_paid, unconf_paid

    def get_address(self):
        for i in range(config.connection_attempts):
            try:
                self.address = self.rpc.getnewaddress(self.label)
            except Exception as e:
                print(e)
                print("Attempting again... {}/{}...".format(i+1, config.connection_attempts))
        return
