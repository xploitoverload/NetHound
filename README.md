# NetHound 🐕
### Newly Registered Domains (NRDs) Tracker & Threat Intelligence Engine

[![Release](https://img.shields.io/badge/release-v1.0.0-blue.svg)](https://github.com/xploitoverload/NetHound/releases)
[![Daily Domain Fetch](https://github.com/xploitoverload/NetHound/actions/workflows/daily-domain-fetch.yml/badge.svg)](https://github.com/xploitoverload/NetHound/actions/workflows/daily-domain-fetch.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Platform: Linux | macOS | Windows](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg)](https://github.com/xploitoverload/NetHound)

**NetHound** is a fast, modular CLI tool and threat intelligence engine designed to monitor, extract, and search Newly Registered Domains (NRDs) across global registries (.IN, .COM, and hundreds of top-level domains).

Security teams, OSINT researchers, and penetration testers use newly registered domains to detect:
* **Phishing campaigns** and credential harvesting setups hours after registration.
* **Brand impersonation** and typosquatting attacks targeting organizations.
* **Malware C2 infrastructure** and fast-flux domains before active deployment.

---

## ✨ Features

* **Multi-Registry Tracking:** Native support for `.IN` (Registry.in), `.COM`, and hundreds of generic TLDs (`.cn`, `.shop`, `.top`, `.net`, `.xyz`, etc.).
* **Pure Python & Fast Extraction:** Uses high-performance `pypdf` stream extraction with zero external system binaries.
* **Built-in Search Engine:** Search through historical and daily domain lists by exact string or regular expressions (`nethound search`).
* **Unix Pipe Friendly:** Stream domains straight to stdout (`--stdout` / `-s`) to pipe into `httpx`, `dnsx`, `subfinder`, or `nuclei`.
* **Debian & Kali Linux Ready:** Native `debian/` packaging included out-of-the-box for inclusion in security distributions.

---

## 🚀 Installation

### Using pip
```bash
git clone https://github.com/xploitoverload/NetHound.git
cd NetHound
pip install .
```

Or install directly via Git:
```bash
pip install git+https://github.com/xploitoverload/NetHound.git
```

### Debian / Kali Linux Package Build
```bash
sudo apt install -y dh-python python3-all python3-requests python3-pypdf
cd NetHound
dpkg-buildpackage -us -uc -b
sudo dpkg -i ../nethound_1.0.0*.deb
```

---

## 🛠️ Usage

### 1. Fetching Domains (`nethound fetch`)

Fetch all domains from yesterday across all supported registries:
```bash
nethound fetch --tld all
```

Fetch only `.IN` newly registered domains for a specific date:
```bash
nethound fetch --tld in --date 2026-11-01
```

Fetch only `.COM` domains:
```bash
nethound fetch --tld com --date 2026-11-01
```

Fetch specific TLD (e.g. `.cn` or `.shop`):
```bash
nethound fetch --tld cn --date 2026-11-01
```

#### Pipeline Integration (Piping to Security Tools)
Stream domain names directly to standard output without status logs:
```bash
# Check live HTTP services on today's .in registrations
nethound fetch --tld in -s | httpx -silent -title -status-code

# Resolve DNS records for newly registered .com domains
nethound fetch --tld com -s | dnsx -silent -a -resp
```

Output as structured JSON:
```bash
nethound fetch --tld in --json
```

---

### 2. Searching NRD Records (`nethound search`)

Search for keyword occurrences (e.g., brand monitoring for "paypal" or "bank"):
```bash
nethound search "paypal"
```

Search with Regular Expressions (`-r` / `--regex`):
```bash
nethound search -r "^login.*\.com$"
```

Filter search by specific TLD:
```bash
nethound search "binance" --tld com
```

Print source files and line locations:
```bash
nethound search "kali" -V
```

---

### 3. Database Statistics (`nethound stats`)

View a statistical summary of all currently tracked domains and file distributions:
```bash
nethound stats
```

---

## 📂 Repository Data Structure

For researchers interested in automated historical archives, domain lists are structured as follows:

```text
NetHound/
├── in/                          # .IN Registry creations (yearly/monthly)
│   └── 2026/
│       └── 11/
│           └── domains_2026-11-01.txt
├── com/                         # .COM Newly Registered Domains
│   └── 2026/
│       └── 11/
│           └── domains_2026-11-01.txt
├── others/                      # Sub-partitioned per TLD
│   ├── cn/
│   ├── shop/
│   ├── top/
│   └── ...
├── nethound/                    # Core Python package
│   ├── cli.py                   # Main CLI entrypoint
│   ├── config.py                # Configurations & date parsers
│   ├── search.py                # Search and regex engine
│   └── fetchers/                # Registry & WhoisDS extraction engines
├── debian/                      # Official Debian/Kali packaging files
└── .github/workflows/           # Automated daily sync pipeline
```

---

## 🤖 Automated Daily Synchronization

NetHound runs an automated GitHub Action every morning at **09:00 AM IST (03:30 UTC)** to fetch, extract, and index all newly registered domain drops from global registries.

---

## 🛡️ License

This project is licensed under the [MIT License](LICENSE).

---

## 👤 Author

Developed by **[xploitoverload](https://github.com/xploitoverload)**.  
Contributions, issues, and feature requests are welcome!
