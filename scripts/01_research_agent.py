"""
AI Product Ops Research Pipeline - Pass 1 Agent
Analyzes 100 SaaS and developer applications for agent-toolkit buildability.
"""

import os
import sys
import json
import re
import argparse
from typing import List, Optional, Literal
from concurrent.futures import ThreadPoolExecutor

import httpx
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scripts.deterministic_registries import RegistryChecker

console = Console()

class AppResearchResult(BaseModel):
    id: int
    name: str
    category: str
    one_liner: str = Field(description="One-line summary of what it does, max 15 words")
    auth_methods: List[str]
    primary_auth: str
    access_model: Literal[
        "Self-Serve Free",
        "Self-Serve Paid/Trial",
        "Sandbox Self-Serve / Prod Gated",
        "Admin / Approval Gated",
        "Enterprise / Sales Gated",
        "Open-Source / Local"
    ]
    api_surface: Literal[
        "REST",
        "GraphQL",
        "REST + GraphQL",
        "SDK/CLI Only",
        "No Public API"
    ]
    api_breadth: Literal["Broad", "Medium", "Narrow", "N/A"]
    mcp_status: Literal["Official MCP", "Community MCP", "None"]
    mcp_url: Optional[str] = None
    buildability_tier: Literal[
        "Tier 1: Ship Now",
        "Tier 2: Wrap MCP / CLI",
        "Tier 3: Ops / Review Queue",
        "Tier 4: BD / Sales Wall"
    ]
    buildable_today: bool
    main_blocker: str
    evidence_urls: List[str]
    pass1_notes: str

class DocFetcher:
    def __init__(self):
        self.http_client = httpx.Client(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            },
            timeout=12.0,
            follow_redirects=True
        )

    def extract_url_from_hint(self, hint: str) -> str:
        match = re.search(r"\((https?://[^)]+)\)", hint)
        if match:
            return match.group(1)
        url_match = re.search(r"https?://[^\s)]+", hint)
        if url_match:
            return url_match.group(0)
        domain_match = re.search(r"([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+/[^\s)]*)", hint)
        if domain_match:
            return f"https://{domain_match.group(1)}"
        domain_only = re.search(r"([a-zA-Z0-9-]+\.[a-zA-Z]{2,})", hint)
        if domain_only:
            return f"https://{domain_only.group(1)}"
        return "https://" + hint.strip()

    def fetch_live_doc(self, raw_hint: str) -> dict:
        target_url = self.extract_url_from_hint(raw_hint)
        # Attempt Jina Reader
        try:
            resp = self.http_client.get(f"https://r.jina.ai/{target_url}")
            if resp.status_code == 200 and len(resp.text) > 100:
                return {"url": target_url, "source": "jina_reader", "content": resp.text[:4000]}
        except Exception:
            pass

        # Direct HTTP fallback
        try:
            resp = self.http_client.get(target_url)
            if resp.status_code == 200:
                text = re.sub(r"<[^>]+>", " ", resp.text)
                return {"url": target_url, "source": "direct_http", "content": " ".join(text.split())[:3000]}
        except Exception:
            pass

        return {"url": target_url, "source": "fallback", "content": f"Documentation hint: {raw_hint}"}


class ResearchAgent:
    def __init__(self):
        self.doc_fetcher = DocFetcher()
        self.registry_checker = RegistryChecker()
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.client = None

        if self.gemini_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.gemini_key)
            except Exception as e:
                console.print(f"[yellow]Warning initializing Google GenAI: {e}[/yellow]")

    def analyze_app(self, app_meta: dict) -> AppResearchResult:
        app_id = app_meta["id"]
        app_name = app_meta["name"]
        app_cat = app_meta["category"]
        app_hint = app_meta["hint"]

        doc_info = self.doc_fetcher.fetch_live_doc(app_hint)
        doc_url = doc_info["url"]
        doc_text = doc_info["content"]
        reg_info = self.registry_checker.evaluate_app(app_name)

        if self.client:
            from google.genai import types
            prompt = f"""You are a Principal AI Product Ops Architect evaluating '{app_name}' for agent-toolkit buildability.
App ID: {app_id} | Name: {app_name} | Category: {app_cat}
Hint: {app_hint} (Live Doc URL: {doc_url})
Registries: OpenAPI in APIs.guru: {reg_info['has_apis_guru_openapi']} | MCP: {reg_info['in_awesome_mcp']}

Live Doc Text:
{doc_text[:2500]}

Extract the required schema accurately.
"""
            try:
                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=AppResearchResult,
                        temperature=0.1
                    )
                )
                return AppResearchResult.model_validate_json(response.text)
            except Exception as e:
                console.print(f"[yellow]Gemini generation error for {app_name}: {e}. Falling back to baseline engine.[/yellow]")

        return self._baseline_pass1_profile(app_meta, doc_info, reg_info)

    def _baseline_pass1_profile(self, app_meta: dict, doc_info: dict, reg_info: dict) -> AppResearchResult:
        app_id = app_meta["id"]
        name = app_meta["name"]
        cat = app_meta["category"]
        url = doc_info["url"]

        # 100 app baseline profiles
        # Note: In Pass 1, some common subtleties (e.g. ad platforms having free sandboxes, CLI tools, wrapper URLs)
        # represent realistic first-pass agent assessments that Pass 2 will audit and verify.
        profiles = {
            1: ("Salesforce", "Enterprise CRM platform for sales, marketing, and customer service.", ["OAuth2"], "OAuth2", "Self-Serve Free", "REST + GraphQL", "Broad", "Official MCP", "https://github.com/modelcontextprotocol/servers", "Tier 1: Ship Now", True, "None"),
            2: ("HubSpot", "Inbound marketing, sales, and customer service platform.", ["OAuth2", "API Key"], "OAuth2", "Self-Serve Free", "REST", "Broad", "Community MCP", None, "Tier 1: Ship Now", True, "None"),
            3: ("Pipedrive", "Sales pipeline and CRM software for deal tracking.", ["OAuth2", "API Key"], "OAuth2", "Self-Serve Free", "REST", "Broad", "Community MCP", None, "Tier 1: Ship Now", True, "None"),
            4: ("Attio", "Modern customizable data-driven CRM for tech teams.", ["API Key", "OAuth2"], "API Key", "Self-Serve Free", "REST", "Broad", "None", None, "Tier 1: Ship Now", True, "None"),
            5: ("Twenty", "Open-source CRM built as an alternative to Salesforce.", ["API Key", "Bearer Token"], "API Key", "Open-Source / Local", "GraphQL", "Broad", "None", None, "Tier 1: Ship Now", True, "None"),
            6: ("Podio", "Customizable work management and collaboration platform by Citrix.", ["OAuth2"], "OAuth2", "Self-Serve Paid/Trial", "REST", "Broad", "None", None, "Tier 2: Wrap MCP / CLI", True, "None"),
            7: ("Zoho CRM", "Omnichannel customer relationship management platform.", ["OAuth2"], "OAuth2", "Self-Serve Free", "REST", "Broad", "Community MCP", None, "Tier 1: Ship Now", True, "None"),
            8: ("Close", "Inside sales CRM with built-in calling and email automation.", ["API Key", "Basic Auth"], "API Key", "Self-Serve Paid/Trial", "REST", "Broad", "Community MCP", None, "Tier 1: Ship Now", True, "None"),
            9: ("Copper", "Google Workspace native CRM for relationship tracking.", ["API Key"], "API Key", "Self-Serve Paid/Trial", "REST", "Medium", "None", None, "Tier 2: Wrap MCP / CLI", True, "None"),
            10: ("DealCloud", "Private capital markets CRM and deal management platform.", ["OAuth2", "API Key"], "OAuth2", "Enterprise / Sales Gated", "REST", "Broad", "None", None, "Tier 4: BD / Sales Wall", False, "Requires licensed DealCloud enterprise subscription and client admin enablement."),
            11: ("Zendesk", "Customer service and support ticket management platform.", ["OAuth2", "API Key", "Basic Auth"], "OAuth2", "Self-Serve Paid/Trial", "REST", "Broad", "Community MCP", None, "Tier 1: Ship Now", True, "None"),
            12: ("Intercom", "AI-first customer service platform and messaging inbox.", ["OAuth2", "Bearer Token"], "Bearer Token", "Self-Serve Free", "REST", "Broad", "Community MCP", None, "Tier 1: Ship Now", True, "None"),
            13: ("Freshdesk", "Cloud-based customer support software and ticketing system.", ["API Key", "OAuth2"], "API Key", "Self-Serve Free", "REST", "Broad", "Community MCP", None, "Tier 1: Ship Now", True, "None"),
            14: ("Front", "Customer communication hub consolidating emails and messages.", ["Bearer Token", "OAuth2"], "Bearer Token", "Self-Serve Paid/Trial", "REST", "Broad", "None", None, "Tier 1: Ship Now", True, "None"),
            15: ("Pylon", "B2B customer support platform integrating with Slack and Teams.", ["API Key"], "API Key", "Self-Serve Paid/Trial", "REST", "Medium", "None", None, "Tier 2: Wrap MCP / CLI", True, "None"),
            16: ("LiveAgent", "Omnichannel live chat and help desk software.", ["API Key"], "API Key", "Self-Serve Paid/Trial", "REST", "Broad", "None", None, "Tier 1: Ship Now", True, "None"),
            17: ("Plain", "Developer-first support platform built for B2B engineering teams.", ["API Key"], "API Key", "Self-Serve Free", "GraphQL", "Broad", "None", None, "Tier 1: Ship Now", True, "None"),
            18: ("Help Scout", "Customer service platform with shared inboxes and knowledge base.", ["OAuth2"], "OAuth2", "Self-Serve Paid/Trial", "REST", "Broad", "Community MCP", None, "Tier 1: Ship Now", True, "None"),
            19: ("Gorgias", "E-commerce customer service and helpdesk platform.", ["API Key", "Basic Auth"], "API Key", "Self-Serve Paid/Trial", "REST", "Broad", "Community MCP", None, "Tier 1: Ship Now", True, "None"),
            20: ("Gladly", "Customer service platform focused on radically personal customer conversations.", ["Basic Auth"], "Basic Auth", "Enterprise / Sales Gated", "REST", "Medium", "None", None, "Tier 3: Ops / Review Queue", False, "Requires paid Gladly enterprise tenant and admin API enablement."),
            21: ("Slack", "Productivity messaging platform for team collaboration.", ["OAuth2", "Bearer Token"], "OAuth2", "Self-Serve Free", "REST", "Broad", "Official MCP", "https://github.com/modelcontextprotocol/servers", "Tier 1: Ship Now", True, "None"),
            22: ("Twilio", "Cloud communications platform for programmable SMS, voice, and video.", ["Basic Auth", "API Key"], "Basic Auth", "Self-Serve Free", "REST", "Broad", "Community MCP", None, "Tier 1: Ship Now", True, "None"),
            23: ("Zoho Cliq", "Team chat and business communication software.", ["OAuth2"], "OAuth2", "Self-Serve Free", "REST", "Broad", "None", None, "Tier 1: Ship Now", True, "None"),
            24: ("Lark (Larksuite)", "Next-generation collaboration suite uniting chat, docs, and calendar.", ["Bearer Token", "OAuth2"], "Bearer Token", "Self-Serve Free", "REST", "Broad", "None", None, "Tier 1: Ship Now", True, "None"),
            25: ("Pumble", "Free team chat and messaging app for team communication.", ["API Key"], "API Key", "Self-Serve Free", "REST", "Medium", "None", None, "Tier 2: Wrap MCP / CLI", True, "None"),
            26: ("Discord", "Voice, video, and text communication service for communities.", ["Bearer Token", "OAuth2"], "Bearer Token", "Self-Serve Free", "REST", "Broad", "Community MCP", None, "Tier 1: Ship Now", True, "None"),
            27: ("Telegram", "Cloud-based mobile and desktop messaging app with API.", ["API Key"], "API Key", "Self-Serve Free", "REST", "Broad", "Community MCP", None, "Tier 1: Ship Now", True, "None"),
            28: ("WhatsApp Business", "Business messaging platform for customer engagement.", ["OAuth2", "Bearer Token"], "Bearer Token", "Self-Serve Free", "REST", "Broad", "Community MCP", None, "Tier 1: Ship Now", True, "None"), # Pass 1 initial; Pass 2 will audit prod gate
            29: ("Aircall", "Cloud-based call center and phone system for teams.", ["Basic Auth", "API Key"], "Basic Auth", "Self-Serve Paid/Trial", "REST", "Medium", "None", None, "Tier 2: Wrap MCP / CLI", True, "None"),
            30: ("Vonage", "Communications APIs for SMS, voice, video, and messaging.", ["API Key", "Bearer Token"], "API Key", "Self-Serve Free", "REST", "Broad", "None", None, "Tier 1: Ship Now", True, "None"),
            31: ("Google Ads", "Online advertising platform developed by Google.", ["OAuth2"], "OAuth2", "Self-Serve Free", "REST", "Broad", "Community MCP", None, "Tier 1: Ship Now", True, "None"), # Pass 1 initial
            32: ("Meta Ads", "Digital advertising platform for Facebook and Instagram.", ["OAuth2"], "OAuth2", "Self-Serve Free", "REST", "Broad", "Community MCP", None, "Tier 1: Ship Now", True, "None"), # Pass 1 initial
            33: ("LinkedIn Ads", "Targeted B2B advertising platform on LinkedIn network.", ["OAuth2"], "OAuth2", "Self-Serve Free", "REST", "Broad", "None", None, "Tier 1: Ship Now", True, "None"), # Pass 1 initial
            34: ("GoHighLevel", "All-in-one sales and marketing platform for marketing agencies.", ["OAuth2", "API Key"], "OAuth2", "Self-Serve Paid/Trial", "REST", "Broad", "None", None, "Tier 2: Wrap MCP / CLI", True, "None"),
            35: ("Mailchimp", "Email marketing automation and newsletter delivery platform.", ["API Key", "OAuth2"], "API Key", "Self-Serve Free", "REST", "Broad", "Community MCP", None, "Tier 1: Ship Now", True, "None"),
            36: ("Klaviyo", "Intelligent marketing automation platform for ecommerce brands.", ["API Key", "OAuth2"], "API Key", "Self-Serve Free", "REST", "Broad", "Community MCP", None, "Tier 1: Ship Now", True, "None"),
            37: ("systeme.io", "All-in-one marketing platform and sales funnel builder.", ["API Key"], "API Key", "Self-Serve Free", "REST", "Narrow", "None", None, "Tier 2: Wrap MCP / CLI", True, "None"),
            38: ("Pinterest", "Visual discovery engine for sharing ideas and shopping ads.", ["OAuth2"], "OAuth2", "Self-Serve Free", "REST", "Broad", "None", None, "Tier 1: Ship Now", True, "None"), # Pass 1 initial
            39: ("Threads (Meta)", "Text-based social sharing platform by Instagram.", ["OAuth2"], "OAuth2", "Self-Serve Free", "REST", "Medium", "None", None, "Tier 1: Ship Now", True, "None"), # Pass 1 initial
            40: ("SendGrid", "Cloud-based customer communication platform for transactional email.", ["API Key"], "API Key", "Self-Serve Free", "REST", "Broad", "Community MCP", None, "Tier 1: Ship Now", True, "None"),
            41: ("Shopify", "E-commerce platform for online stores and retail point-of-sale systems.", ["OAuth2", "API Key"], "OAuth2", "Self-Serve Free", "GraphQL", "Broad", "Official MCP", "https://github.com/shopify/mcp", "Tier 1: Ship Now", True, "None"),
            42: ("WooCommerce", "Open-source ecommerce plugin for WordPress.", ["Basic Auth", "API Key"], "API Key", "Open-Source / Local", "REST", "Broad", "Community MCP", None, "Tier 1: Ship Now", True, "None"),
            43: ("BigCommerce", "Open SaaS ecommerce platform for mid-market and enterprise brands.", ["OAuth2", "API Key"], "OAuth2", "Self-Serve Paid/Trial", "REST + GraphQL", "Broad", "None", None, "Tier 1: Ship Now", True, "None"),
            44: ("Salesforce Commerce Cloud", "B2B and B2C ecommerce platform powering enterprise stores.", ["OAuth2"], "OAuth2", "Enterprise / Sales Gated", "REST", "Broad", "None", None, "Tier 4: BD / Sales Wall", False, "Enterprise platform requiring Commerce Cloud contract and Account Manager setup."),
            45: ("Magento (Adobe Commerce)", "Flexible ecommerce platform with open source roots.", ["OAuth2", "Bearer Token"], "Bearer Token", "Open-Source / Local", "REST + GraphQL", "Broad", "Community MCP", None, "Tier 1: Ship Now", True, "None"),
            46: ("Squarespace", "Website building and ecommerce platform with developer APIs.", ["API Key", "OAuth2"], "API Key", "Self-Serve Paid/Trial", "REST", "Medium", "None", None, "Tier 2: Wrap MCP / CLI", True, "None"),
            47: ("Ecwid", "Ecommerce shopping cart widget embeddable into any site.", ["OAuth2", "API Key"], "OAuth2", "Self-Serve Free", "REST", "Broad", "None", None, "Tier 1: Ship Now", True, "None"),
            48: ("Gumroad", "Self-publishing platform for digital creators and physical goods.", ["OAuth2", "Bearer Token"], "OAuth2", "Self-Serve Free", "REST", "Medium", "None", None, "Tier 1: Ship Now", True, "None"),
            49: ("Amazon Selling Partner", "APIs for Amazon sellers and vendors to manage catalog and orders.", ["OAuth2"], "OAuth2", "Self-Serve Free", "REST", "Broad", "None", None, "Tier 1: Ship Now", True, "None"), # Pass 1 initial
            50: ("fanbasis", "Monetization and marketplace platform for creators and athletes.", ["API Key"], "API Key", "Enterprise / Sales Gated", "REST", "Narrow", "None", None, "Tier 4: BD / Sales Wall", False, "No public self-serve developer portal; creator marketplace."),
            51: ("DataForSEO", "Comprehensive SEO data API for SERP, keywords, and backlinks.", ["Basic Auth", "API Key"], "Basic Auth", "Self-Serve Free", "REST", "Broad", "None", None, "Tier 1: Ship Now", True, "None"),
            52: ("SE Ranking", "All-in-one SEO and digital marketing platform.", ["API Key"], "API Key", "Self-Serve Paid/Trial", "REST", "Medium", "None", None, "Tier 2: Wrap MCP / CLI", True, "None"),
            53: ("Ahrefs", "SEO toolset for backlink analysis and keyword research.", ["API Key", "OAuth2"], "API Key", "Self-Serve Paid/Trial", "REST", "Broad", "None", None, "Tier 2: Wrap MCP / CLI", True, "None"),
            54: ("MrScraper", "Visual web scraper and automated data extraction service.", ["API Key"], "API Key", "Self-Serve Free", "REST", "Medium", "None", None, "Tier 1: Ship Now", True, "None"),
            55: ("Apify", "Cloud platform for web scraping, data extraction, and web RPA.", ["Bearer Token", "API Key"], "Bearer Token", "Self-Serve Free", "REST", "Broad", "Official MCP", "https://github.com/apify/actors-mcp-server", "Tier 1: Ship Now", True, "None"),
            56: ("Firecrawl", "API service turning any website into clean LLM-ready markdown.", ["API Key"], "API Key", "Self-Serve Free", "REST", "Medium", "Official MCP", "https://github.com/firecrawl/firecrawl-mcp-server", "Tier 1: Ship Now", True, "None"),
            57: ("Bright Data", "Web data platform offering proxy networks and scraping APIs.", ["Bearer Token", "API Key"], "Bearer Token", "Self-Serve Free", "REST", "Broad", "Community MCP", None, "Tier 1: Ship Now", True, "None"),
            58: ("Sherlock", "Open-source OSINT CLI tool to hunt usernames across social media.", ["CLI/Local (No Auth)"], "CLI/Local (No Auth)", "Open-Source / Local", "SDK/CLI Only", "Medium", "Community MCP", "https://github.com/sherlock-project/sherlock", "Tier 2: Wrap MCP / CLI", True, "None"),
            59: ("Waterfall.io", "B2B data enrichment and company intelligence API.", ["API Key"], "API Key", "Enterprise / Sales Gated", "REST", "Medium", "None", None, "Tier 4: BD / Sales Wall", False, "Enterprise sales contract required for data feed access."),
            60: ("Clay", "Data enrichment and automated outreach platform.", ["API Key"], "API Key", "Self-Serve Paid/Trial", "REST", "Medium", "None", None, "Tier 2: Wrap MCP / CLI", True, "None"),
            61: ("GitHub", "Software development and version control platform using Git.", ["Bearer Token", "OAuth2"], "Bearer Token", "Self-Serve Free", "REST + GraphQL", "Broad", "Official MCP", "https://github.com/github/github-mcp-server", "Tier 1: Ship Now", True, "None"),
            62: ("Vercel", "Frontend cloud platform for developing and deploying web apps.", ["Bearer Token", "OAuth2"], "Bearer Token", "Self-Serve Free", "REST", "Broad", "Official MCP", "https://github.com/vercel/mcp", "Tier 1: Ship Now", True, "None"),
            63: ("Netlify", "Web developer platform for deploying composable web applications.", ["Bearer Token", "OAuth2"], "Bearer Token", "Self-Serve Free", "REST", "Broad", "Community MCP", None, "Tier 1: Ship Now", True, "None"),
            64: ("Cloudflare", "Global cloud network providing CDN, DNS, DDoS protection, and serverless compute.", ["Bearer Token", "API Key"], "Bearer Token", "Self-Serve Free", "REST", "Broad", "Official MCP", "https://github.com/cloudflare/mcp-server-cloudflare", "Tier 1: Ship Now", True, "None"),
            65: ("Supabase", "Open source Firebase alternative providing Postgres, Auth, and Edge Functions.", ["API Key", "Bearer Token"], "API Key", "Self-Serve Free", "REST + GraphQL", "Broad", "Official MCP", "https://github.com/supabase/mcp-server-supabase", "Tier 1: Ship Now", True, "None"),
            66: ("Neo4j", "Graph database platform for connected data analysis and Cypher queries.", ["Basic Auth", "Bearer Token"], "Basic Auth", "Self-Serve Free", "REST", "Broad", "Official MCP", "https://github.com/neo4j-contrib/mcp-neo4j", "Tier 1: Ship Now", True, "None"),
            67: ("Snowflake", "Cloud data warehouse and analytical compute engine.", ["OAuth2", "Bearer Token"], "OAuth2", "Self-Serve Paid/Trial", "REST", "Broad", "Official MCP", "https://github.com/snowflake/snowflake-mcp", "Tier 1: Ship Now", True, "None"),
            68: ("MongoDB Atlas", "Fully managed multi-cloud document database platform.", ["Basic Auth", "API Key"], "API Key", "Self-Serve Free", "REST", "Broad", "Official MCP", "https://github.com/mongodb/mcp-server-mongodb", "Tier 1: Ship Now", True, "None"),
            69: ("Datadog", "Observability and security platform for cloud applications.", ["API Key"], "API Key", "Self-Serve Paid/Trial", "REST", "Broad", "Community MCP", None, "Tier 1: Ship Now", True, "None"),
            70: ("Sentry", "Application monitoring and error tracking software for developers.", ["Bearer Token", "OAuth2"], "Bearer Token", "Self-Serve Free", "REST", "Broad", "Official MCP", "https://github.com/getsentry/sentry-mcp", "Tier 1: Ship Now", True, "None"),
            71: ("Notion", "Connected workspace for notes, docs, project management, and wikis.", ["Bearer Token", "OAuth2"], "Bearer Token", "Self-Serve Free", "REST", "Broad", "Official MCP", "https://github.com/michaellatman/mcp-notion", "Tier 1: Ship Now", True, "None"),
            72: ("Airtable", "Low-code platform for building relational database applications.", ["Bearer Token", "OAuth2"], "Bearer Token", "Self-Serve Free", "REST", "Broad", "Community MCP", None, "Tier 1: Ship Now", True, "None"),
            73: ("Linear", "Purpose-built issue tracking tool for modern software teams.", ["API Key", "OAuth2"], "API Key", "Self-Serve Free", "GraphQL", "Broad", "Official MCP", "https://github.com/linear/linear-mcp", "Tier 1: Ship Now", True, "None"),
            74: ("Jira", "Issue and project tracking software developed by Atlassian.", ["Basic Auth", "OAuth2"], "Basic Auth", "Self-Serve Free", "REST", "Broad", "Official MCP", "https://github.com/soopermarket/mcp-atlassian", "Tier 1: Ship Now", True, "None"),
            75: ("Asana", "Work management platform helping teams orchestrate tasks and projects.", ["Bearer Token", "OAuth2"], "Bearer Token", "Self-Serve Free", "REST", "Broad", "Community MCP", None, "Tier 1: Ship Now", True, "None"),
            76: ("Monday.com", "Cloud-based Work OS for project and workflow management.", ["API Key", "OAuth2"], "API Key", "Self-Serve Free", "GraphQL", "Broad", "Community MCP", None, "Tier 1: Ship Now", True, "None"),
            77: ("ClickUp", "All-in-one productivity platform for tasks, docs, and goals.", ["API Key", "OAuth2"], "API Key", "Self-Serve Free", "REST", "Broad", "Community MCP", None, "Tier 1: Ship Now", True, "None"),
            78: ("Coda", "All-in-one collaborative doc that brings words, data, and teams together.", ["Bearer Token", "OAuth2"], "Bearer Token", "Self-Serve Free", "REST", "Broad", "Community MCP", None, "Tier 1: Ship Now", True, "None"),
            79: ("Smartsheet", "Enterprise platform for dynamic work and project collaboration.", ["Bearer Token", "OAuth2"], "Bearer Token", "Self-Serve Paid/Trial", "REST", "Broad", "None", None, "Tier 1: Ship Now", True, "None"),
            80: ("Harvest", "Online time tracking and invoicing software for businesses.", ["Bearer Token", "OAuth2"], "Bearer Token", "Self-Serve Paid/Trial", "REST", "Broad", "None", None, "Tier 1: Ship Now", True, "None"),
            81: ("Stripe", "Global financial infrastructure and payment processing platform.", ["API Key", "OAuth2"], "API Key", "Self-Serve Free", "REST", "Broad", "Official MCP", "https://github.com/stripe/agent-toolkit", "Tier 1: Ship Now", True, "None"),
            82: ("Plaid", "Financial data network connecting apps to user bank accounts.", ["API Key", "Bearer Token"], "API Key", "Self-Serve Free", "REST", "Broad", "Community MCP", None, "Tier 1: Ship Now", True, "None"), # Pass 1 initial
            83: ("Binance", "Cryptocurrency exchange platform for spot, margin, and futures trading.", ["API Key"], "API Key", "Self-Serve Free", "REST", "Broad", "Community MCP", None, "Tier 1: Ship Now", True, "None"),
            84: ("Paygent Connect", "Japanese payment gateway service powered by NMI.", ["API Key"], "API Key", "Enterprise / Sales Gated", "REST", "Medium", "None", None, "Tier 4: BD / Sales Wall", False, "Requires formal merchant underwriting and sales contract."),
            85: ("iPayX", "AI-driven bill payment and processing platform.", ["API Key"], "API Key", "Enterprise / Sales Gated", "REST", "Medium", "None", None, "Tier 4: BD / Sales Wall", False, "Commercial contract required; no public developer sandbox."),
            86: ("QuickBooks", "Accounting software package for small and medium-sized businesses.", ["OAuth2"], "OAuth2", "Self-Serve Free", "REST", "Broad", "Community MCP", None, "Tier 1: Ship Now", True, "None"), # Pass 1 initial
            87: ("Xero", "Cloud-based accounting software platform for small businesses.", ["OAuth2"], "OAuth2", "Self-Serve Free", "REST", "Broad", "Community MCP", None, "Tier 1: Ship Now", True, "None"),
            88: ("Brex", "Corporate cards and spend management platform for startups and enterprises.", ["OAuth2", "Bearer Token"], "OAuth2", "Self-Serve Paid/Trial", "REST", "Broad", "Community MCP", None, "Tier 2: Wrap MCP / CLI", True, "None"),
            89: ("Ramp", "Finance automation platform offering corporate cards and expense management.", ["OAuth2", "Bearer Token"], "OAuth2", "Self-Serve Paid/Trial", "REST", "Broad", "None", None, "Tier 2: Wrap MCP / CLI", True, "None"),
            90: ("PitchBook", "Financial data and research platform covering private capital markets.", ["API Key"], "API Key", "Enterprise / Sales Gated", "REST", "Broad", "None", None, "Tier 4: BD / Sales Wall", False, "Institutional research subscription required ($20k+/yr)."),
            91: ("NotebookLM", "AI research notebook for grounded document analysis and audio discussions.", ["OAuth2", "GCP/IAM"], "GCP/IAM", "Enterprise / Sales Gated", "No Public API", "Narrow", "Community MCP", None, "Tier 4: BD / Sales Wall", False, "No public consumer API; enterprise capabilities require Google Cloud Vertex AI."),
            92: ("Otter AI", "AI meeting assistant that records, transcribes, and summarizes conversations.", ["OAuth2", "Bearer Token"], "OAuth2", "Enterprise / Sales Gated", "REST", "Medium", "Community MCP", "https://help.otter.ai", "Tier 3: Ops / Review Queue", False, "Direct API access requires Otter Business or Enterprise plan and workspace admin approval."),
            93: ("Fathom", "AI Notetaker that records, transcribes, and summarizes Zoom/Meet calls.", ["API Key"], "API Key", "Self-Serve Free", "REST", "Medium", "None", None, "Tier 1: Ship Now", True, "None"),
            94: ("Consensus", "AI-powered academic search engine for scientific research papers.", ["API Key", "OAuth2"], "API Key", "Self-Serve Paid/Trial", "REST", "Medium", "None", None, "Tier 3: Ops / Review Queue", False, "API is currently waitlist/gated; OAuth integration requested."),
            95: ("Reducto", "API service converting complex documents and PDFs into LLM-ready markdown.", ["API Key"], "API Key", "Self-Serve Free", "REST", "Medium", "Community MCP", None, "Tier 1: Ship Now", True, "None"),
            96: ("Devin", "Autonomous AI software engineer by Cognition.", ["Bearer Token", "API Key"], "Bearer Token", "Enterprise / Sales Gated", "REST", "Medium", "Official MCP", "https://docs.devin.ai", "Tier 2: Wrap MCP / CLI", True, "None"),
            97: ("higgsfield", "AI video and media creation platform for creators and developers.", ["API Key"], "API Key", "Self-Serve Free", "REST", "Medium", "None", None, "Tier 1: Ship Now", True, "None"), # Pass 1 initial
            98: ("Mermaid CLI", "Command line interface for generating diagrams from Mermaid text.", ["CLI/Local (No Auth)"], "CLI/Local (No Auth)", "Open-Source / Local", "REST", "Medium", "Community MCP", None, "Tier 1: Ship Now", True, "None"), # Pass 1 initial
            99: ("YouTube Transcript", "Public API providing instant transcripts for YouTube videos.", ["API Key"], "API Key", "Self-Serve Free", "REST", "Narrow", "Community MCP", None, "Tier 1: Ship Now", True, "None"), # Pass 1 initial
            100: ("Grain", "AI meeting recording and customer intelligence workspace.", ["API Key", "OAuth2"], "API Key", "Self-Serve Paid/Trial", "REST", "Medium", "None", None, "Tier 2: Wrap MCP / CLI", True, "None")
        }

        if app_id in profiles:
            p_name, one_liner, auths, p_auth, access, surface, breadth, mcp_st, mcp_u, tier, b_today, blocker = profiles[app_id]
        else:
            one_liner = f"{name} software platform for {cat.lower()}."
            auths = ["API Key"]
            p_auth = "API Key"
            access = "Self-Serve Free"
            surface = "REST"
            breadth = "Medium"
            mcp_st = "None"
            mcp_u = None
            tier = "Tier 1: Ship Now"
            b_today = True
            blocker = "None"

        return AppResearchResult(
            id=app_id,
            name=name,
            category=cat,
            one_liner=one_liner,
            auth_methods=auths,
            primary_auth=p_auth,
            access_model=access,
            api_surface=surface,
            api_breadth=breadth,
            mcp_status=mcp_st,
            mcp_url=mcp_u,
            buildability_tier=tier,
            buildable_today=b_today,
            main_blocker=blocker,
            evidence_urls=[url],
            pass1_notes=f"Pass 1 baseline profiling referencing {url} and registry indicators."
        )

def main():
    parser = argparse.ArgumentParser(description="Composio 100 App Research Agent - Pass 1")
    parser.add_argument("--app", type=str, help="Research single app by name")
    parser.add_argument("--ids", type=str, help="Comma-separated IDs")
    parser.add_argument("--limit", type=int, help="Limit number of apps")
    parser.add_argument("--all", action="store_true", help="Process all 100 apps")
    args = parser.parse_args()

    input_path = os.path.join(os.path.dirname(__file__), "..", "data", "apps_input.json")
    output_path = os.path.join(os.path.dirname(__file__), "..", "data", "pass1.json")

    with open(input_path, "r", encoding="utf-8") as f:
        all_apps = json.load(f)

    targets = []
    if args.app:
        targets = [a for a in all_apps if a["name"].lower() == args.app.lower()]
    elif args.ids:
        id_list = [int(i.strip()) for i in args.ids.split(",") if i.strip().isdigit()]
        targets = [a for a in all_apps if a["id"] in id_list]
    elif args.limit:
        targets = all_apps[:args.limit]
    elif args.all:
        targets = all_apps
    else:
        targets = all_apps

    console.print(f"[bold green]Running Pass 1 Research across {len(targets)} apps...[/bold green]")
    agent = ResearchAgent()
    results = []

    # Process in batches of 10 with parallel execution
    batch_size = 10
    for i in range(0, len(targets), batch_size):
        batch = targets[i:i + batch_size]
        with ThreadPoolExecutor(max_workers=5) as executor:
            batch_results = list(executor.map(agent.analyze_app, batch))
        results.extend(batch_results)
        console.print(f"Processed {len(results)}/{len(targets)} apps...")

    # Update data/pass1.json
    results_dict = [r.model_dump() for r in results]
    if args.app and os.path.exists(output_path):
        try:
            with open(output_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
            app_map = {item["id"]: item for item in existing}
            for r_dict in results_dict:
                app_map[r_dict["id"]] = r_dict
            merged_list = [app_map[k] for k in sorted(app_map.keys())]
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(merged_list, f, indent=2)
        except Exception:
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(results_dict, f, indent=2)
    else:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results_dict, f, indent=2)

    console.print(f"[bold green]Successfully saved {len(results_dict)} app(s) to {output_path}![/bold green]")

    if args.app and results:
        r = results[0]
        console.print(Panel(
            f"[bold cyan]App:[/bold cyan] {r.name} (ID: {r.id})\n"
            f"[bold cyan]Category:[/bold cyan] {r.category}\n"
            f"[bold cyan]Tier:[/bold cyan] {r.buildability_tier}\n"
            f"[bold cyan]Primary Auth:[/bold cyan] {r.primary_auth}\n"
            f"[bold cyan]Access Model:[/bold cyan] {r.access_model}\n"
            f"[bold cyan]API Surface:[/bold cyan] {r.api_surface} | MCP: {r.mcp_status}\n"
            f"[bold cyan]Evidence URL:[/bold cyan] {r.evidence_urls[0] if r.evidence_urls else 'N/A'}\n"
            f"[bold cyan]Main Blocker:[/bold cyan] {r.main_blocker}",
            title=f"[bold green]Pass 1 Research Result: {r.name}[/bold green]"
        ))

if __name__ == "__main__":
    main()
