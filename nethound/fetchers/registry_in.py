import io
import re
from datetime import datetime
from pathlib import Path
import requests

from nethound.config import DEFAULT_HEADERS

REGISTRY_IN_URL = "https://registry.in/system/files/domain-creates_{date}.pdf"


def _extract_domains_pypdf(content: bytes) -> list[str]:
    import pypdf
    reader = pypdf.PdfReader(io.BytesIO(content))
    domains = set()
    for page in reader.pages:
        text = page.extract_text()
        if not text:
            continue
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("Domain User Form") or line.startswith("Page"):
                continue
            parts = line.split()
            if parts:
                dom = parts[0].strip().lower()
                if "." in dom and not dom.startswith("page") and not dom.startswith("created"):
                    domains.add(dom)
    return sorted(domains)


def _extract_domains_pdfplumber(content: bytes) -> list[str]:
    import pdfplumber
    domains = set()
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                for row in table[1:]:
                    if row and row[0]:
                        domain = row[0].strip().lower()
                        if domain and domain != "domain user form" and "." in domain:
                            domains.add(domain)
    return sorted(domains)


def extract_domains_from_pdf_bytes(content: bytes) -> list[str]:
    """Extract domains from registry.in PDF bytes using pypdf or pdfplumber."""
    try:
        return _extract_domains_pypdf(content)
    except ImportError:
        pass

    try:
        return _extract_domains_pdfplumber(content)
    except ImportError:
        raise RuntimeError("No PDF extractor available. Please install 'python3-pypdf' or 'pdfplumber'.")


def fetch_in_domains(target_date: datetime, output_dir: Path | None = None) -> list[str]:
    """Download and extract .IN newly registered domains for target_date."""
    date_formatted = target_date.strftime("%Y-%m-%d")
    url = REGISTRY_IN_URL.format(date=date_formatted)

    response = requests.get(url, headers=DEFAULT_HEADERS, timeout=45)
    response.raise_for_status()

    domains = extract_domains_from_pdf_bytes(response.content)

    if output_dir:
        year = target_date.strftime("%Y")
        month = target_date.strftime("%m")
        dest_dir = output_dir / "in" / year / month
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file = dest_dir / f"domains_{date_formatted}.txt"
        with open(dest_file, "w", encoding="utf-8") as f:
            f.write("\n".join(domains) + ("\n" if domains else ""))

    return domains
