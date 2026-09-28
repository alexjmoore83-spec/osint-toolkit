# OSINT Framework // Cyber Intel Toolkit (AstrOsint)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Status: Active](https://img.shields.io/badge/Status-100%25%20Verified-00ffaa.svg)](#)
[![Interface: Web HUD](https://img.shields.io/badge/UI-Cyber%20HUD-00f0ff.svg)](#)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8+-ffaa00.svg)](#)
[![GitHub Pages](https://img.shields.io/badge/Deployment-GitHub%20Pages-9d4edd.svg)](https://alexjmoore83-spec.github.io/osint-toolkit/)

A high-grade, curated Open Source Intelligence (OSINT) framework and investigative toolkit. Designed for cybersecurity analysts, penetration testers, investigative journalists, and digital forensics researchers.

Featuring both an **interactive futuristic Web HUD** and a powerful **terminal CLI companion (AstrOSINT)**.

![Cyber Intelligence Global HUD Banner](./assets/cyber_intel_hero.jpg)

> 🌐 **Live Web Demo:** [https://alexjmoore83-spec.github.io/osint-toolkit/](https://alexjmoore83-spec.github.io/osint-toolkit/)

---

## ⚡ Key Features

### 🖥️ Web HUD Application (`index.html`)
- **124+ Curated & Verified OSINT Tools:** Spanning 24 operational sectors, filtered for active, functional web resources.
- **Dual Visual Themes:**
  - **Dark Cyber Matrix Mode:** Deep obsidian glass, neon cyan telemetry glow, and subtle ambient gradients.
  - **High-Contrast Bright Mode:** Crisp pure white surfaces with deep charcoal slate typography (`#090e1a` / `#334155`) for effortless daytime reading.
- **Live Sector Filtering:** Filter instantly by tool classification:
  - `(T)` **Local Install:** Command-line utilities & local packages.
  - `(D)` **Google Dork:** Targeted search syntax and indexing queries.
  - `(R)` **Registration Required:** Free tier services requiring accounts.
  - `(M)` **Manual URL:** Advanced URL manipulation and parameter tampering.
- **Instant Search & Hotkeys:** Real-time query matching across tool names, URLs, and descriptions with keyboard shortcut (`/` or `Cmd+K` / `Ctrl+K`).
- **1-Click Copy & Quick Launch:** Dedicated clipboard copy with HUD toast notifications and direct launch links.
- **Zero Dependencies:** Pure vanilla HTML5, CSS3, and modern JavaScript. No build steps, Node.js, or external frameworks required.

---

### 🐍 Terminal CLI Companion (`osint_cli.py` / AstrOSINT)
- **Target Tracking:** Save, manage, and investigate multiple targets across sessions.
- **Automated Tool Checks:** Detects installed system tools and provides auto-installation helpers (Homebrew, pip).
- **Automated Workflow:** Query APIs, perform DNS/Whois checks, reverse lookups, and export comprehensive investigation reports in HTML & JSON.

---

## 📂 Intelligence Categories Covered

| Category | Description | Featured Tools |
| :--- | :--- | :--- |
| **👤 Username Intelligence** | Enumerate identity footprints across social platforms | Sherlock, WhatsMyName, Namechk, Usersearch, Instant Username |
| **📧 Email Reconnaissance** | Verify deliverability, discover company formats & breaches | Hunter, Epieos, Phonebook, Email Checker, MXToolbox |
| **🌐 Domain & DNS** | Dig into DNS records, subdomains, reverse lookups | Shodan, Censys, Whois DomainTools, DNSlytics, ViewDNS |
| **📍 IP & Network** | Geo-locate addresses, autonomous systems, port audits | IPinfo, AbuseIPDB, WhatIsMyIP, MAC Vendor Lookup |
| **🖼️ Images & Media** | Reverse image search, video verification, metadata inspection | Jimpl, TinEye, InVID, ExifTool, Google Images |
| **📞 Telephone Numbers** | Caller identification, spam scoring, carrier lookups | TrueCaller, ThatsThem, NumVerify, CallerID |
| **🌑 Dark Web & Tor** | Onion search engines, verified service directories | Tor Browser, Ahmia, Tor Taxi, Dark.fail |
| **🛡️ Threat Intel & Malware** | Multi-engine file analysis, sandbox detonators, reputation checks | VirusTotal, AlienVault OTX, URLScan, Any.Run, Hybrid Analysis |
| **🔐 Encoding & Hashes** | Decode cyber artifacts, hash identification, rainbow tables | CyberChef, Hashes.com, URL Decode, Base64 Decode |
| **🤖 AI Intelligence** | Synthetic analysis, investigative prompting, automated research | ChatGPT, Claude, Perplexity, Gemini, Microsoft Copilot |
| **✈️ Transportation** | Real-time global flight, maritime, and train tracking | Flightradar24, FlightAware, MarineTraffic, Trainline |
| **🔒 OpSec & Security** | Breach monitoring, 2FA directory, password vaults | Have I Been Pwned, 2FA Directory, KeePassXC, EFF SSD |

---

## 🚀 Quick Start

### 1. Run the Web Interface
Simply double-click or open `index.html` in any modern web browser:

```bash
# macOS
open index.html

# Linux
xdg-open index.html

# Windows
start index.html
```

Or serve locally with Python:
```bash
python3 -m http.server 8000
# Open http://localhost:8000
```

### 2. Run the CLI Companion
```bash
python3 osint_cli.py
```

---

## 📁 Repository Structure

```
osint-toolkit/
├── index.html                  # Cyber Intel Framework Web HUD
├── assets/
│   └── cyber_intel_hero.jpg    # Holographic Global Operations visual
├── osint_cli.py                # AstrOSINT Python CLI tool
├── SPEC.md                     # Technical UI/UX design specifications
├── .gitignore                  # Git hygiene ignore rules
└── README.md                   # Project documentation
```

---

## ⚖️ Legal & Ethical Disclaimer

This toolkit is designed exclusively for authorized cybersecurity testing, educational research, academic investigations, and legal open-source intelligence gathering. Users are solely responsible for compliance with all applicable local, national, and international laws and terms of service. The developers assume no liability for misuse.
