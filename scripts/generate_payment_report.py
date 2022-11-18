import argparse
import csv
from datetime import datetime, timedelta
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import config
from payments import database
from node import bitcoind, clightning, lnd, xpub


def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        msg = "not a valid date: {0!r}".format(s)
        raise argparse.ArgumentTypeError(msg)


def main():
    parser = argparse.ArgumentParser(
        description="Generate CSV report about received payments.")
    parser.add_argument("report_file")
    parser.add_argument("--date-from", required=False, dest="date_from",
                        help="from date (YYYY-MM-DD)", type=valid_date)
    parser.add_argument("--date-to", required=False, dest="date_to",
                        help="to date (YYYY-MM-DD)", type=valid_date)

    try:
        args = parser.parse_args()
    except Exception as e:
        print("Error: {}".format(e))
        return

    nodes = {}
    onchain = None
    lightning = None
    for method in config.payment_methods:
        print("Connecting to {} node...".format(method["name"]))
        if method["name"] == "bitcoind":
            nodes["bitcoind"] = bitcoind.bitcoind(method)
            onchain = "bitcoind"
        elif method["name"] == "lnd":
            nodes["lnd"] = lnd.lnd(method)
            lightning = "lnd"
        elif method["name"] == "clightning":
            nodes["clightning"] = clightning.clightning(method)
            lightning = "clightning"
        elif method["name"] == "xpub":
            nodes["xpub"] = xpub.xpub(method)
            onchain = "xpub"
    print("All nodes connected.")

    where = "1"
    if args.date_from:
        where = where + " AND time >= {}".format(
            datetime.timestamp(args.date_from))
    if args.date_to:
        where = where + " AND time < {}".format(
            datetime.timestamp(args.date_to + timedelta(days=1)))
    invoices = database.load_invoices_from_db(where)

    with open(args.report_file, "w", newline="") as csvfile:
        reportwriter = csv.writer(csvfile)
        reportwriter.writerow([
            "Date", "Invoice ID", "Base value", "Base currency", "BTC value",
            "BTC paid", "Payment method", "Address / invoice", "Message"
        ])
        num_rows = 0
        for invoice in invoices:
            if invoice["method"] == "onchain":
                use_node_type = onchain
            elif invoice["method"] == "lightning":
                use_node_type = lightning
            else:
                use_node_type = invoice["method"]
            if use_node_type == "lnd":
                conf_paid, unconf_paid = nodes[use_node_type].check_payment(
                    invoice["rhash"])
            else:
                conf_paid, unconf_paid = nodes[use_node_type].check_payment(
                    invoice["uuid"])

            if conf_paid > 0:
                if invoice["method"] == "lightning":
                    address = invoice["bolt11_invoice"]
                else:
                    address = invoice["address"]
                reportwriter.writerow([
                    datetime.utcfromtimestamp(
                        int(invoice["time"])).strftime("%Y-%m-%d"),
                    invoice["uuid"],
                    invoice["base_value"],
                    invoice["base_currency"],
                    "%.8f" % float(invoice["btc_value"]),
                    "%.8f" % float(conf_paid),
                    invoice["method"],
                    address,
                    invoice["message"]
                ])
                num_rows = num_rows + 1

    print("Report generated and saved to {} ({} rows).".format(
        args.report_file, num_rows))


if __name__ == "__main__":
    main()
