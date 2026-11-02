import base64
from collections import defaultdict
from datetime import datetime
import io
from pathlib import Path
import tempfile
import zipfile
import requests

from nethound.config import DEFAULT_HEADERS

WHOISDS_URL = "https://whoisds.com/whois-database/newly-registered-domains/{b64_date}/nrd"


def download_nrd_archive(target_date: datetime) -> bytes | None:
    """Download daily NRD zip archive from WhoisDS, with temporary caching."""
    date_formatted = target_date.strftime("%Y-%m-%d")
    cache_file = Path(tempfile.gettempdir()) / f"nethound_{date_formatted}.zip"

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
    url = WHOISDS_URL.format(b64_date=b64_filename)

    response = requests.get(url, headers=DEFAULT_HEADERS, timeout=60)
    if response.status_code != 200:
        return None

    try:
        with zipfile.ZipFile(io.BytesIO(response.content)) as z:
            if not z.namelist():
                return None
    except zipfile.BadZipFile:
        return None

    with open(cache_file, "wb") as f:
        f.write(response.content)

    return response.content


def fetch_whoisds_domains(
    target_date: datetime,
    tld: str = "com",
    output_dir: Path | None = None,
) -> dict[str, list[str]]:
    """
    Extract domains from WhoisDS NRD archive.
    tld can be 'com', 'all', 'others', or a specific TLD like 'net', 'shop', 'cn'.
    Returns a dict mapping TLD -> list of domains.
    """
    archive_bytes = download_nrd_archive(target_date)
    if not archive_bytes:
        return {}

    date_formatted = target_date.strftime("%Y-%m-%d")
    year = target_date.strftime("%Y")
    month = target_date.strftime("%m")

    tld_lower = tld.lower()
    target_is_all = tld_lower in ("all", "*")
    target_is_others = tld_lower == "others"
    target_is_com = tld_lower == "com"

    results: dict[str, list[str]] = defaultdict(list)

    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as z:
        for filename in z.namelist():
            with z.open(filename) as f:
                for line in f:
                    domain = line.decode("utf-8", errors="ignore").strip().lower()
                    if not domain or "." not in domain:
                        continue

                    if domain.endswith(".com"):
                        if target_is_all or target_is_com:
                            results["com"].append(domain)
                    else:
                        if target_is_com:
                            continue
                        try:
                            ascii_dom = domain.encode("idna").decode("ascii")
                        except Exception:
                            ascii_dom = domain

                        parts = ascii_dom.rsplit(".", 1)
                        if len(parts) == 2:
                            current_tld = parts[1].lower()
                            if current_tld.replace("-", "").isalnum():
                                if not target_is_all and not target_is_others and current_tld != tld_lower:
                                    continue
                                results[current_tld].append(domain)

    # Sort and deduplicate
    for k in list(results.keys()):
        results[k] = sorted(set(results[k]))

    # Save to disk if output directory provided
    if output_dir:
        for current_tld, doms in results.items():
            if current_tld == "com":
                dest_dir = output_dir / "com" / year / month
            else:
                dest_dir = output_dir / "others" / current_tld / year / month
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_file = dest_dir / f"domains_{date_formatted}.txt"
            with open(dest_file, "w", encoding="utf-8") as f:
                f.write("\n".join(doms) + ("\n" if doms else ""))

    return dict(results)
