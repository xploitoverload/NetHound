<p align="center">
  <img src="NetHound%20Cybersecurity%20Intelligence%20Banner.png" alt="NetHound Cybersecurity Intelligence Banner" width="100%">
</p>

# NetHound 🐕

### Newly Registered Domains (NRDs) tracker for OSINT and threat-intelligence research

[![GitHub Stars](https://img.shields.io/github/stars/xploitoverload/NetHound?style=social)](https://github.com/xploitoverload/NetHound/stargazers)
[![Daily Domain Fetch](https://github.com/xploitoverload/NetHound/actions/workflows/daily-domain-fetch.yml/badge.svg)](https://github.com/xploitoverload/NetHound/actions/workflows/daily-domain-fetch.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Platform: Linux | macOS | Windows](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg)](https://github.com/xploitoverload/NetHound)

**NetHound** is a modular command-line tool for collecting, archiving, and searching Newly Registered Domains (NRDs). It tracks supported TLD data sources, keeps date-organized domain archives, and makes the results easy to inspect or pipe into other security tools.

It is designed for security researchers, SOC analysts, OSINT investigators, and defenders working on:

- Phishing and suspicious-domain investigations
- Brand monitoring and typosquatting research
- DNS and infrastructure reconnaissance
- Threat-intelligence enrichment and hunting

> **Important:** A newly registered domain is not automatically malicious. NetHound helps with discovery and triage; always validate findings with additional context before treating a domain as a threat.

---

## Why NetHound?

- **Multi-TLD collection:** Supports `.IN`, `.COM`, and additional TLD datasets through the configured sources.
- **Python-based extraction:** Uses `pypdf` for PDF stream extraction without requiring external system binaries.
- **Historical search:** Search archived daily domain lists by keyword or regular expression.
- **Pipeline-friendly output:** Stream results to standard output or export structured JSON.
- **Security-tool workflows:** Pipe domain lists into tools such as `httpx` and `dnsx` for authorized investigation.
- **Linux packaging:** Includes Debian packaging files for building a package for Debian-based systems.

## Quick start

### Install from source

```bash
git clone https://github.com/xploitoverload/NetHound.git
cd NetHound
python -m pip install .
```

Check the installation:

```bash
nethound --version
nethound --help
```

You can also install directly from the repository:

```bash
python -m pip install git+https://github.com/xploitoverload/NetHound.git
```

## Usage

### 1. Fetch newly registered domains

Fetch the previous day's data for all supported TLD sources:

```bash
nethound fetch --tld all
```

Fetch only `.IN` domains for a specific date:

```bash
nethound fetch --tld in --date 2026-11-01
```

Fetch `.COM` domains:

```bash
nethound fetch --tld com --date 2026-11-01
```

Fetch a specific supported TLD:

```bash
nethound fetch --tld cn --date 2026-11-01
nethound fetch --tld shop --date 2026-11-01
```

### 2. Pipe results into other tools

Stream domains to standard output without status messages:

```bash
# Inspect HTTP services on newly registered .IN domains
nethound fetch --tld in --stdout | httpx -silent -title -status-code

# Resolve newly registered .COM domains
nethound fetch --tld com --stdout | dnsx -silent -a -resp
```

These examples are intended for authorized research and defensive monitoring.

### 3. Export JSON

```bash
nethound fetch --tld in --json
```

### 4. Search archived domains

Search for a keyword:

```bash
nethound search "paypal"
```

Search using a regular expression:

```bash
nethound search --regex "^login.*\\.com$"
```

Filter by TLD:

```bash
nethound search "binance" --tld com
```

Show the source file and matching line:

```bash
nethound search "kali" --verbose
```

### 5. View archive statistics

```bash
nethound stats
```

## Automated daily synchronization

The repository includes a GitHub Actions workflow scheduled for **09:00 IST (03:30 UTC)**. It attempts to collect the previous day's data and commit archive updates to the repository.

You can also trigger the workflow manually from the **Actions** tab.

## Repository layout

```text
NetHound/
├── in/                          # .IN domain archives
├── com/                         # .COM domain archives
├── others/                      # Other supported TLD archives
├── nethound/                    # Python CLI package
│   ├── cli.py                   # CLI entry point
│   ├── config.py                # Configuration and date parsing
│   ├── search.py                # Keyword and regex search
│   └── fetchers/                # Domain data extraction sources
├── debian/                      # Debian packaging files
└── .github/workflows/           # Scheduled synchronization
```

## Contributing

Bug reports, feature ideas, documentation improvements, and pull requests are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a change.

## Security and responsible use

Use NetHound only for lawful research and systems you are authorized to assess. Do not assume that a newly registered domain is malicious, and validate findings before acting on them. See [SECURITY.md](SECURITY.md) for reporting guidance.

## License

NetHound is licensed under the [MIT License](LICENSE).

## Author

Created and maintained by [xploitoverload](https://github.com/xploitoverload).

**Found NetHound useful?** Give the repository a star to help other researchers discover it, or open an issue with feedback and ideas.

[⭐ Star NetHound on GitHub](https://github.com/xploitoverload/NetHound)
