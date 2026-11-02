import os
import re
from pathlib import Path
from typing import Generator


def find_matching_files(data_dir: Path, tld: str | None = None, date_str: str | None = None) -> list[Path]:
    """Find domain text files matching optional TLD and date filters."""
    matched = []
    if not data_dir.exists():
        return matched

    for root, _, files in os.walk(data_dir):
        for f in files:
            if not f.startswith("domains_") or not f.endswith(".txt"):
                continue
            path = Path(root) / f

            # Date filter check
            if date_str and f"domains_{date_str}.txt" != f:
                continue

            # TLD filter check
            if tld:
                rel = path.relative_to(data_dir)
                parts = rel.parts
                # Structure: in/year/month/file or com/year/month/file or others/tld/year/month/file
                if parts[0] == "in" and tld.lower() != "in":
                    continue
                elif parts[0] == "com" and tld.lower() != "com":
                    continue
                elif parts[0] == "others" and len(parts) > 1 and parts[1].lower() != tld.lower():
                    continue

            matched.append(path)

    return sorted(matched)


def search_domains(
    data_dir: Path,
    pattern: str,
    regex: bool = False,
    tld: str | None = None,
    date_str: str | None = None,
) -> Generator[tuple[str, Path], None, None]:
    """
    Search domain records for a string or regex pattern.
    Yields (domain, file_path).
    """
    files = find_matching_files(data_dir, tld=tld, date_str=date_str)
    
    if regex:
        compiled = re.compile(pattern, re.IGNORECASE)
        matcher = lambda d: bool(compiled.search(d))
    else:
        needle = pattern.lower()
        matcher = lambda d: needle in d.lower()

    for file_path in files:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    dom = line.strip()
                    if dom and matcher(dom):
                        yield (dom, file_path)
        except Exception:
            continue
