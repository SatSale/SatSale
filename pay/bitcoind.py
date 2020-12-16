import config
import subprocess

class btcd:
    def __init__(self):
        from bitcoinrpc.authproxy import AuthServiceProxy

        connection_str = "http://{}:{}@{}:{}".format(config.username, config.password, config.host, config.rpcport)
        print("Attempting to connect to {}.".format(connection_str))

        try:
            self.rpc = AuthServiceProxy(connection_str)
            # info = self.rpc.getblockchaininfo()
            # info = self.rpc.help()

            print("Successfully contacted bitcoind.")
            print("-"*10)
            print(info)
            print("-"*10)

        except Exception as e:
            print(e)

    def load_invoice(self, invoice):
        self.value = invoice.value
        self.label = invoice.label
        self.paid = False
        return

    def check_payment(self):
        self.address = "bc1qwxlwghumfmhwdc2deyn7h42syp2t496penax2y"
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
        self.address = self.rpc.getnewaddress(self.label)
        return
