import argparse
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from payments import database
from node import xpub


def main():
    parser = argparse.ArgumentParser(
        description="Scan xpub for used addresses.")
    parser.add_argument("--dry-run", action="store_true",
        help="Only scan addresses but don't update local database")
    parser.add_argument("-g", "--gap-limit", required=True, dest="gap_limit", type=int,
        help="Gap limit (how many unused addresses to scan starting from the last known used one)")

    try:
        args = parser.parse_args()
    except Exception as e:
        print(f"Error: {e}")
        return

    import config
    node = None
    xpub_str = None
    for method in config.payment_methods:
        if method["name"] == "xpub":
            node = xpub.xpub(method)
            xpub_str = method["xpub"]
    if node is None:
        print("xpub payment method not configured")
        return

    start_index = database.get_next_address_index(xpub_str)

    print(f"Scanning {xpub_str} for the next {args.gap_limit} addresses from index {start_index} (dry_run={args.dry_run})")

    current_index = start_index
    last_used_index = current_index - 1
    current_gap = 0
    while current_gap < args.gap_limit:
        address = node.get_address_at_index(current_index)
        conf_paid, conf_unpaid = node.check_payment(address)
        paid = conf_paid + conf_unpaid
        print(f"{address} ({current_index}): {paid:.8f} (gap={current_gap})")
        if paid > 0:
            last_used_index = current_index
            current_gap = 0
        else:
            current_gap = current_gap + 1
        current_index = current_index + 1

    print(f"Last used index: {last_used_index}")

    if not args.dry_run:
        for i in range(start_index, last_used_index + 1):
            address = node.get_address_at_index(i)
            print(f"Marking {address} ({i}) as used")
            database.add_generated_address(i, address, xpub_str)


if __name__ == "__main__":
    main()
