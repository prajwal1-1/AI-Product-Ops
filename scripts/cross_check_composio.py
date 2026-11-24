"""
Cross-checks the 100 apps in data/final_verified.json against Composio's live toolkits catalog.
Supports:
1. Direct API call to https://backend.composio.dev/api/v3.1/toolkits?limit=1000 if COMPOSIO_API_KEY is available.
2. Official live GitHub catalog https://raw.githubusercontent.com/ComposioHQ/composio/master/docs/public/data/toolkits.json fallback (1,841 toolkits).
Enriches final_verified.json with `in_composio` and `composio_meta`.
Updates patterns_summary.json with Composio adoption and Net-New Quick Wins metrics.
"""

import os
import json
import re
import httpx
from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
FINAL_JSON = os.path.join(ROOT_DIR, "data", "final_verified.json")
PATTERNS_JSON = os.path.join(ROOT_DIR, "data", "patterns_summary.json")

# Verified Composio slug aliases for our 100 apps
APP_SLUG_ALIASES = {
    "Salesforce": "salesforce",
    "HubSpot": "hubspot",
    "Pipedrive": "pipedrive",
    "Attio": "attio",
    "Twenty": "twenty",
    "Podio": "podio",
    "Zoho CRM": "zoho",
    "Close": "close",
    "Copper": "copper",
    "Zendesk": "zendesk",
    "Intercom": "intercom",
    "Freshdesk": "freshdesk",
    "Front": "front",
    "Pylon": "pylon_mcp",
    "Plain": "plain",
    "Help Scout": "helpscout",
    "Gorgias": "gorgias",
    "Slack": "slack",
    "Twilio": "twilio",
    "Zoho Cliq": "zoho_cliq",
    "Lark (Larksuite)": "lark",
    "Discord": "discord",
    "Telegram": "telegram",
    "WhatsApp Business": "whatsapp",
    "Aircall": "aircall",
    "Google Ads": "googleads",
    "Meta Ads": "facebook_marketing",
    "LinkedIn Ads": "linkedin",
    "Mailchimp": "mailchimp",
    "Klaviyo": "klaviyo",
    "Pinterest": "pinterest",
    "Threads (Meta)": "threads",
    "SendGrid": "sendgrid",
    "Shopify": "shopify",
    "BigCommerce": "bigcommerce",
    "Gumroad": "gumroad",
    "Ahrefs": "ahrefs",
    "Apify": "apify",
    "Clay": "clay",
    "GitHub": "github",
    "Vercel": "vercel",
    "Netlify": "netlify",
    "Cloudflare": "cloudflare",
    "Supabase": "supabase",
    "Neo4j": "neo4j",
    "Snowflake": "snowflake",
    "MongoDB Atlas": "mongodb",
    "Datadog": "datadog",
    "Sentry": "sentry",
    "Notion": "notion",
    "Airtable": "airtable",
    "Linear": "linear",
    "Jira": "jira",
    "Asana": "asana",
    "Monday.com": "monday",
    "ClickUp": "clickup",
    "Coda": "coda",
    "Smartsheet": "smartsheet",
    "Harvest": "harvest",
    "Stripe": "stripe",
    "Plaid": "plaid",
    "Binance": "binance",
    "QuickBooks": "quickbooks",
    "Xero": "xero",
    "Brex": "brex",
    "Ramp": "ramp",
    "Fathom": "fathom"
}

def fetch_composio_toolkits():
    api_key = os.getenv("COMPOSIO_API_KEY")
    toolkits = []
    
    if api_key:
        print("[Info] Calling live Composio API with x-api-key...")
        cursor = None
        headers = {"x-api-key": api_key}
        while True:
            url = "https://backend.composio.dev/api/v3.1/toolkits?limit=1000"
            if cursor:
                url += f"&cursor={cursor}"
            try:
                resp = httpx.get(url, headers=headers, timeout=20.0)
                if resp.status_code == 200:
                    data = resp.json()
                    items = data.get("items", [])
                    toolkits.extend(items)
                    cursor = data.get("next_cursor")
                    if not cursor:
                        break
                else:
                    print(f"[Warning] Composio API returned HTTP {resp.status_code}, falling back to live catalog.")
                    break
            except Exception as e:
                print(f"[Warning] Composio API error: {e}, falling back to live catalog.")
                break

    if not toolkits:
        print("[Info] Fetching official live Composio toolkits catalog from docs dataset...")
        url = "https://raw.githubusercontent.com/ComposioHQ/composio/master/docs/public/data/toolkits.json"
        resp = httpx.get(url, timeout=30.0)
        if resp.status_code == 200:
            toolkits = resp.json()
            print(f"[Success] Loaded {len(toolkits)} live toolkits from official catalog.")
        else:
            raise RuntimeError(f"Failed to fetch Composio toolkits: HTTP {resp.status_code}")

    return toolkits

def cross_check():
    toolkits = fetch_composio_toolkits()
    
    # Build lookup maps
    by_slug = {t.get("slug", "").lower(): t for t in toolkits if t.get("slug")}
    by_name = {re.sub(r"[^a-zA-Z0-9]", "", t.get("name", "")).lower(): t for t in toolkits if t.get("name")}

    with open(FINAL_JSON, "r", encoding="utf-8") as f:
        apps = json.load(f)

    with open(PATTERNS_JSON, "r", encoding="utf-8") as f:
        patterns = json.load(f)

    already_in_composio = []
    net_new_apps = []
    net_new_quick_wins = []

    for a in apps:
        name = a["name"]
        norm = re.sub(r"[^a-zA-Z0-9]", "", name).lower()
        alias_slug = APP_SLUG_ALIASES.get(name)

        matched_tk = None
        if alias_slug and alias_slug.lower() in by_slug:
            matched_tk = by_slug[alias_slug.lower()]
        elif norm in by_name:
            matched_tk = by_name[norm]
        elif norm in by_slug:
            matched_tk = by_slug[norm]
        else:
            # Check lowercase direct slug match
            for s, tk in by_slug.items():
                if s == name.lower() or s == norm:
                    matched_tk = tk
                    break

        if matched_tk:
            slug = matched_tk.get("slug")
            managed_oauth = "OAUTH2" in matched_tk.get("composioManagedAuthSchemes", [])
            instant = matched_tk.get("category") == "instant" or len(matched_tk.get("authSchemes", [])) == 0
            
            a["in_composio"] = True
            a["composio_meta"] = {
                "slug": slug,
                "managed_oauth": managed_oauth,
                "instant_supported": instant
            }
            already_in_composio.append(a)
        else:
            a["in_composio"] = False
            a["composio_meta"] = {
                "slug": None,
                "managed_oauth": False,
                "instant_supported": False
            }
            net_new_apps.append(a)
            if a.get("buildability_tier") in ["Tier 1: Ship Now", "Tier 2: Wrap MCP / CLI"]:
                net_new_quick_wins.append(a)

    print(f"\n=== COMPOSIO CATALOG RECONCILIATION ===")
    print(f"Total Apps in Study: {len(apps)}")
    print(f"Already in Composio: {len(already_in_composio)} ({len(already_in_composio)}%)")
    print(f"Net-New Opportunities: {len(net_new_apps)} ({len(net_new_apps)}%)")
    print(f"Net-New Tier 1 & 2 Quick Wins: {len(net_new_quick_wins)} ({len(net_new_quick_wins)}%)")

    # Update patterns_summary.json
    patterns["composio_catalog_comparison"] = {
        "total_apps": len(apps),
        "already_in_composio_count": len(already_in_composio),
        "already_in_composio_pct": f"{len(already_in_composio)}%",
        "net_new_apps_count": len(net_new_apps),
        "net_new_apps_pct": f"{len(net_new_apps)}%",
        "net_new_quick_wins_count": len(net_new_quick_wins),
        "net_new_quick_wins_sample": [a["name"] for a in net_new_quick_wins[:10]],
        "net_new_all_sample": [a["name"] for a in net_new_apps[:10]]
    }

    # Save updated final_verified.json
    with open(FINAL_JSON, "w", encoding="utf-8") as f:
        json.dump(apps, f, indent=2)

    # Save updated patterns_summary.json
    with open(PATTERNS_JSON, "w", encoding="utf-8") as f:
        json.dump(patterns, f, indent=2)

    print("✔ Successfully updated data/final_verified.json and data/patterns_summary.json with Composio catalog metadata.")

if __name__ == "__main__":
    cross_check()
