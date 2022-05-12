class MissingRPCCookieFile(Exception):
    def __init__(self):
        super().__init__(f"rpc_cookie_file {self.config['rpc_cookie_file']} not found")

class BitcoindConnErr(Exception):
    def __init__(self):
        super().__init__(f"Could not connect to bitcoind. \
                Check your RPC / port tunneling settings and try again.")

class PaymentMethodUnknown(Exception):
    def __init__(self, method_name):
        super().__init__(f"Unknown payment method: {method_name}")

class ClightningConnErr(Exception):
    def __init__(self):
        super().__init__(f"Could not connect to c-lightning. Check your port tunneling settings and try again.")

class LNDConnErr(Exception):
    def __init__(self):
        super().__init__(f"Could not connect to lnd. Check your gRPC / port tunneling settings and try again.")

class XchangeUnreachable(Exception):
    def __init__(self, price_feed):
        super().__init__(f"Failed to reach {price_feed}")

class XchangeCurrencyUnavailable(Exception):
    def __init__(self, currency, price_feed):
        super().__init__(f"Failed to find currency {currency} from {price_feed}")              
