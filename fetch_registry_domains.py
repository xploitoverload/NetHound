#!/usr/bin/env python3
import sys
from pathlib import Path
from nethound.config import parse_date
from nethound.fetchers.registry_in import fetch_in_domains

def process_date(date_str=None):
    try:
        target_date = parse_date(date_str)
        print(f"[*] Processing .IN domains for {target_date.strftime('%Y-%m-%d')}...")
        domains = fetch_in_domains(target_date, output_dir=Path("."))
        print(f"[✓] Success! Extracted {len(domains)} .IN domains to in/")
        return True
    except Exception as e:
        print(f"[!] Error: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    process_date(date_arg)
