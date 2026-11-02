#!/usr/bin/env python3
import argparse
import sys
from fetch_nrd_domains import process_date

def main():
    parser = argparse.ArgumentParser(description="NetHound Other TLD Domains Fetcher")
    parser.add_argument("date", nargs="?", default=None, help="Date in YYYY-MM-DD or DD-MM-YYYY format")
    parser.add_argument("--tld", default=None, help="Optional specific TLD to extract (e.g. cn, shop, net)")
    args = parser.parse_args()

    process_date(args.date, target_types=("others",), specific_tld=args.tld)

if __name__ == "__main__":
    main()
