import argparse
import csv
import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import config
from payments import database
from node import bitcoind, clightning, lnd, xpub


REPORT_HEADERS = [
    "Date",
    "Invoice ID",
    "Base value",
    "Base currency",
    "BTC value",
    "BTC paid",
    "Payment method",
    "Address / invoice",
    "Message",
]


def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        msg = "not a valid date: {0!r}".format(s)
        raise argparse.ArgumentTypeError(msg)


def create_parser():
    parser = argparse.ArgumentParser(
        description="Generate CSV report about received payments."
    )
    parser.add_argument("report_file")
    parser.add_argument(
        "--date-from",
        required=False,
        dest="date_from",
        help="from date (YYYY-MM-DD)",
        type=valid_date,
    )
    parser.add_argument(
        "--date-to",
        required=False,
        dest="date_to",
        help="to date (YYYY-MM-DD)",
        type=valid_date,
    )
    return parser


def connect_nodes(payment_methods):
    nodes = {}
    onchain = None
    lightning = None

    for method in payment_methods:
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
    return nodes, onchain, lightning


def build_where_clause(date_from=None, date_to=None):
    where = "1"

    if date_from:
        where = where + " AND time >= {}".format(datetime.timestamp(date_from))

    if date_to:
        where = where + " AND time < {}".format(
            datetime.timestamp(date_to + timedelta(days=1))
        )

    return where


def get_node_type_for_invoice(invoice, onchain, lightning):
    if invoice["method"] == "onchain":
        return onchain

    if invoice["method"] == "lightning":
        return lightning

    return invoice["method"]


def check_invoice_payment(invoice, nodes, onchain, lightning):
    node_type = get_node_type_for_invoice(invoice, onchain, lightning)

    if node_type == "lnd":
        return nodes[node_type].check_payment(invoice["rhash"])

    return nodes[node_type].check_payment(invoice["uuid"])


def get_invoice_address(invoice):
    if invoice["method"] == "lightning":
        return invoice["bolt11_invoice"]

    return invoice["address"]


def invoice_to_report_row(invoice, conf_paid):
    return [
        datetime.utcfromtimestamp(int(invoice["time"])).strftime("%Y-%m-%d"),
        invoice["uuid"],
        invoice["base_value"],
        invoice["base_currency"],
        "%.8f" % Decimal(invoice["btc_value"]),
        "%.8f" % Decimal(conf_paid),
        invoice["method"],
        get_invoice_address(invoice),
        invoice["message"],
    ]


def write_payment_report(report_file, invoices, nodes, onchain, lightning):
    num_rows = 0

    with open(report_file, "w", newline="") as csvfile:
        reportwriter = csv.writer(csvfile)
        reportwriter.writerow(REPORT_HEADERS)

        for invoice in invoices:
            conf_paid, _ = check_invoice_payment(
                invoice, nodes, onchain, lightning
            )

            if conf_paid > 0:
                reportwriter.writerow(invoice_to_report_row(invoice, conf_paid))
                num_rows = num_rows + 1

    return num_rows


def main():
    parser = create_parser()

    try:
        args = parser.parse_args()
    except Exception as e:
        print("Error: {}".format(e))
        return

    nodes, onchain, lightning = connect_nodes(config.payment_methods)

    where = build_where_clause(args.date_from, args.date_to)
    invoices = database.load_invoices_from_db(where)

    num_rows = write_payment_report(
        args.report_file,
        invoices,
        nodes,
        onchain,
        lightning,
    )

    print("Report generated and saved to {} ({} rows).".format(
        args.report_file, num_rows
    ))


if __name__ == "__main__":
    main()
