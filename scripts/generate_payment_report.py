import argparse
import csv
from datetime import datetime, timedelta

import config
from payments import database
from node import bitcoind
from node import lnd
from node import clightning


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

    bitcoin_node = bitcoind.btcd()
    if config.pay_method == "lnd":
        lightning_node = lnd.lnd()
    elif config.pay_method == "clightning":
        lightning_node = clightning.clightning()

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
            "Date", "Invoice ID", "Fiat value", "BTC value",
            "BTC paid", "Payment method", "Address"
        ])
        num_rows = 0
        for invoice in invoices:
            conf_paid = 0
            if invoice["method"] == "bitcoind":
                conf_paid, unconf_paid = bitcoin_node.check_payment(
                    invoice["uuid"])
            elif invoice["method"] == "lnd":
                conf_paid, unconf_paid = lightning_node.check_payment(
                    invoice["rhash"])
            elif invoice["method"] == "clightning":
                conf_paid, unconf_paid = lightning_node.check_payment(
                    invoice["uuid"])

            if conf_paid > 0:
                reportwriter.writerow([
                    datetime.utcfromtimestamp(
                        int(invoice["time"])).strftime("%Y-%m-%d"),
                    invoice["uuid"],
                    invoice["fiat_value"],
                    "%.8f" % float(invoice["btc_value"]),
                    "%.8f" % float(conf_paid),
                    invoice["method"],
                    invoice["address"]
                ])
                num_rows = num_rows + 1

    print("Report generated and saved to {} ({} rows).".format(
        args.report_file, num_rows))


if __name__ == "__main__":
    main()