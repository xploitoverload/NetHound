import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

from nethound import __version__
from nethound.config import DEFAULT_DATA_DIR, parse_date
from nethound.fetchers.registry_in import fetch_in_domains
from nethound.fetchers.whoisds import fetch_whoisds_domains
from nethound.search import search_domains, find_matching_files


def cmd_fetch(args) -> int:
    try:
        target_date = parse_date(args.date)
    except ValueError as e:
        print(f"[!] {e}", file=sys.stderr)
        return 1

    tld_arg = args.tld.lower()
    output_dir = Path(args.output_dir) if args.output_dir and not args.stdout else None
    
    # If not writing to stdout and no explicit output_dir, default to local directory
    if not args.stdout and not output_dir:
        output_dir = Path(".")

    all_domains: dict[str, list[str]] = {}

    # 1. Handle .IN TLD
    if tld_arg in ("in", "all", "*"):
        if not args.stdout:
            print(f"[*] Fetching .IN domains for {target_date.strftime('%Y-%m-%d')}...", file=sys.stderr)
        try:
            in_domains = fetch_in_domains(target_date, output_dir=output_dir)
            all_domains["in"] = in_domains
            if not args.stdout:
                print(f"[✓] Extracted {len(in_domains)} .IN domains.", file=sys.stderr)
        except Exception as e:
            if not args.stdout:
                print(f"[!] Failed to fetch .IN domains: {e}", file=sys.stderr)

    # 2. Handle WhoisDS TLDs (.com, others, specific)
    if tld_arg != "in":
        whois_target = "all" if tld_arg == "all" else tld_arg
        if not args.stdout:
            print(f"[*] Fetching WhoisDS domains ({whois_target}) for {target_date.strftime('%Y-%m-%d')}...", file=sys.stderr)
        try:
            whois_results = fetch_whoisds_domains(target_date, tld=whois_target, output_dir=output_dir)
            for k, v in whois_results.items():
                all_domains[k] = v
                if not args.stdout:
                    print(f"[✓] Extracted {len(v)} .{k} domains.", file=sys.stderr)
        except Exception as e:
            if not args.stdout:
                print(f"[!] Failed to fetch WhoisDS domains: {e}", file=sys.stderr)

    # Output formatting
    if args.json:
        payload = {
            "date": target_date.strftime("%Y-%m-%d"),
            "total_domains": sum(len(d) for d in all_domains.values()),
            "tlds": {k: len(v) for k, v in all_domains.items()},
            "domains": all_domains,
        }
        print(json.dumps(payload, indent=2))
    elif args.stdout:
        for tld_name, dom_list in all_domains.items():
            for dom in dom_list:
                print(dom)
    else:
        total = sum(len(d) for d in all_domains.values())
        print(f"[*] Done. Total {total} domains saved into {output_dir.resolve()}/", file=sys.stderr)

    return 0


def cmd_search(args) -> int:
    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        print(f"[!] Data directory '{data_dir}' does not exist.", file=sys.stderr)
        return 1

    results = []
    for domain, file_path in search_domains(
        data_dir,
        pattern=args.pattern,
        regex=args.regex,
        tld=args.tld,
        date_str=args.date,
    ):
        if args.json:
            results.append({"domain": domain, "file": str(file_path)})
        else:
            if args.verbose:
                print(f"{domain}\t({file_path})")
            else:
                print(domain)

    if args.json:
        print(json.dumps(results, indent=2))

    return 0


def cmd_stats(args) -> int:
    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        print(f"[!] Data directory '{data_dir}' does not exist.", file=sys.stderr)
        return 1

    files = find_matching_files(data_dir)
    print(f"[*] NetHound Database Summary: {data_dir.resolve()}")
    print(f"    Total domain files: {len(files)}")

    tld_counts: dict[str, int] = {}
    for f in files:
        rel = f.relative_to(data_dir)
        tld_key = rel.parts[0]
        if tld_key == "others" and len(rel.parts) > 1:
            tld_key = f"others/{rel.parts[1]}"
        try:
            with open(f, "r", encoding="utf-8", errors="ignore") as fp:
                count = sum(1 for line in fp if line.strip())
            tld_counts[tld_key] = tld_counts.get(tld_key, 0) + count
        except Exception:
            pass

    for tld_key, count in sorted(tld_counts.items(), key=lambda x: x[1], reverse=True)[:20]:
        print(f"    - {tld_key:<15}: {count:,} domains")

    print(f"    Total domains tracked: {sum(tld_counts.values()):,}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nethound",
        description="NetHound - Newly Registered Domains (NRDs) Tracker & Threat Intelligence Extractor",
    )
    parser.add_argument("-v", "--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Fetch subcommand
    fetch_parser = subparsers.add_parser("fetch", help="Fetch daily newly registered domains")
    fetch_parser.add_argument(
        "--tld",
        default="all",
        help="Target TLD ('in', 'com', 'all', 'others', or specific e.g. 'cn', 'shop', 'net'). Default: all",
    )
    fetch_parser.add_argument(
        "--date",
        default=None,
        help="Date in YYYY-MM-DD or DD-MM-YYYY format (default: yesterday)",
    )
    fetch_parser.add_argument(
        "-o",
        "--output-dir",
        default=None,
        help="Directory to save domains (default: current directory structure)",
    )
    fetch_parser.add_argument(
        "-s",
        "--stdout",
        action="store_true",
        help="Stream domains directly to stdout (useful for piping into httpx, subfinder, dnsx)",
    )
    fetch_parser.add_argument(
        "--json",
        action="store_true",
        help="Output results in JSON format",
    )

    # Search subcommand
    search_parser = subparsers.add_parser("search", help="Search downloaded NRDs for keywords or regex")
    search_parser.add_argument("pattern", help="String or regular expression pattern to match")
    search_parser.add_argument("-r", "--regex", action="store_true", help="Treat pattern as regular expression")
    search_parser.add_argument("--tld", default=None, help="Filter by specific TLD")
    search_parser.add_argument("--date", default=None, help="Filter by specific date (YYYY-MM-DD)")
    search_parser.add_argument("-d", "--data-dir", default=".", help="Root directory containing domain files (default: .)")
    search_parser.add_argument("-V", "--verbose", action="store_true", help="Print file source alongside matching domain")
    search_parser.add_argument("--json", action="store_true", help="Output results in JSON format")

    # Stats subcommand
    stats_parser = subparsers.add_parser("stats", help="Display statistics of local NRD database")
    stats_parser.add_argument("-d", "--data-dir", default=".", help="Root directory containing domain files (default: .)")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    if args.command == "fetch":
        return cmd_fetch(args)
    elif args.command == "search":
        return cmd_search(args)
    elif args.command == "stats":
        return cmd_stats(args)

    return 0


if __name__ == "__main__":
    sys.exit(main())
