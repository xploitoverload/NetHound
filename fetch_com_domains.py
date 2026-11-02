#!/usr/bin/env python3
import sys
from pathlib import Path
from nethound.config import parse_date
from nethound.fetchers.whoisds import fetch_whoisds_domains

def process_date(date_str=None):
    try:
        target_date = parse_date(date_str)
        print(f"[*] Processing .COM domains for {target_date.strftime('%Y-%m-%d')}...")
        results = fetch_whoisds_domains(target_date, tld="com", output_dir=Path("."))
        com_count = len(results.get("com", []))
        print(f"[✓] Extracted {com_count} .com domains to com/")
        return True
    except Exception as e:
        print(f"[!] Error: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    process_date(date_arg)
