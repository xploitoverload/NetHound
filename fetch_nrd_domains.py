#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
from nethound.config import parse_date
from nethound.fetchers.whoisds import fetch_whoisds_domains

def process_date(date_str=None, target_types=("com", "others"), specific_tld=None):
    try:
        target_date = parse_date(date_str)
        tld_arg = "all"
        if specific_tld:
            tld_arg = specific_tld
        elif target_types == ("com",):
            tld_arg = "com"
        elif target_types == ("others",):
            tld_arg = "others"

        print(f"[*] Processing NRD domains ({tld_arg}) for {target_date.strftime('%Y-%m-%d')}...")
        results = fetch_whoisds_domains(target_date, tld=tld_arg, output_dir=Path("."))
        total = sum(len(d) for d in results.values())
        print(f"[✓] Extracted {total} domains across {len(results)} TLDs.")
        return True
    except Exception as e:
        print(f"[!] Error: {e}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description="NetHound Multi-TLD NRD Fetcher")
    parser.add_argument("date", nargs="?", default=None, help="Date in YYYY-MM-DD or DD-MM-YYYY format")
    parser.add_argument("--type", choices=["all", "com", "others"], default="all",
                        help="Which domain categories to extract (default: all)")
    parser.add_argument("--tld", default=None, help="Specific other TLD to extract (e.g. cn, shop, net)")
    args = parser.parse_args()

    if args.type == "all":
        types = ("com", "others")
    elif args.type == "com":
        types = ("com",)
    else:
        types = ("others",)

    process_date(args.date, target_types=types, specific_tld=args.tld)

if __name__ == "__main__":
    main()
