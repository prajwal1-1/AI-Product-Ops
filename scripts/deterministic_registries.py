"""
Deterministic Ground-Truth Registry Cross-Checker.

Integrates:
1. modelcontextprotocol/registry API
2. APIs-guru/openapi-directory API
3. punkpeye/awesome-mcp-servers & awesome-remote-mcp-servers
"""

import httpx
import json
import os
import re
from typing import Dict, Any, List

CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

class RegistryChecker:
    def __init__(self):
        self.client = httpx.Client(timeout=15.0, follow_redirects=True)
        self.apis_guru_data: Dict[str, Any] = {}
        self.awesome_mcp_text: str = ""
        self.awesome_remote_mcp_text: str = ""

    def load_apis_guru(self) -> Dict[str, Any]:
        cache_path = os.path.join(CACHE_DIR, "apis_guru_list.json")
        if os.path.exists(cache_path):
            with open(cache_path, "r", encoding="utf-8") as f:
                self.apis_guru_data = json.load(f)
                return self.apis_guru_data

        url = "https://api.apis.guru/v2/list.json"
        try:
            resp = self.client.get(url)
            if resp.status_code == 200:
                self.apis_guru_data = resp.json()
                with open(cache_path, "w", encoding="utf-8") as f:
                    json.dump(self.apis_guru_data, f)
        except Exception as e:
            print(f"[Warning] Failed to fetch APIs.guru list: {e}")
        return self.apis_guru_data

    def load_awesome_mcp(self) -> str:
        cache_path = os.path.join(CACHE_DIR, "awesome_mcp.md")
        if os.path.exists(cache_path):
            with open(cache_path, "r", encoding="utf-8") as f:
                self.awesome_mcp_text = f.read()
                return self.awesome_mcp_text

        url = "https://raw.githubusercontent.com/punkpeye/awesome-mcp-servers/main/README.md"
        try:
            resp = self.client.get(url)
            if resp.status_code == 200:
                self.awesome_mcp_text = resp.text
                with open(cache_path, "w", encoding="utf-8") as f:
                    f.write(self.awesome_mcp_text)
        except Exception as e:
            print(f"[Warning] Failed to fetch awesome-mcp-servers: {e}")
        return self.awesome_mcp_text

    def check_official_mcp_registry(self, app_name: str) -> List[Dict[str, Any]]:
        clean_name = re.sub(r"[^a-zA-Z0-9]", "", app_name).lower()
        url = f"https://registry.modelcontextprotocol.io/v0.1/servers?search={clean_name}&version=latest"
        try:
            resp = self.client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                results = []
                servers = data.get("servers", [])
                for s in servers:
                    name = s.get("name", "")
                    desc = s.get("description", "")
                    if clean_name in name.lower() or clean_name in desc.lower():
                        results.append({"name": name, "description": desc, "url": s.get("url", "")})
                return results
        except Exception:
            pass
        return []

    def check_apis_guru(self, app_name: str) -> List[str]:
        if not self.apis_guru_data:
            self.load_apis_guru()
        clean = re.sub(r"[^a-zA-Z0-9]", "", app_name).lower()
        matches = []
        for key in self.apis_guru_data.keys():
            if clean in key.lower():
                matches.append(key)
        return matches

    def check_awesome_mcp(self, app_name: str) -> bool:
        if not self.awesome_mcp_text:
            self.load_awesome_mcp()
        pattern = rf"\b{re.escape(app_name)}\b"
        return bool(re.search(pattern, self.awesome_mcp_text, re.IGNORECASE))

    def evaluate_app(self, app_name: str) -> Dict[str, Any]:
        return {
            "app_name": app_name,
            "has_apis_guru_openapi": len(self.check_apis_guru(app_name)) > 0,
            "apis_guru_keys": self.check_apis_guru(app_name),
            "official_mcp_servers": self.check_official_mcp_registry(app_name),
            "in_awesome_mcp": self.check_awesome_mcp(app_name)
        }

if __name__ == "__main__":
    checker = RegistryChecker()
    checker.load_apis_guru()
    checker.load_awesome_mcp()
    test_apps = ["GitHub", "Stripe", "Slack", "Twenty", "DealCloud"]
    for app in test_apps:
        res = checker.evaluate_app(app)
        print(f"\n[{app}] -> OpenAPI: {res['has_apis_guru_openapi']} (keys: {res['apis_guru_keys'][:2]}), Official MCP: {len(res['official_mcp_servers'])}, Awesome MCP: {res['in_awesome_mcp']}")
