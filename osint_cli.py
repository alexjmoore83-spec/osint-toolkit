#!/usr/bin/env python3
"""
AstrOSINT - Advanced OSINT Toolkit v2.0
A comprehensive OSINT research toolkit with integrated tools and services.
"""

import os
import sys
import json
import subprocess
import argparse
import time
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import configparser
import shutil

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# ==================== CONFIG ====================

class Config:
    """Configuration manager"""
    def __init__(self):
        self.config_dir = Path.home() / ".osint-toolkit"
        self.config_file = self.config_dir / "config.ini"
        self.api_keys_file = self.config_dir / "api_keys.json"
        self.targets_file = self.config_dir / "targets.json"
        self.history_file = self.config_dir / "history.json"
        self.output_dir = self.config_dir / "outputs"
        
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.load_config()
    
    def load_config(self):
        """Load or create config"""
        if not self.config_file.exists():
            self.create_default_config()
        
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)
    
    def create_default_config(self):
        """Create default config"""
        config = configparser.ConfigParser()
        config['General'] = {
            'default_output_dir': str(self.output_dir),
            'browser': 'default',
            'timeout': '60',
            'auto_install': 'true'
        }
        config['Reports'] = {
            'format': 'html',
            'include_screenshots': 'false'
        }
        
        with open(self.config_file, 'w') as f:
            config.write(f)
    
    def get(self, section, key, fallback=None):
        return self.config.get(section, key, fallback=fallback)
    
    def set(self, section, key, value):
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, value)
        with open(self.config_file, 'w') as f:
            self.config.write(f)

# ==================== API KEYS ====================

class APIKeyManager:
    """Manage API keys for premium services"""
    def __init__(self, config: Config):
        self.config = config
        self.keys = {}
        self.load()
    
    def load(self):
        if self.config.api_keys_file.exists():
            with open(self.config.api_keys_file, 'r') as f:
                self.keys = json.load(f)
        else:
            self.keys = {
                "virustotal": "",
                "shodan": "",
                "hunter": "",
                "alienvault": "",
                "zoomeye": "",
                "greynoise": ""
            }
            self.save()
    
    def save(self):
        with open(self.config.api_keys_file, 'w') as f:
            json.dump(self.keys, f, indent=2)
    
    def get(self, service: str) -> str:
        return self.keys.get(service, "")
    
    def set(self, service: str, key: str):
        self.keys[service] = key
        self.save()
    
    def list(self):
        return {k: v for k, v in self.keys.items() if v}

# ==================== TARGET MANAGER ====================

class TargetManager:
    """Manage OSINT targets"""
    def __init__(self, config: Config):
        self.config = config
        self.targets = {}
        self.load()
    
    def load(self):
        if self.config.targets_file.exists():
            with open(self.config.targets_file, 'r') as f:
                self.targets = json.load(f)
    
    def save(self):
        with open(self.config.targets_file, 'w') as f:
            json.dump(self.targets, f, indent=2)
    
    def add(self, name: str, target_type: str, value: str, notes: str = ""):
        self.targets[name] = {
            "type": target_type,
            "value": value,
            "notes": notes,
            "created": datetime.now().isoformat(),
            "last_scan": None,
            "scans": []
        }
        self.save()
    
    def get(self, name: str) -> Optional[dict]:
        return self.targets.get(name)
    
    def list(self):
        return self.targets
    
    def update_scan(self, name: str, scan_result: str):
        if name in self.targets:
            self.targets[name]["last_scan"] = datetime.now().isoformat()
            self.targets[name]["scans"].append({
                "date": datetime.now().isoformat(),
                "result": scan_result
            })
            self.save()
    
    def delete(self, name: str):
        if name in self.targets:
            del self.targets[name]
            self.save()

# ==================== REPORT GENERATOR ====================

class ReportGenerator:
    """Generate HTML reports"""
    def __init__(self, config: Config):
        self.config = config
    
    def generate(self, target: str, category: str, tool: str, results: str) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"OSINT_Report_{target}_{timestamp}.html"
        filepath = self.config.output_dir / filename
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OSINT Report - {target}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #eaeaea;
            min-height: 100vh;
            padding: 2rem;
        }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        header {{
            background: rgba(255,255,255,0.1);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 2rem;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        h1 {{
            font-size: 2rem;
            margin-bottom: 0.5rem;
            background: linear-gradient(90deg, #e94560, #ff6b8a);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .meta {{
            display: flex;
            gap: 2rem;
            color: #a0a0a0;
            font-size: 0.9rem;
        }}
        .section {{
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .section h2 {{
            color: #e94560;
            margin-bottom: 1rem;
            font-size: 1.2rem;
        }}
        .result {{
            background: #0f0f1a;
            border-radius: 8px;
            padding: 1rem;
            font-family: 'Consolas', monospace;
            font-size: 0.85-x: auto;
rem;
            overflow            white-space: pre-wrap;
            word-wrap: break-word;
        }}
        .badge {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            margin-right: 0.5rem;
        }}
        .badge-category {{ background: rgba(233,69,96,0.2); color: #e94560; }}
        .badge-tool {{ background: rgba(0,191,255,0.2); color: #00bfff; }}
        footer {{
            text-align: center;
            padding: 2rem;
            color: #666;
            font-size: 0.8rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔍 OSINT Investigation Report</h1>
            <div class="meta">
                <span>📅 {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</span>
                <span>🎯 Target: {target}</span>
                <span>📁 Category: {category}</span>
            </div>
        </header>
        
        <div class="section">
            <h2>Scan Details</h2>
            <p>
                <span class="badge badge-category">{category}</span>
                <span class="badge badge-tool">{tool}</span>
            </p>
        </div>
        
        <div class="section">
            <h2>Results</h2>
            <div class="result">{results}</div>
        </div>
        
        <footer>
            <p>Generated by AstrOSINT</p>
            <p>🔗 osintframework.com</p>
        </footer>
    </div>
</body>
</html>"""
        
        with open(filepath, 'w') as f:
            f.write(html)
        
        return str(filepath)

# ==================== TOOL INSTALLER ====================

class ToolInstaller:
    """Auto-install OSINT tools"""
    @staticmethod
    def check_go() -> bool:
        """Check if Go is installed"""
        result = subprocess.run(["which", "go"], capture_output=True)
        return result.returncode == 0
    
    @staticmethod
    def install(tool_name: str) -> bool:
        """Install a tool based on its name"""
        # Web alternatives for tools that require Go
        web_alternatives = {
            "subfinder": "https://subfinder.com/",
            "amass": "https://amass.com/",
            "assetfinder": "https://github.com/tomnomnom/assetfinder",
            "shodan": "https://shodan.io",
            "ffuf": "https://github.com/ffuf/ffuf",
            "naabu": "https://github.com/projectdiscovery/naabu",
            "httpx": "https://github.com/projectdiscovery/httpx",
            "nuclei": "https://github.com/projectdiscovery/nuclei"
        }
        
        installers = {
            "sherlock": "pip3 install sherlock-project",
            "subfinder": "go install -github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest",
            "amass": "go install -github.com/OWASP/Amass/v3/...@latest",
            "assetfinder": "go install -github.com/tomnomnom/assetfinder@latest",
            "shodan": "pip3 install shodan",
            "exiftool": "brew install exiftool",
            "recon-ng": "pip3 install recon-ng",
            "theharvester": "pip3 install theHarvester",
            "nmap": "brew install nmap",
            "wappalyzer": "npm install -g wappalyzer-cli",
            "wafw00f": "pip3 install wafw00f",
            "dirb": "brew install dirb",
            "ffuf": "go install -github.com/ffuf/ffuf@latest",
            "gf": "go install -github.com/tomnomnom/gf@latest",
            "naabu": "go install -github.com/projectdiscovery/naabu/v2/cmd/naabu@latest",
            "httpx": "go install -github.com/projectdiscovery/httpx/cmd/httpx@latest",
            " nuclei": "go install -github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest"
        }
        
        if tool_name.lower() not in installers:
            print(f"{Colors.YELLOW}No installer available for {tool_name}{Colors.ENDC}")
            return False
        
        # Check if Go is required but not installed
        tool_cmd = installers[tool_name.lower()]
        if "go install" in tool_cmd and not ToolInstaller.check_go():
            print(f"{Colors.YELLOW}Go is required to install {tool_name}{Colors.ENDC}")
            print(f"{Colors.CYAN}Install Go with: brew install go{Colors.ENDC}")
            if tool_name.lower() in web_alternatives:
                open_url(web_alternatives[tool_name.lower()])
                print(f"{Colors.GREEN}Opened web alternative in browser{Colors.ENDC}")
            return False
        
        cmd = installers[tool_name.lower()]
        print(f"{Colors.CYAN}Installing {tool_name}...{Colors.ENDC}")
        print(f"Command: {cmd}")
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
            if result.returncode == 0:
                print(f"{Colors.GREEN}✓ Successfully installed {tool_name}{Colors.ENDC}")
                return True
            else:
                print(f"{Colors.RED}✗ Installation failed: {result.stderr}{Colors.ENDC}")
                return False
        except Exception as e:
            print(f"{Colors.RED}✗ Error: {e}{Colors.ENDC}")
            return False

# ==================== UTILITY FUNCTIONS ====================

def print_banner():
    banner = f"""
{Colors.CYAN}
    █████╗ ██╗      ██████╗  ██████╗ ██████╗ ██╗██████╗ ███████╗██╗   ██╗
   ██╔══██╗██║     ██╔════╝ ██╔═══██╗██╔══██╗██║██╔══██╗██╔════╝██║   ██║
   ███████║██║     ██║  ███╗██║   ██║██████╔╝██║██║  ██║█████╗  ██║   ██║
   ██╔══██║██║     ██║   ██║██║   ██║██╔══██╗██║██║  ██║██╔══╝  ╚██╗ ██╔╝
   ██║  ██║███████╗╚██████╔╝╚██████╔╝██║  ██║██║██████╔╝███████╗ ╚████╔╝ 
   ╚═╝  ╚═╝╚══════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝╚═════╝ ╚══════╝  ╚═══╝  
                                                                       
   ██████╗ ███████╗██╗   ██╗
   ██╔══██╗██╔════╝██║   ██║
   ██║  ██║█████╗  ██║   ██║
   ██║  ██║██╔══╝  ╚██╗ ██╔╝
   ██████╔╝███████╗ ╚████╔╝ 
   ╚═════╝ ╚══════╝  ╚═══╝  

   {Colors.YELLOW}ASTROSINT - Advanced OSINT Toolkit v2.0{Colors.CYAN}
   {Colors.BLUE}═══════════════════════════════════════════
   🧠 Autonomous Intelligence Gathering Platform
{Colors.ENDC}
    """
    print(banner)

def print_category(title: str):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}  {title}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def run_command(cmd: List[str], description: str = "Running...", timeout: int = 60) -> tuple:
    """Run a shell command and return output"""
    print(f"{Colors.YELLOW}{description}{Colors.ENDC}")
    print(f"{Colors.CYAN}Command: {' '.join(cmd)}{Colors.ENDC}\n")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=isinstance(cmd, str)
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)

def open_url(url: str):
    """Open URL in default browser"""
    print(f"{Colors.GREEN}Opening: {url}{Colors.ENDC}")
    webbrowser.open(url)

def check_tool_installed(tool: str) -> bool:
    """Check if a tool is installed"""
    # Check using which command
    result = subprocess.run(
        ["which", tool],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        return True
    
    # Check in Python bin directory
    python_bin = subprocess.run(
        ["python3", "-c", "import sys; print(sys.executable.replace('/bin/python3', '/bin'))"],
        capture_output=True, text=True
    ).stdout.strip()
    if python_bin:
        result = subprocess.run(
            ["ls", f"{python_bin}/{tool}"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            return True
    
    # Check if pip package is installed
    result = subprocess.run(
        ["pip3", "show", tool],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        return True
    
    # Check with -m module
    result = subprocess.run(
        ["python3", "-m", tool, "--help"],
        capture_output=True, text=True, timeout=5
    )
    if result.returncode == 0:
        return True
    
    return False

def save_output(data: str, filename: str, output_dir: Path = None) -> str:
    """Save command output to file"""
    if output_dir is None:
        output_dir = Path.home() / ".osint-toolkit" / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    filepath = output_dir / filename
    with open(filepath, 'w') as f:
        f.write(data)
    
    print(f"{Colors.GREEN}Output saved to: {filepath}{Colors.ENDC}")
    return str(filepath)

# ==================== TOOL CATEGORIES ====================

TOOLS = {
    "Username OSINT": [
        {"name": "Sherlock", "description": "Hunt down social media accounts by username", "command": "sherlock {target}", "requires_install": True, "install_cmd": "pip3 install sherlock-project", "web": None},
        {"name": "Namechk", "description": "Check username availability across platforms", "command": None, "requires_install": False, "install_cmd": None, "web": "https://namechk.com"},
        {"name": "UserSearch", "description": "Reverse username lookup", "command": None, "requires_install": False, "install_cmd": None, "web": "https://usersearch.org"},
        {"name": "WhatsMyName", "description": "Username enumeration across websites", "command": None, "requires_install": False, "install_cmd": None, "web": "https://whatsmyname.app"}
    ],
    "Email OSINT": [
        {"name": "Phonebook", "description": "Email, username, and domain search", "command": None, "requires_install": False, "install_cmd": None, "web": "https://phonebook.cz"},
        {"name": "Hunter", "description": "Find email addresses for companies", "command": None, "requires_install": False, "install_cmd": None, "web": "https://hunter.io"},
        {"name": "Email Checker", "description": "Verify if email exists", "command": None, "requires_install": False, "install_cmd": None, "web": "https://email-checker.net"},
        {"name": "GRAVY", "description": "Email reconnaissance tool", "command": None, "requires_install": False, "install_cmd": None, "web": "https://grazy.xyz"}
    ],
    "Domain OSINT": [
        {"name": "Subfinder", "description": "Fast subdomain enumeration", "command": "subfinder -d {target}", "requires_install": True, "install_cmd": "go install -github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest", "web": "https://securitytrails.com"},
        {"name": "Amass", "description": "In-depth subdomain enumeration", "command": "amass enum -d {target}", "requires_install": True, "install_cmd": "go install -github.com/OWASP/Amass/v3/...@latest", "web": "https://dnsdumpster.com"},
        {"name": "Assetfinder", "description": "Find related domains and subdomains", "command": "assetfinder {target}", "requires_install": True, "install_cmd": "go install -github.com/tomnomnom/assetfinder@latest", "web": "https://crt.sh"},
        {"name": "Whois", "description": "Domain registration lookup", "command": "whois {target}", "requires_install": False, "install_cmd": None, "web": None},
        {"name": "DNSlytics", "description": "DNS and domain analysis", "command": None, "requires_install": False, "install_cmd": None, "web": "https://dnslytics.com"},
        {"name": "Shodan", "description": "Internet-connected devices search", "command": "shodan host {target}", "requires_install": True, "install_cmd": "pip3 install shodan", "web": "https://shodan.io"}
    ],
    "IP OSINT": [
        {"name": "IPInfo", "description": "IP address intelligence", "command": None, "requires_install": False, "install_cmd": None, "web": "https://ipinfo.io"},
        {"name": "AbuseIPDB", "description": "Check IP reputation", "command": None, "requires_install": False, "install_cmd": None, "web": "https://www.abuseipdb.com"},
        {"name": "Censys", "description": "Internet-wide scanning data", "command": None, "requires_install": False, "install_cmd": None, "web": "https://censys.io"},
        {"name": "BGPHe", "description": "IP to ASN mapping", "command": None, "requires_install": False, "install_cmd": None, "web": "https://bgp.he.net"}
    ],
    "Social Media OSINT": [
        {"name": "Social Searcher", "description": "Search social media platforms", "command": None, "requires_install": False, "install_cmd": None, "web": "https://www.social-searcher.com"},
        {"name": "Nitter", "description": "Twitter intelligence (web)", "command": None, "requires_install": False, "install_cmd": None, "web": "https://nitter.net"},
        {"name": "Social Blade", "description": "Social media statistics", "command": None, "requires_install": False, "install_cmd": None, "web": "https://socialblade.com"},
        {"name": "SparkToro", "description": "Audience research", "command": None, "requires_install": False, "install_cmd": None, "web": "https://sparktoro.com"}
    ],
    "Search Engines": [
        {"name": "Google", "description": "Google search", "command": None, "requires_install": False, "install_cmd": None, "web": "https://google.com"},
        {"name": "DuckDuckGo", "description": "Privacy-focused search", "command": None, "requires_install": False, "install_cmd": None, "web": "https://duckduckgo.com"},
        {"name": "Bing", "description": "Microsoft search", "command": None, "requires_install": False, "install_cmd": None, "web": "https://www.bing.com"},
        {"name": "Yandex", "description": "Russian search engine", "command": None, "requires_install": False, "install_cmd": None, "web": "https://yandex.com"},
        {"name": "Baidu", "description": "Chinese search engine", "command": None, "requires_install": False, "install_cmd": None, "web": "https://www.baidu.com"}
    ],
    "Image/Video OSINT": [
        {"name": "Google Images", "description": "Reverse image search", "command": None, "requires_install": False, "install_cmd": None, "web": "https://images.google.com"},
        {"name": "Yandex Images", "description": "Reverse image search", "command": None, "requires_install": False, "install_cmd": None, "web": "https://yandex.com/images"},
        {"name": "TinEye", "description": "Reverse image search", "command": None, "requires_install": False, "install_cmd": None, "web": "https://tineye.com"},
        {"name": "InVID", "description": "Video verification tool", "command": None, "requires_install": False, "install_cmd": None, "web": "https://www.invid-project.eu"}
    ],
    "People Search": [
        {"name": "Pipl", "description": "People search engine", "command": None, "requires_install": False, "install_cmd": None, "web": "https://pipl.com"},
        {"name": "TruePeopleSearch", "description": "Free people finder", "command": None, "requires_install": False, "install_cmd": None, "web": "https://truepeoplesearch.com"},
        {"name": "LinkedIn", "description": "Professional network search", "command": None, "requires_install": False, "install_cmd": None, "web": "https://linkedin.com"},
        {"name": "Spokeo", "description": "People search engine", "command": None, "requires_install": False, "install_cmd": None, "web": "https://www.spokeo.com"}
    ],
    "Phone OSINT": [
        {"name": "TrueCaller", "description": "Caller ID and spam blocking", "command": None, "requires_install": False, "install_cmd": None, "web": "https://www.truecaller.com"},
        {"name": "CallerID", "description": "Phone number information", "command": None, "requires_install": False, "install_cmd": None, "web": "https://www.callerid.com"},
        {"name": "NumVerify", "description": "Phone number validation", "command": None, "requires_install": False, "install_cmd": None, "web": "https://numverify.com"}
    ],
    "Geolocation": [
        {"name": "Google Maps", "description": "Maps and satellite imagery", "command": None, "requires_install": False, "install_cmd": None, "web": "https://www.google.com/maps"},
        {"name": "Google Earth", "description": "Satellite and aerial imagery", "command": None, "requires_install": False, "install_cmd": None, "web": "https://earth.google.com"},
        {"name": "OpenStreetMap", "description": "Open source maps", "command": None, "requires_install": False, "install_cmd": None, "web": "https://www.openstreetmap.org"},
        {"name": "Flightradar24", "description": "Real-time aircraft tracking", "command": None, "requires_install": False, "install_cmd": None, "web": "https://www.flightradar24.com"},
        {"name": "MarineTraffic", "description": "Ship tracking", "command": None, "requires_install": False, "install_cmd": None, "web": "https://www.marinetraffic.com"}
    ],
    "Archives": [
        {"name": "Wayback Machine", "description": "Historical web snapshots", "command": None, "requires_install": False, "install_cmd": None, "web": "https://web.archive.org"},
        {"name": "Archive.is", "description": "Web page archiving", "command": None, "requires_install": False, "install_cmd": None, "web": "https://archive.is"},
        {"name": "Performing", "description": "Twitter/X archive search", "command": None, "requires_install": False, "install_cmd": None, "web": "https://performing.lol"}
    ],
    "Dark Web": [
        {"name": "Tor Browser", "description": "Access onion sites", "command": None, "requires_install": False, "install_cmd": None, "web": "https://www.torproject.org"},
        {"name": "Ahmia", "description": "Search engine for onion sites", "command": None, "requires_install": False, "install_cmd": None, "web": "https://ahmia.fi"},
        {"name": "DarkSearch", "description": "Dark web search engine", "command": None, "requires_install": False, "install_cmd": None, "web": "https://darksearch.io"}
    ],
    "Crypto/Blockchain": [
        {"name": "Blockchain Explorer", "description": "Bitcoin block explorer", "command": None, "requires_install": False, "install_cmd": None, "web": "https://blockchain.com/explorer"},
        {"name": "Etherscan", "description": "Ethereum block explorer", "command": None, "requires_install": False, "install_cmd": None, "web": "https://etherscan.io"},
        {"name": "Blockchair", "description": "Multi-cryptocurrency explorer", "command": None, "requires_install": False, "install_cmd": None, "web": "https://blockchair.com"}
    ],
    "Threat Intelligence": [
        {"name": "VirusTotal", "description": "Analyze suspicious files and URLs", "command": None, "requires_install": False, "install_cmd": None, "web": "https://www.virustotal.com"},
        {"name": "AlienVault OTX", "description": "Threat intelligence platform", "command": None, "requires_install": False, "install_cmd": None, "web": "https://otx.alienvault.com"},
        {"name": "URLScan", "description": "URL scanner and sandbox", "command": None, "requires_install": False, "install_cmd": None, "web": "https://urlscan.io"},
        {"name": "Hybrid Analysis", "description": "Advanced malware analysis", "command": None, "requires_install": False, "install_cmd": None, "web": "https://www.hybrid-analysis.com"},
        {"name": "Any.Run", "description": "Interactive malware analysis", "command": None, "requires_install": False, "install_cmd": None, "web": "https://any.run"}
    ],
    "Malware Analysis": [
        {"name": "Joe Sandbox", "description": "Malware analysis sandbox", "command": None, "requires_install": False, "install_cmd": None, "web": "https://www.joesandbox.com"},
        {"name": "Any.Run", "description": "Online malware sandbox", "command": None, "requires_install": False, "install_cmd": None, "web": "https://any.run"},
        {"name": "Detux", "description": "Linux malware sandbox", "command": None, "requires_install": False, "install_cmd": None, "web": "https://detux.org"}
    ],
    "Metadata": [
        {"name": "Exif Online", "description": "Online EXIF viewer", "command": None, "requires_install": False, "install_cmd": None, "web": "https://exif.regex.info"},
        {"name": "Jeffrey's EXIF", "description": "EXIF metadata viewer", "command": None, "requires_install": False, "install_cmd": None, "web": "https://exif.regex.info"},
        {"name": "Metadeta", "description": "Metadata extraction", "command": None, "requires_install": False, "install_cmd": None, "web": "https://metadeta.com"}
    ],
    "Encoding/Decoding": [
        {"name": "CyberChef", "description": "Data encoding/decoding tool", "command": None, "requires_install": False, "install_cmd": None, "web": "https://gchq.github.io/CyberChef"},
        {"name": "URL Decode", "description": "URL encoding/decoding", "command": None, "requires_install": False, "install_cmd": None, "web": "https://www.urldecoder.org"},
        {"name": "Base64 Decode", "description": "Base64 encode/decode", "command": None, "requires_install": False, "install_cmd": None, "web": "https://www.base64decode.org"}
    ],
    "Automation Tools": [
        {"name": "SpiderFoot", "description": "Automated OSINT (GitHub)", "command": None, "requires_install": False, "install_cmd": None, "web": "https://github.com/smicallef/spiderfoot"},
        {"name": "Recon-ng", "description": "Web reconnaissance (GitHub)", "command": None, "requires_install": False, "install_cmd": None, "web": "https://github.com/lanmaster53/recon-ng"},
        {"name": "theHarvester", "description": "Email enumeration (GitHub)", "command": None, "requires_install": False, "install_cmd": None, "web": "https://github.com/laramies/theHarvester"},
        {"name": "Maltego", "description": "Interactive OSINT tool", "command": None, "requires_install": False, "install_cmd": None, "web": "https://www.maltego.com"}
    ],
    "Business Records": [
        {"name": "Crunchbase", "description": "Business and funding data", "command": None, "requires_install": False, "install_cmd": None, "web": "https://www.crunchbase.com"},
        {"name": "OpenCorporates", "description": "Global company registry", "command": None, "requires_install": False, "install_cmd": None, "web": "https://opencorporates.com"},
        {"name": "LinkedIn", "description": "Company and employee research", "command": None, "requires_install": False, "install_cmd": None, "web": "https://linkedin.com"}
    ],
    "Public Records": [
        {"name": "PACER", "description": "US federal court records", "command": None, "requires_install": False, "install_cmd": None, "web": "https://pacer.uscourts.gov"},
        {"name": "GovInfo", "description": "US government publications", "command": None, "requires_install": False, "install_cmd": None, "web": "https://www.govinfo.gov"},
        {"name": "FOIA", "description": "Freedom of Information Act", "command": None, "requires_install": False, "install_cmd": None, "web": "https://www.foia.gov"}
    ],
    "Exploits/CVE": [
        {"name": "CVE", "description": "Common Vulnerabilities database", "command": None, "requires_install": False, "install_cmd": None, "web": "https://cve.mitre.org"},
        {"name": "NVD", "description": "National Vulnerability Database", "command": None, "requires_install": False, "install_cmd": None, "web": "https://nvd.nist.gov"},
        {"name": "Exploit-DB", "description": "Exploit database", "command": None, "requires_install": False, "install_cmd": None, "web": "https://www.exploit-db.com"},
        {"name": "PacketStorm", "description": "Security advisories", "command": None, "requires_install": False, "install_cmd": None, "web": "https://packetstormsecurity.com"}
    ],
    "Training": [
        {"name": "IntelTechniques", "description": "OSINT training and tools", "command": None, "requires_install": False, "install_cmd": None, "web": "https://inteltechniques.com"},
        {"name": "Trace Labs", "description": "OSINT CTF platform", "command": None, "requires_install": False, "install_cmd": None, "web": "https://www.tracelabs.org"},
        {"name": "OSINT Dojo", "description": "OSINT training platform", "command": None, "requires_install": False, "install_cmd": None, "web": "https://www.osintdojo.com"}
    ],
    "OpSec/Privacy": [
        {"name": "Have I Been Pwned", "description": "Check email in breaches", "command": None, "requires_install": False, "install_cmd": None, "web": "https://haveibeenpwned.com"},
        {"name": "2FA Directory", "description": "Sites with 2FA", "command": None, "requires_install": False, "install_cmd": None, "web": "https://2fa.directory"},
        {"name": "EFF Surveillance", "description": "Digital security guides", "command": None, "requires_install": False, "install_cmd": None, "web": "https://ssd.eff.org"}
    ]
}

# ==================== CLI FUNCTIONS ====================

def list_categories():
    """List all available categories"""
    print_category("Available OSINT Categories")
    categories = list(TOOLS.keys())
    for i, cat in enumerate(categories, 1):
        tool_count = len(TOOLS[cat])
        print(f"  {Colors.CYAN}[{i:2d}]{Colors.ENDC} {Colors.BOLD}{cat}{Colors.ENDC} ({tool_count} tools)")
    print()

def list_tools_in_category(category: str):
    """List all tools in a category"""
    if category not in TOOLS:
        print(f"{Colors.RED}Category not found!{Colors.ENDC}")
        return
    
    print_category(category)
    tools = TOOLS[category]
    for i, tool in enumerate(tools, 1):
        status = ""
        if tool["requires_install"]:
            if tool["command"]:
                cmd_name = tool["command"].split()[0]
                if check_tool_installed(cmd_name):
                    status = f" {Colors.GREEN}[✓ INSTALLED]{Colors.ENDC}"
                else:
                    status = f" {Colors.YELLOW}[✗ NOT INSTALLED]{Colors.ENDC}"
        
        web_indicator = " 🌐" if tool["web"] else " 💻"
        print(f"  {Colors.CYAN}[{i:2d}]{Colors.ENDC} {Colors.BOLD}{tool['name']}{Colors.ENDC}{web_indicator}{status}")
        print(f"      {tool['description']}")
        print()

def run_tool(config: Config, api_manager: APIKeyManager, target_manager: TargetManager, report_gen: ReportGenerator, category: str, tool_index: int, target: str = None):
    """Run a specific tool"""
    if category not in TOOLS:
        print(f"{Colors.RED}Category not found!{Colors.ENDC}")
        return
    
    tools = TOOLS[category]
    if tool_index < 1 or tool_index > len(tools):
        print(f"{Colors.RED}Invalid tool index!{Colors.ENDC}")
        return
    
    tool = tools[tool_index - 1]
    print(f"\n{Colors.BOLD}Running: {tool['name']}{Colors.ENDC}")
    print(f"Description: {tool['description']}\n")
    
    # Check if it's a web tool
    if tool["web"]:
        url = tool["web"]
        if target:
            if "{" in url:
                url = url.replace("{target}", target)
            else:
                url = f"{url}/search?q={target}"
        open_url(url)
        print(f"{Colors.GREEN}Opened in browser!{Colors.ENDC}")
        return
    
    if not tool["command"]:
        print(f"{Colors.RED}No command available for this tool.{Colors.ENDC}")
        return
    
    cmd_parts = tool["command"].split()
    cmd_name = cmd_parts[0]
    
    if not check_tool_installed(cmd_name):
        print(f"{Colors.YELLOW}Tool not installed: {cmd_name}{Colors.ENDC}")
        
        # Check if stdin is interactive
        try:
            import sys
            is_interactive = sys.stdin.isatty()
        except:
            is_interactive = False
        
        # Auto-install option (only in interactive mode)
        if is_interactive and config.get('General', 'auto_install', fallback='true').lower() == 'true':
            install = input(f"{Colors.CYAN}Auto-install {cmd_name}? (y/n): {Colors.ENDC}").strip().lower()
            if install == 'y':
                ToolInstaller.install(cmd_name)
                # Check again after install
                if not check_tool_installed(cmd_name):
                    print(f"{Colors.RED}Installation failed or incomplete{Colors.ENDC}")
            elif tool["web"]:
                print(f"{Colors.CYAN}Opening web version instead...{Colors.ENDC}")
                open_url(tool["web"])
                return
            else:
                print(f"{Colors.YELLOW}Skipping.{Colors.ENDC}")
                return
        else:
            # Non-interactive: just use web version if available
            if tool["web"]:
                print(f"{Colors.CYAN}Opening web version...{Colors.ENDC}")
                open_url(tool["web"])
            else:
                print(f"{Colors.YELLOW}Tool not available. Install with: pip3 install {cmd_name}{Colors.ENDC}")
            return
        
        # Check if tool is now installed
        if not check_tool_installed(cmd_name):
            if tool["web"]:
                print(f"{Colors.CYAN}Using web version instead...{Colors.ENDC}")
                open_url(tool["web"])
                return
            else:
                print(f"{Colors.RED}Tool still not installed. Skipping.{Colors.ENDC}")
                return
    
    cmd = tool["command"]
    if target:
        cmd = cmd.replace("{target}", target)
    
    cmd_list = cmd.split()
    
    timeout = int(config.get('General', 'timeout', fallback='60'))
    returncode, stdout, stderr = run_command(cmd_list, f"Running {tool['name']}...", timeout=timeout)
    
    output = stdout + "\n" + stderr
    
    if stdout:
        print(stdout)
    if stderr:
        print(f"{Colors.RED}{stderr}{Colors.ENDC}")
    
    # Save output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"{tool['name']}_{timestamp}.txt"
    save_output(output, output_file, config.output_dir)
    
    # Generate report
    report_path = report_gen.generate(target or "N/A", category, tool['name'], output)
    print(f"{Colors.CYAN}Report: {report_path}{Colors.ENDC}")
    
    # Update target history
    if target:
        target_manager.update_scan(target, f"{category}: {tool['name']}")
    
    print(f"\n{Colors.GREEN}Done!{Colors.ENDC}")

def quick_search(query: str):
    """Quick search using various OSINT sources"""
    print_category("Quick OSINT Search")
    print(f"Searching for: {Colors.BOLD}{query}{Colors.ENDC}\n")
    
    searches = [
        ("Google", f"https://google.com/search?q={query}"),
        ("DuckDuckGo", f"https://duckduckgo.com/?q={query}"),
        ("Wayback Machine", f"https://web.archive.org/web/*/{query}"),
        ("VirusTotal", f"https://www.virustotal.com/gui/search/{query}"),
        ("Shodan", f"https://www.shodan.io/search?query={query}"),
    ]
    
    for name, url in searches:
        print(f"  {Colors.CYAN}[{name}]{Colors.ENDC}")
        open_url(url)
        time.sleep(0.3)
    
    print(f"\n{Colors.GREEN}Opened {len(searches)} search pages!{Colors.ENDC}")

def spiderfoot_scan(target: str, config: Config):
    """Run SpiderFoot scan"""
    print_category("SpiderFoot Scan")
    
    if not check_tool_installed("sfcli"):
        print(f"{Colors.YELLOW}SpiderFoot CLI not installed.{Colors.ENDC}")
        print(f"{Colors.CYAN}Opening SpiderFoot on GitHub (self-hosted)...{Colors.ENDC}")
        open_url(f"https://github.com/smicallef/spiderfoot")
        print(f"{Colors.GREEN}Opened SpiderFoot GitHub in browser!{Colors.ENDC}")
        return
    
    print(f"{Colors.BOLD}Starting SpiderFoot scan for: {target}{Colors.ENDC}\n")
    
    cmd = ["sfcli", "-s", target]
    timeout = int(config.get('General', 'timeout', fallback='300'))
    returncode, stdout, stderr = run_command(cmd, "Running SpiderFoot...", timeout=timeout)
    
    if stdout:
        print(stdout)
    if stderr:
        print(f"{Colors.RED}{stderr}{Colors.ENDC}")

def check_installed_tools():
    """Check which tools are installed"""
    print_category("Installed Tools Check")
    
    installed = []
    not_installed = []
    
    for category, tools in TOOLS.items():
        for tool in tools:
            if tool["command"]:
                cmd_name = tool["command"].split()[0]
                if check_tool_installed(cmd_name):
                    installed.append((category, tool["name"]))
                else:
                    not_installed.append((category, tool["name"]))
    
    print(f"{Colors.GREEN}✓ INSTALLED ({len(installed)}):{Colors.ENDC}")
    for cat, name in installed:
        print(f"  • {name} ({cat})")
    
    print(f"\n{Colors.YELLOW}✗ NOT INSTALLED ({len(not_installed)}):{Colors.ENDC}")
    for cat, name in not_installed:
        print(f"  • {name} ({cat})")
    
    print()

def manage_api_keys(api_manager: APIKeyManager):
    """Manage API keys"""
    print_category("API Key Manager")
    
    while True:
        print(f"{Colors.CYAN}[1]{Colors.ENDC} View configured keys")
        print(f"{Colors.CYAN}[2]{Colors.ENDC} Set a key")
        print(f"{Colors.CYAN}[3]{Colors.ENDC} Clear a key")
        print(f"{Colors.CYAN}[Q]{Colors.ENDC} Back")
        
        choice = input(f"\n{Colors.CYAN}Select: {Colors.ENDC}").strip().lower()
        
        if choice == '1':
            keys = api_manager.list()
            if keys:
                for service, key in keys.items():
                    print(f"  {service}: {key[:10]}...")
            else:
                print("  No API keys configured.")
        
        elif choice == '2':
            service = input("Service (virustotal/shodan/hunter/alienvault/greynoise): ").strip().lower()
            key = input(f"API key for {service}: ").strip()
            api_manager.set(service, key)
            print(f"{Colors.GREEN}Saved!{Colors.ENDC}")
        
        elif choice == '3':
            service = input("Service to clear: ").strip().lower()
            api_manager.set(service, "")
            print(f"{Colors.GREEN}Cleared!{Colors.ENDC}")
        
        elif choice == 'q':
            break

def manage_targets(target_manager: TargetManager):
    """Manage OSINT targets"""
    print_category("Target Manager")
    
    while True:
        print(f"{Colors.CYAN}[1]{Colors.ENDC} List targets")
        print(f"{Colors.CYAN}[2]{Colors.ENDC} Add target")
        print(f"{Colors.CYAN}[3]{Colors.ENDC} View target details")
        print(f"{Colors.CYAN}[4]{Colors.ENDC} Delete target")
        print(f"{Colors.CYAN}[Q]{Colors.ENDC} Back")
        
        choice = input(f"\n{Colors.CYAN}Select: {Colors.ENDC}").strip().lower()
        
        if choice == '1':
            targets = target_manager.list()
            if targets:
                for name, data in targets.items():
                    print(f"  • {name} ({data['type']}): {data['value']}")
            else:
                print("  No targets saved.")
        
        elif choice == '2':
            name = input("Target name: ").strip()
            target_type = input("Type (domain/email/username/ip): ").strip()
            value = input(f"{target_type}: ").strip()
            notes = input("Notes (optional): ").strip()
            target_manager.add(name, target_type, value, notes)
            print(f"{Colors.GREEN}Target added!{Colors.ENDC}")
        
        elif choice == '3':
            name = input("Target name: ").strip()
            target = target_manager.get(name)
            if target:
                print(f"\nName: {name}")
                print(f"Type: {target['type']}")
                print(f"Value: {target['value']}")
                print(f"Notes: {target['notes']}")
                print(f"Created: {target['created']}")
                print(f"Last scan: {target['last_scan']}")
            else:
                print(f"{Colors.RED}Target not found!{Colors.ENDC}")
        
        elif choice == '4':
            name = input("Target name to delete: ").strip()
            target_manager.delete(name)
            print(f"{Colors.GREEN}Deleted!{Colors.ENDC}")
        
        elif choice == 'q':
            break

def install_all_tools():
    """Install all available tools"""
    print_category("Install All Tools")
    
    print(f"{Colors.YELLOW}This will attempt to install all OSINT tools.{Colors.ENDC}")
    print(f"{Colors.YELLOW}Some tools require: Go, Node.js, or Homebrew.{Colors.ENDC}")
    print()
    
    confirm = input(f"{Colors.CYAN}Continue? (y/n): {Colors.ENDC}").strip().lower()
    if confirm != 'y':
        print(f"{Colors.YELLOW}Cancelled.{Colors.ENDC}")
        return
    
    print(f"\n{Colors.CYAN}Checking prerequisites...{Colors.ENDC}")
    
    # Check and install Homebrew if not present
    def check_brew() -> bool:
        result = subprocess.run(["which", "brew"], capture_output=True)
        return result.returncode == 0
    
    if not check_brew():
        print(f"{Colors.YELLOW}⚠ Homebrew not installed. Installing...{Colors.ENDC}")
        print(f"  Running: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
        print(f"  {Colors.CYAN}(You may need to enter your password){Colors.ENDC}")
        result = subprocess.run(
            ["/bin/bash", "-c", "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"],
            capture_output=True, text=True, shell=True
        )
        if check_brew():
            print(f"  ✓ Homebrew installed!")
        else:
            print(f"  ✗ Failed. Try manually:")
            print(f"  /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
            return
    else:
        print(f"  ✓ Homebrew installed")
    
    # Check for Go
    has_go = ToolInstaller.check_go()
    if not has_go:
        print(f"{Colors.YELLOW}⚠ Go not installed. Installing automatically...{Colors.ENDC}")
        print(f"  Running: brew install go")
        result = subprocess.run(["brew", "install", "go"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✓ Go installed successfully!")
            has_go = True
        else:
            print(f"  ✗ Failed to install Go. Install manually: brew install go")
    
    # Check for Node.js
    result = subprocess.run(["which", "node"], capture_output=True)
    has_node = result.returncode == 0
    if not has_node:
        print(f"{Colors.YELLOW}⚠ Node.js not installed. Installing...{Colors.ENDC}")
        result = subprocess.run(["brew", "install", "node"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✓ Node.js installed!")
            has_node = True
        else:
            print(f"  ✗ Failed. Install manually: brew install node")
    
    # Tools to install via pip3 (working packages)
    pip_tools = ["shodan", "wafw00f", "sherlock-project"]
    # Tools to install via brew
    brew_tools = ["exiftool", "nmap", "dirb", "go"]
    # Tools to install via Go (if available)
    go_tools = ["subfinder", "amass", "assetfinder", "ffuf"]
    
    print(f"\n{Colors.CYAN}Installing pip3 tools...{Colors.ENDC}")
    for tool in pip_tools:
        print(f"  Installing {tool}...", end=" ")
        result = subprocess.run(f"pip3 install {tool}".split(), capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓")
        else:
            print(f"✗ (skipping)")
    
    print(f"\n{Colors.CYAN}Installing Go tools...{Colors.ENDC}")
    if has_go:
        for tool in go_tools:
            print(f"  Installing {tool}...", end=" ")
            result = subprocess.run(f"go install -github.com/projectdiscovery/{tool}/v2/cmd/{tool}@latest".split(), capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓")
            else:
                print(f"✗")
    else:
        print(f"  {Colors.YELLOW}Skipped - Go not installed{Colors.ENDC}")
    
    print(f"\n{Colors.GREEN}════════════════════════════════════{Colors.ENDC}")
    print(f"{Colors.CYAN}To install remaining tools, run:{Colors.ENDC}")
    print(f"  brew install {' '.join(brew_tools)}")
    print(f"{Colors.GREEN}════════════════════════════════════{Colors.ENDC}")
    
    print(f"\n{Colors.GREEN}Installation complete!{Colors.ENDC}")
    print(f"{Colors.CYAN}Run --check to see what's installed.{Colors.ENDC}")

def interactive_menu(config: Config, api_manager: APIKeyManager, target_manager: TargetManager, report_gen: ReportGenerator):
    """Interactive menu mode"""
    while True:
        print_banner()
        print(f"{Colors.GREEN}[1]{Colors.ENDC} List all categories")
        print(f"{Colors.GREEN}[2]{Colors.ENDC} Quick search")
        print(f"{Colors.GREEN}[3]{Colors.ENDC} SpiderFoot scan")
        print(f"{Colors.GREEN}[4]{Colors.ENDC} Check installed tools")
        print(f"{Colors.GREEN}[5]{Colors.ENDC} Run tool")
        print(f"{Colors.GREEN}[6]{Colors.ENDC} Target manager")
        print(f"{Colors.GREEN}[7]{Colors.ENDC} API keys")
        print(f"{Colors.GREEN}[8]{Colors.ENDC} Settings")
        print(f"{Colors.YELLOW}[9]{Colors.ENDC} Install all tools")
        print(f"{Colors.GREEN}[Q]{Colors.ENDC} Quit")
        print()
        
        choice = input(f"{Colors.CYAN}Select option: {Colors.ENDC}").strip().lower()
        
        if choice == '1':
            list_categories()
            cat_input = input(f"{Colors.CYAN}Enter category number to view (or 'b'): {Colors.ENDC}").strip()
            if cat_input.lower() != 'b':
                try:
                    idx = int(cat_input)
                    categories = list(TOOLS.keys())
                    if 1 <= idx <= len(categories):
                        category = categories[idx - 1]
                        list_tools_in_category(category)
                except ValueError:
                    pass
        
        elif choice == '2':
            query = input(f"{Colors.CYAN}Enter search query: {Colors.ENDC}").strip()
            if query:
                quick_search(query)
        
        elif choice == '3':
            target = input(f"{Colors.CYAN}Enter target: {Colors.ENDC}").strip()
            if target:
                spiderfoot_scan(target, config)
        
        elif choice == '4':
            check_installed_tools()
        
        elif choice == '5':
            list_categories()
            cat_input = input(f"{Colors.CYAN}Enter category number: {Colors.ENDC}").strip()
            try:
                idx = int(cat_input)
                categories = list(TOOLS.keys())
                if 1 <= idx <= len(categories):
                    category = categories[idx - 1]
                    list_tools_in_category(category)
                    
                    tool_input = input(f"{Colors.CYAN}Enter tool number: {Colors.ENDC}").strip()
                    target = input(f"{Colors.CYAN}Enter target (optional): {Colors.ENDC}").strip()
                    
                    run_tool(config, api_manager, target_manager, report_gen, category, int(tool_input), target if target else None)
            except (ValueError, KeyError):
                print(f"{Colors.RED}Invalid input!{Colors.ENDC}")
        
        elif choice == '6':
            manage_targets(target_manager)
        
        elif choice == '7':
            manage_api_keys(api_manager)
        
        elif choice == '8':
            print_category("Settings")
            print(f"Config file: {config.config_file}")
            print(f"Output dir: {config.output_dir}")
            print(f"Auto-install: {config.get('General', 'auto_install', fallback='true')}")
            print(f"Timeout: {config.get('General', 'timeout', fallback='60')}")
            print()
        
        elif choice == '9':
            install_all_tools()
        
        elif choice == 'q':
            print(f"\n{Colors.CYAN}Goodbye! 👽{Colors.ENDC}\n")
            break
        
        input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.ENDC}")

def main():
    # Initialize
    config = Config()
    api_manager = APIKeyManager(config)
    target_manager = TargetManager(config)
    report_gen = ReportGenerator(config)
    
    parser = argparse.ArgumentParser(
        description="🔭 AstrOSINT - Advanced OSINT Toolkit v2.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  osint -l                           List all categories
  osint -c "Domain OSINT"            List tools in category
  osint -c "Domain OSINT" -t 1       Run tool #1 in Domain OSINT
  osint -c "Domain OSINT" -t 2 -s example.com
  osint -q "target.com"              Quick search
  osint -i                           Interactive menu
  osint -sf example.com              SpiderFoot scan
  osint --check                      Check installed tools
  osint --targets                    Manage targets
  osint --api                        Manage API keys
        """
    )
    
    parser.add_argument("-l", "--list", action="store_true", help="List all categories")
    parser.add_argument("-c", "--category", type=str, help="Category name")
    parser.add_argument("-t", "--tool", type=int, help="Tool number in category")
    parser.add_argument("-s", "--target", type=str, help="Target for the tool")
    parser.add_argument("-q", "--quick", type=str, help="Quick search")
    parser.add_argument("-i", "--interactive", action="store_true", help="Interactive menu")
    parser.add_argument("-sf", "--spiderfoot", type=str, help="Run SpiderFoot scan")
    parser.add_argument("--check", action="store_true", help="Check installed tools")
    parser.add_argument("--targets", action="store_true", help="Manage targets")
    parser.add_argument("--api", action="store_true", help="Manage API keys")
    parser.add_argument("--install", type=str, help="Install a tool by name")
    
    args = parser.parse_args()
    
    # Interactive mode
    if args.interactive:
        interactive_menu(config, api_manager, target_manager, report_gen)
        return
    
    # List categories
    if args.list:
        list_categories()
        return
    
    # Quick search
    if args.quick:
        quick_search(args.quick)
        return
    
    # SpiderFoot scan
    if args.spiderfoot:
        spiderfoot_scan(args.spiderfoot, config)
        return
    
    # Check installed tools
    if args.check:
        check_installed_tools()
        return
    
    # Manage targets
    if args.targets:
        manage_targets(target_manager)
        return
    
    # Manage API keys
    if args.api:
        manage_api_keys(api_manager)
        return
    
    # Install tool
    if args.install:
        ToolInstaller.install(args.install)
        return
    
    # Run specific tool
    if args.category and args.tool:
        run_tool(config, api_manager, target_manager, report_gen, args.category, args.tool, args.target)
        return
    
    # List tools in category
    if args.category:
        list_tools_in_category(args.category)
        return
    
    # Default: show help
    parser.print_help()
    print(f"\n{Colors.CYAN}Use -i for interactive menu!{Colors.ENDC}")

if __name__ == "__main__":
    main()
