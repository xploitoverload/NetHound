import os
from datetime import datetime
from pathlib import Path

DEFAULT_DATA_DIR = Path(os.environ.get("NETHOUND_DATA_DIR", "nethound_data"))

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36 NetHound/1.0.0"
    ),
    "Accept": "*/*",
}

def parse_date(date_str: str | None) -> datetime:
    """Parse a date string in YYYY-MM-DD or DD-MM-YYYY format, or default to yesterday."""
    if not date_str:
        from datetime import timedelta
        return datetime.now() - timedelta(days=1)
    
    for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            pass
    raise ValueError(f"Invalid date format '{date_str}'. Expected YYYY-MM-DD or DD-MM-YYYY.")
