# NetHound - Newly Registered Domains (NRDs) Tracker

[![Daily Domain Fetch](https://github.com/xploitoverload/NetHound/actions/workflows/daily-domain-fetch.yml/badge.svg)](https://github.com/xploitoverload/NetHound/actions/workflows/daily-domain-fetch.yml)

Automated daily snapshots of Newly Registered Domains (NRDs) for **.IN**, **.COM**, and **other global TLDs** for threat intelligence, security operations, and OSINT research.

## Supported Registries

* **.IN NRDs (`in/`):** Automatically fetched from [.IN Registry](https://registry.in) daily domain creation reports via `fetch_registry_domains.py`.
* **.COM NRDs (`com/`):** Automatically extracted from daily registry newly registered domain archives via `fetch_com_domains.py`.
* **Other TLD NRDs (`others/`):** Automatically extracted newly registered domains for all other global extensions (.net, .org, .xyz, .top, .online, .site, etc.) via `fetch_other_domains.py`.

## Data Format and Structure

Domains are organized by TLD category, Year, and Month with one domain per line:

```text
NetHound/
├── in/
│   └── 2026/
│       └── 11/
│           └── domains_01-11-2026.txt
├── com/
│   └── 2026/
│       └── 11/
│           └── domains_2026-11-01.txt
├── others/
│   └── 2026/
│       └── 11/
│           └── domains_2026-11-01.txt
├── fetch_registry_domains.py   # .IN extractor
├── fetch_com_domains.py        # .COM extractor
├── fetch_other_domains.py      # Other TLDs extractor
├── fetch_nrd_domains.py        # Unified NRD extractor
└── .github/workflows/daily-domain-fetch.yml
```

## Automation

Domain archives are automatically fetched, extracted, and committed every morning at **9:00 AM IST (03:30 UTC)** via GitHub Actions (`daily-domain-fetch.yml`).

## Manual Execution

### Fetch .IN domains
```bash
python3 fetch_registry_domains.py [YYYY-MM-DD]
```

### Fetch .COM domains
```bash
python3 fetch_com_domains.py [YYYY-MM-DD]
```

### Fetch Other TLD domains
```bash
python3 fetch_other_domains.py [YYYY-MM-DD]
```

### Fetch Both .COM and Other TLDs simultaneously
```bash
python3 fetch_nrd_domains.py [YYYY-MM-DD]
```

## Reliability Notice & Disclaimer

- The maintainer makes no warranties regarding the completeness or accuracy of third-party registry feeds.
- Data is provided **AS-IS** for research and threat intelligence analysis.
- Not affiliated with registry.in or Verisign.

## License

All data and automation code in this repository are released under [The Unlicense](https://unlicense.org).
