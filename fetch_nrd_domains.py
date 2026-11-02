#!/usr/bin/env python3
import argparse
import base64
from collections import defaultdict
from datetime import datetime, timedelta
import io
import os
from pathlib import Path
import sys
import tempfile
import zipfile
import requests

BASE_URL = "https://whoisds.com/whois-database/newly-registered-domains/{b64_date}/nrd"

def get_cached_or_download_zip(date_formatted: str) -> bytes | None:
    cache_file = Path(tempfile.gettempdir()) / f"nrd_{date_formatted}.zip"
    if cache_file.exists() and cache_file.stat().st_size > 1024:
        try:
            with open(cache_file, "rb") as f:
                data = f.read()
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                if z.namelist():
                    return data
        except Exception:
            cache_file.unlink(missing_ok=True)

    b64_filename = base64.b64encode(f"{date_formatted}.zip".encode()).decode().rstrip("=")
    download_url = BASE_URL.format(b64_date=b64_filename)

    print(f"[*] Downloading daily NRD archive for {date_formatted} from: {download_url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "*/*"
    }

    try:
        response = requests.get(download_url, headers=headers, timeout=60)
        if response.status_code != 200:
            print(f"[!] HTTP {response.status_code} when fetching archive for {date_formatted}")
            return None

        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            if not z.namelist():
                print(f"[!] Empty archive for {date_formatted}")
                return None

        with open(cache_file, "wb") as f:
            f.write(response.content)

        return response.content

    except zipfile.BadZipFile:
        print(f"[!] Non-zip response received for {date_formatted} (file may not be ready yet)")
        return None
    except Exception as e:
        print(f"[!] Error downloading archive for {date_formatted}: {e}")
        return None

def extract_nrd_domains(target_date: datetime, target_types=("com", "others"), specific_tld=None) -> bool:
    date_formatted = target_date.strftime("%Y-%m-%d")
    year = target_date.strftime("%Y")
    month = target_date.strftime("%m")

    # Check if files already exist
    com_file = Path("com") / year / month / f"domains_{date_formatted}.txt"
    check_tld = specific_tld if specific_tld else "cn"
    other_check = Path("others") / check_tld / year / month / f"domains_{date_formatted}.txt"

    needed = False
    if "com" in target_types and not (com_file.exists() and com_file.stat().st_size > 0):
        needed = True
    if "others" in target_types and not (other_check.exists() and other_check.stat().st_size > 0):
        needed = True

    if not needed:
        print(f"[*] Requested domains for {date_formatted} already exist. Skipping.")
        return True

    zip_bytes = get_cached_or_download_zip(date_formatted)
    if not zip_bytes:
        return False

    com_domains = []
    other_domains_by_tld = defaultdict(list)

    try:
        with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
            for filename in z.namelist():
                with z.open(filename) as f:
                    for line in f:
                        domain = line.decode("utf-8", errors="ignore").strip().lower()
                        if not domain or "." not in domain:
                            continue

                        if domain.endswith(".com"):
                            if "com" in target_types:
                                com_domains.append(domain)
                        elif "others" in target_types:
                            try:
                                ascii_domain = domain.encode("idna").decode("ascii")
                            except Exception:
                                ascii_domain = domain

                            parts = ascii_domain.rsplit(".", 1)
                            if len(parts) == 2:
                                tld = parts[1].lower()
                                if tld.replace("-", "").isalnum():
                                    if specific_tld and tld != specific_tld.lower():
                                        continue
                                    other_domains_by_tld[tld].append(domain)

        if "com" in target_types:
            com_domains = sorted(set(com_domains))
            out_dir = Path("com") / year / month
            out_dir.mkdir(parents=True, exist_ok=True)
            with open(com_file, "w", encoding="utf-8") as f:
                f.write("\n".join(com_domains) + "\n")
            print(f"[✓] Extracted {len(com_domains)} .com domains to {com_file}")

        if "others" in target_types:
            total_other_count = 0
            for tld, dom_list in other_domains_by_tld.items():
                tld_domains = sorted(set(dom_list))
                total_other_count += len(tld_domains)
                out_dir = Path("others") / tld / year / month
                out_dir.mkdir(parents=True, exist_ok=True)
                out_file = out_dir / f"domains_{date_formatted}.txt"
                with open(out_file, "w", encoding="utf-8") as f:
                    f.write("\n".join(tld_domains) + "\n")

            print(f"[✓] Extracted {total_other_count} other domains across {len(other_domains_by_tld)} TLD folders under others/")

        return True

    except Exception as e:
        print(f"[!] Error extracting domains for {date_formatted}: {e}")
        return False

def process_date(date_str=None, target_types=("com", "others"), specific_tld=None):
    if date_str:
        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            target_date = datetime.strptime(date_str, "%d-%m-%Y")

        success = extract_nrd_domains(target_date, target_types=target_types, specific_tld=specific_tld)
        if not success:
            fallback = target_date - timedelta(days=1)
            print(f"[*] Retrying with previous day ({fallback.strftime('%Y-%m-%d')})...")
            extract_nrd_domains(fallback, target_types=target_types, specific_tld=specific_tld)
    else:
        yesterday = datetime.now() - timedelta(days=1)
        extract_nrd_domains(yesterday, target_types=target_types, specific_tld=specific_tld)

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
