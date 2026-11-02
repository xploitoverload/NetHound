#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
from nethound.config import parse_date
from nethound.fetchers.whoisds import fetch_whoisds_domains

def process_date(date_str=None, specific_tld=None):
    try:
        target_date = parse_date(date_str)
        tld_target = specific_tld if specific_tld else "others"
        print(f"[*] Processing other TLD domains ({tld_target}) for {target_date.strftime('%Y-%m-%d')}...")
        results = fetch_whoisds_domains(target_date, tld=tld_target, output_dir=Path("."))
        total = sum(len(d) for d in results.values())
        print(f"[✓] Extracted {total} domains across {len(results)} TLDs under others/")
        return True
    except Exception as e:
        print(f"[!] Error: {e}", file=sys.stderr)
        return False

def main():
    parser = argparse.ArgumentParser(description="NetHound Other TLD Domains Fetcher")
    parser.add_argument("date", nargs="?", default=None, help="Date in YYYY-MM-DD or DD-MM-YYYY format")
    parser.add_argument("--tld", default=None, help="Optional specific TLD to extract (e.g. cn, shop, net)")
    args = parser.parse_args()
    process_date(args.date, specific_tld=args.tld)

if __name__ == "__main__":
    main()
