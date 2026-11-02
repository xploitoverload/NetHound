#!/usr/bin/env python3
import base64
from datetime import datetime, timedelta
import io
import os
from pathlib import Path
import sys
import zipfile
import requests

BASE_URL = "https://whoisds.com/whois-database/newly-registered-domains/{b64_date}/nrd"

def fetch_com_for_date(target_date: datetime, output_base: Path = Path("com")) -> bool:
    date_formatted = target_date.strftime("%Y-%m-%d")
    year = target_date.strftime("%Y")
    month = target_date.strftime("%m")

    output_dir = output_base / year / month
    output_file = output_dir / f"domains_{date_formatted}.txt"

    if output_file.exists() and output_file.stat().st_size > 0:
        print(f"[*] {output_file} already exists. Skipping download.")
        return True

    # WhoisDS uses base64 encoded 'YYYY-MM-DD.zip' without padding '='
    b64_filename = base64.b64encode(f"{date_formatted}.zip".encode()).decode().rstrip("=")
    download_url = BASE_URL.format(b64_date=b64_filename)

    print(f"[*] Fetching .com NRDs for {date_formatted} from: {download_url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "*/*"
    }

    try:
        response = requests.get(download_url, headers=headers, timeout=60)
        if response.status_code != 200:
            print(f"[!] HTTP {response.status_code} for {date_formatted}")
            return False

        com_domains = []
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            for filename in z.namelist():
                with z.open(filename) as f:
                    for line in f:
                        domain = line.decode("utf-8", errors="ignore").strip().lower()
                        if domain.endswith(".com"):
                            com_domains.append(domain)

        if not com_domains:
            print(f"[!] No .com domains found in archive for {date_formatted}")
            return False

        com_domains = sorted(set(com_domains))

        output_dir.mkdir(parents=True, exist_ok=True)
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("\n".join(com_domains) + "\n")

        print(f"[✓] Extracted {len(com_domains)} .com domains to {output_file}")
        return True

    except zipfile.BadZipFile:
        print(f"[!] Non-zip response received for {date_formatted} (file may not be ready yet)")
        return False
    except Exception as e:
        print(f"[!] Error processing {date_formatted}: {e}")
        return False

def process_date(date_str=None):
    if date_str:
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            target_date = datetime.strptime(date_str, "%d-%m-%Y")
        
        success = fetch_com_for_date(target_date)
        if not success:
            fallback = target_date - timedelta(days=1)
            print(f"[*] Retrying with previous day ({fallback.strftime('%Y-%m-%d')})...")
            fetch_com_for_date(fallback)
    else:
        # Default: fetch yesterday and day before if missing
        yesterday = datetime.now() - timedelta(days=1)
        fetch_com_for_date(yesterday)

if __name__ == "__main__":
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    process_date(date_arg)
