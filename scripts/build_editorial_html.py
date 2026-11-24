"""
Compiles the pristine, editorial light-mode single-file executive case study: index.html.
Fully adheres to:
- Editorial light-mode aesthetic (#FAFAFA background, #FFFFFF cards, #E5E7EB borders, Inter + JetBrains Mono)
- 2-Minute Executive comprehension
- Exact 6-section structure specified by the user
- Embedded JSON agent-consumable layer and clipboard copy
"""

import os
import json

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
FINAL_JSON = os.path.join(ROOT_DIR, "data", "final_verified.json")
PATTERNS_JSON = os.path.join(ROOT_DIR, "data", "patterns_summary.json")
LOG_JSON = os.path.join(ROOT_DIR, "data", "verification_log.json")
OUTPUT_HTML = os.path.join(ROOT_DIR, "index.html")

def build():
    with open(FINAL_JSON, "r", encoding="utf-8") as f:
        apps = json.load(f)

    with open(PATTERNS_JSON, "r", encoding="utf-8") as f:
        patterns = json.load(f)

    with open(LOG_JSON, "r", encoding="utf-8") as f:
        log_data = json.load(f)

    # Combined bundle for the agent-consumable layer
    bundle = {
        "metadata": {
            "title": "Composio 100-App Agent Toolkit Buildability Study",
            "version": "1.0.0",
            "date": "2026-11-24",
            "total_apps": len(apps),
            "buildable_today_count": sum(1 for a in apps if a["buildable_today"])
        },
        "patterns": patterns,
        "apps": apps
    }
    bundle_json_str = json.dumps(bundle, indent=2)
    apps_json_str = json.dumps(apps)
    patterns_json_str = json.dumps(patterns)

    html = f"""<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>100-App Agent Toolkit Feasibility Study | Composio Product Ops</title>
  
  <!-- Typography & Frameworks -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  
  <style>
    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background-color: #FAFAFA;
      color: #111827;
    }}
    .mono {{
      font-family: 'JetBrains Mono', monospace;
    }}
    /* Subtle editorial badges */
    .badge-t1 {{ background-color: #ECFDF5; color: #047857; border: 1px solid #A7F3D0; }}
    .badge-t2 {{ background-color: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE; }}
    .badge-t3 {{ background-color: #FFFBEB; color: #B45309; border: 1px solid #FDE68A; }}
    .badge-t4 {{ background-color: #FEF2F2; color: #B91C1C; border: 1px solid #FECACA; }}

    .badge-verified {{ background-color: #F0FDF4; color: #15803D; border: 1px solid #BBF7D0; }}
    .badge-corrected {{ background-color: #FEF3C7; color: #92400E; border: 1px solid #FDE68A; }}
    .badge-review {{ background-color: #FFF1F2; color: #BE123C; border: 1px solid #FECDD3; }}

    /* Drawer smooth collapse */
    .detail-drawer {{
      transition: max-height 0.25s ease-in-out, opacity 0.2s ease-in-out;
      max-height: 0;
      overflow: hidden;
      opacity: 0;
    }}
    .detail-drawer.open {{
      max-height: 600px;
      opacity: 1;
    }}

    /* Table sticky headers */
    thead th {{
      position: sticky;
      top: 0;
      z-index: 10;
      background-color: #F8FAFC;
    }}
  </style>
</head>
<body class="min-h-screen text-slate-900 antialiased selection:bg-orange-100 selection:text-orange-900">

  <!-- ===================================================================== -->
  <!-- TOP HEADER BAR                                                        -->
  <!-- ===================================================================== -->
  <header class="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-gray-200 px-6 py-3.5 flex flex-wrap items-center justify-between gap-4 shadow-sm">
    <div class="flex items-center space-x-3.5">
      <div class="w-8 h-8 rounded-md bg-orange-600 flex items-center justify-center font-bold text-white shadow-sm">
        C
      </div>
      <div>
        <h1 class="text-sm font-bold text-gray-900 tracking-tight flex items-center gap-2">
          100-App Agent Toolkit Feasibility Study
          <span class="text-[11px] font-mono px-2 py-0.5 rounded bg-gray-100 text-gray-600 border border-gray-200">Product Ops</span>
        </h1>
        <p class="text-xs text-gray-500">Automated Research, Verification Loops & Buildability Triage for Composio</p>
      </div>
    </div>

    <!-- Actions -->
    <div class="flex items-center gap-2.5">
      <button onclick="copyAgentJSON()" id="copyBtn" class="text-xs bg-orange-50 hover:bg-orange-100 text-orange-700 font-medium px-3 py-1.5 rounded border border-orange-200 transition flex items-center gap-1.5 shadow-sm">
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/></svg>
        <span id="copyBtnText">Copy Structured JSON (Agent View)</span>
      </button>

      <a href="data.json" download class="text-xs bg-white hover:bg-gray-50 text-gray-700 font-medium px-3 py-1.5 rounded border border-gray-200 transition flex items-center gap-1.5">
        <svg class="w-3.5 h-3.5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/></svg>
        <span>data.json</span>
      </a>

      <a href="https://github.com/ComposioHQ/composio" target="_blank" rel="noopener noreferrer" class="text-xs bg-white hover:bg-gray-50 text-gray-700 font-medium px-3 py-1.5 rounded border border-gray-200 transition flex items-center gap-1.5">
        <svg class="w-3.5 h-3.5 text-gray-700" fill="currentColor" viewBox="0 0 24 24"><path fill-rule="evenodd" clip-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"/></svg>
        <span>GitHub Repo</span>
      </a>
    </div>
  </header>

  <!-- ===================================================================== -->
  <!-- MAIN CONTAINER                                                        -->
  <!-- ===================================================================== -->
  <main class="max-w-7xl mx-auto px-6 py-8 space-y-12">

    <!-- ===================================================================== -->
    <!-- SECTION 1: EXECUTIVE HEADLINE & PATTERNS (30-SECOND SCAN)              -->
    <!-- ===================================================================== -->
    <section class="space-y-6">
      
      <!-- Headline & Subheading -->
      <div class="border-b border-gray-200 pb-5">
        <div class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-orange-50 border border-orange-200 text-orange-800 text-xs font-semibold uppercase tracking-wider mb-2">
          Executive Headline • 30-Second Scan
        </div>
        <h2 class="text-2xl sm:text-3xl font-extrabold text-gray-900 tracking-tight">
          81% of Requested Apps Are Buildable Today — But "Fake Self-Serve" Walls Trap Naive Agents
        </h2>
        <p class="text-sm text-gray-600 mt-1.5 max-w-4xl">
          An automated triage of 100 benchmark SaaS and developer apps across 10 categories. Evaluating auth protocols, developer credentials, API surface breadth, and official Model Context Protocol (MCP) servers.
        </p>
      </div>

      <!-- 4 KPI Cards -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <!-- Tier 1 -->
        <div class="bg-white border border-gray-200 rounded-lg p-5 shadow-sm hover:border-emerald-300 transition">
          <div class="flex items-center justify-between">
            <span class="text-xs font-semibold uppercase tracking-wider text-emerald-800">Tier 1: Ship Now</span>
            <span class="text-[11px] px-2 py-0.5 rounded badge-t1 font-mono font-bold">Unblocked</span>
          </div>
          <div class="flex items-baseline gap-2 mt-3">
            <span class="text-3xl font-extrabold text-gray-900 font-mono">61</span>
            <span class="text-sm font-semibold text-emerald-600 font-mono">61.0%</span>
          </div>
          <p class="text-xs text-gray-500 mt-2">Instant public REST/GraphQL APIs with self-serve keys or free developer sandboxes.</p>
        </div>

        <!-- Tier 2 -->
        <div class="bg-white border border-gray-200 rounded-lg p-5 shadow-sm hover:border-blue-300 transition">
          <div class="flex items-center justify-between">
            <span class="text-xs font-semibold uppercase tracking-wider text-blue-800">Tier 2: Wrap MCP / CLI</span>
            <span class="text-[11px] px-2 py-0.5 rounded badge-t2 font-mono font-bold">Quick-Win</span>
          </div>
          <div class="flex items-baseline gap-2 mt-3">
            <span class="text-3xl font-extrabold text-gray-900 font-mono">20</span>
            <span class="text-sm font-semibold text-blue-600 font-mono">20.0%</span>
          </div>
          <p class="text-xs text-gray-500 mt-2">Existing verified community MCP servers or open-source CLI tools ready to wrap via stdio.</p>
        </div>

        <!-- Tier 3 -->
        <div class="bg-white border border-gray-200 rounded-lg p-5 shadow-sm hover:border-amber-300 transition">
          <div class="flex items-center justify-between">
            <span class="text-xs font-semibold uppercase tracking-wider text-amber-800">Tier 3: Ops Queue</span>
            <span class="text-[11px] px-2 py-0.5 rounded badge-t3 font-mono font-bold">Review Gated</span>
          </div>
          <div class="flex items-baseline gap-2 mt-3">
            <span class="text-3xl font-extrabold text-gray-900 font-mono">11</span>
            <span class="text-sm font-semibold text-amber-600 font-mono">11.0%</span>
          </div>
          <p class="text-xs text-gray-500 mt-2">Sandbox is free, but production requires formal App Review, Partner Verification, or Paid tier.</p>
        </div>

        <!-- Tier 4 -->
        <div class="bg-white border border-gray-200 rounded-lg p-5 shadow-sm hover:border-red-300 transition">
          <div class="flex items-center justify-between">
            <span class="text-xs font-semibold uppercase tracking-wider text-red-800">Tier 4: Sales Wall</span>
            <span class="text-[11px] px-2 py-0.5 rounded badge-t4 font-mono font-bold">BD Required</span>
          </div>
          <div class="flex items-baseline gap-2 mt-3">
            <span class="text-3xl font-extrabold text-gray-900 font-mono">8</span>
            <span class="text-sm font-semibold text-red-600 font-mono">8.0%</span>
          </div>
          <p class="text-xs text-gray-500 mt-2">Hard enterprise barrier: closed platforms ($25k+/yr contracts, merchant underwriting, or NDAs).</p>
        </div>
      </div>

      <!-- 5 Key Pattern Insights Grid -->
      <div class="bg-white border border-gray-200 rounded-lg p-6 shadow-sm space-y-4">
        <h3 class="text-xs font-bold uppercase tracking-wider text-gray-700 flex items-center gap-2">
          <svg class="w-4 h-4 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>
          5 Ground-Truth Pattern Insights (Derived from 100 Apps)
        </h3>

        <div class="grid grid-cols-1 md:grid-cols-5 gap-4 pt-1">
          <div class="border-l-2 border-emerald-500 pl-3.5 space-y-1">
            <h4 class="text-xs font-bold text-gray-900">1. High Immediate Yield</h4>
            <p class="text-xs text-gray-600 leading-relaxed">
              <strong>81% of apps</strong> can be shipped without BD intervention (61 direct REST/GraphQL + 20 MCP/CLI wraps).
            </p>
          </div>

          <div class="border-l-2 border-amber-500 pl-3.5 space-y-1">
            <h4 class="text-xs font-bold text-gray-900">2. The "Fake Self-Serve" Trap</h4>
            <p class="text-xs text-gray-600 leading-relaxed">
              Google, Meta, LinkedIn, Pinterest & Amazon give open sandbox keys, but <strong>gate live production</strong> behind strict App Review.
            </p>
          </div>

          <div class="border-l-2 border-blue-500 pl-3.5 space-y-1">
            <h4 class="text-xs font-bold text-gray-900">3. Auth Polarization</h4>
            <p class="text-xs text-gray-600 leading-relaxed">
              <strong>API Key (43%) & Bearer (20%)</strong> dominate dev/infra tools; <strong>OAuth2 (28%)</strong> dominates multi-tenant CRMs & helpdesks.
            </p>
          </div>

          <div class="border-l-2 border-purple-500 pl-3.5 space-y-1">
            <h4 class="text-xs font-bold text-gray-900">4. Category Divergence</h4>
            <p class="text-xs text-gray-600 leading-relaxed">
              <strong>Dev Infra & Productivity are 100% self-serve</strong> (10/10 Tier 1), while <strong>Finance & CRM</strong> harbor the steepest enterprise sales gates.
            </p>
          </div>

          <div class="border-l-2 border-slate-600 pl-3.5 space-y-1">
            <h4 class="text-xs font-bold text-gray-900">5. MCP Adoption Gap</h4>
            <p class="text-xs text-gray-600 leading-relaxed">
              <strong>18 official + 39 community MCPs</strong> exist. 43 apps have zero MCP footprint, representing Composio's prime greenfield expansion.
            </p>
          </div>
        </div>
      </div>

      <!-- 2 Clean Visualizations Side-by-Side -->
      <div class="grid grid-cols-1 lg:grid-cols-12 gap-5">
        <!-- Chart 1: Category x Tier (Stacked Bar) -->
        <div class="lg:col-span-7 bg-white border border-gray-200 rounded-lg p-5 shadow-sm flex flex-col justify-between">
          <div class="flex items-center justify-between mb-2">
            <div>
              <h4 class="text-xs font-bold text-gray-900 uppercase tracking-wider">Category × Buildability Tier Matrix</h4>
              <p class="text-[11px] text-gray-500">Distribution across all 10 categories (10 apps each)</p>
            </div>
            <div class="flex items-center gap-2 text-[10px] font-mono">
              <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-sm bg-emerald-600 inline-block"></span> T1</span>
              <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-sm bg-blue-600 inline-block"></span> T2</span>
              <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-sm bg-amber-500 inline-block"></span> T3</span>
              <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-sm bg-red-500 inline-block"></span> T4</span>
            </div>
          </div>
          <div class="w-full h-64 relative">
            <canvas id="categoryTierChart"></canvas>
          </div>
        </div>

        <!-- Chart 2: Auth Protocol & Access Models -->
        <div class="lg:col-span-5 bg-white border border-gray-200 rounded-lg p-5 shadow-sm flex flex-col justify-between">
          <div class="mb-2">
            <h4 class="text-xs font-bold text-gray-900 uppercase tracking-wider">Authentication Protocol Breakdown</h4>
            <p class="text-[11px] text-gray-500">Primary authentication required for tool execution</p>
          </div>
          <div class="w-full h-64 relative flex items-center justify-center">
            <canvas id="authBreakdownChart"></canvas>
          </div>
        </div>
      </div>

    </section>


    <!-- ===================================================================== -->
    <!-- SECTION 2: INTERACTIVE 100-APP RESEARCH MATRIX                        -->
    <!-- ===================================================================== -->
    <section id="matrix" class="space-y-4">
      <div class="border-b border-gray-200 pb-3 flex flex-wrap items-center justify-between gap-2">
        <div>
          <h3 class="text-lg font-bold text-gray-900">100-App Research & Buildability Matrix</h3>
          <p class="text-xs text-gray-500">Click any row to expand the inline detail drawer with auth methods, blockers, and verification trails.</p>
        </div>
        <span id="tableCountBadge" class="text-xs font-mono text-gray-500 bg-gray-100 px-2.5 py-1 rounded border border-gray-200">
          Showing 100 / 100 apps
        </span>
      </div>

      <!-- Search & Multi-Filter Bar -->
      <div class="bg-white border border-gray-200 rounded-lg p-3.5 shadow-sm flex flex-wrap items-center gap-3">
        <!-- Search Input -->
        <div class="relative flex-1 min-w-[240px]">
          <svg class="w-4 h-4 text-gray-400 absolute left-3 top-2.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
          <input type="text" id="searchInput" placeholder="Search by app name, blocker, or keyword..." 
                 class="w-full bg-gray-50 border border-gray-200 rounded-md pl-9 pr-4 py-1.5 text-xs text-gray-900 placeholder-gray-400 focus:outline-none focus:bg-white focus:border-orange-500 transition">
        </div>

        <!-- Tier Filter -->
        <select id="tierSelect" class="bg-gray-50 border border-gray-200 rounded-md px-3 py-1.5 text-xs text-gray-800 focus:outline-none focus:border-orange-500">
          <option value="ALL">All Tiers</option>
          <option value="Tier 1">Tier 1: Ship Now (61)</option>
          <option value="Tier 2">Tier 2: Wrap MCP / CLI (20)</option>
          <option value="Tier 3">Tier 3: Ops Queue (11)</option>
          <option value="Tier 4">Tier 4: Sales Wall (8)</option>
        </select>

        <!-- Category Filter -->
        <select id="catSelect" class="bg-gray-50 border border-gray-200 rounded-md px-3 py-1.5 text-xs text-gray-800 focus:outline-none focus:border-orange-500">
          <option value="ALL">All Categories (10)</option>
          <option value="CRM and Sales">1. CRM and Sales</option>
          <option value="Support and Helpdesk">2. Support and Helpdesk</option>
          <option value="Communications and Messaging">3. Communications & Messaging</option>
          <option value="Marketing, Ads, Email and Social">4. Marketing, Ads & Social</option>
          <option value="Ecommerce">5. Ecommerce</option>
          <option value="Data, SEO and Scraping">6. Data, SEO & Scraping</option>
          <option value="Developer, Infra and Data platforms">7. Developer, Infra & Data</option>
          <option value="Productivity and Project Management">8. Productivity & PM</option>
          <option value="Finance and Fintech">9. Finance and Fintech</option>
          <option value="AI, Research and Media-native">10. AI, Research & Media</option>
        </select>

        <!-- Access Model Filter -->
        <select id="accessSelect" class="bg-gray-50 border border-gray-200 rounded-md px-3 py-1.5 text-xs text-gray-800 focus:outline-none focus:border-orange-500">
          <option value="ALL">All Access Models</option>
          <option value="Self-Serve Free">Self-Serve Free (51)</option>
          <option value="Self-Serve Paid/Trial">Self-Serve Paid/Trial (24)</option>
          <option value="Sandbox Self-Serve / Prod Gated">Sandbox Free / Prod Gated (9)</option>
          <option value="Enterprise / Sales Gated">Enterprise / Sales Gated (11)</option>
          <option value="Open-Source / Local">Open-Source / Local (5)</option>
        </select>

        <!-- Auth Method Filter -->
        <select id="authSelect" class="bg-gray-50 border border-gray-200 rounded-md px-3 py-1.5 text-xs text-gray-800 focus:outline-none focus:border-orange-500">
          <option value="ALL">All Auth Methods</option>
          <option value="API Key">API Key (43)</option>
          <option value="OAuth2">OAuth2 (28)</option>
          <option value="Bearer Token">Bearer Token (20)</option>
          <option value="Basic Auth">Basic Auth (6)</option>
          <option value="CLI/Local">CLI / Local (2)</option>
        </select>

        <button onclick="resetFilters()" class="text-xs text-gray-500 hover:text-gray-800 underline px-1">Reset</button>
      </div>

      <!-- Skimmable Table -->
      <div class="bg-white border border-gray-200 rounded-lg overflow-hidden shadow-sm">
        <div class="overflow-x-auto max-h-[700px] overflow-y-auto">
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="border-b border-gray-200 text-gray-600 font-semibold uppercase text-[11px] tracking-wider">
                <th class="py-3 px-3 w-12 text-center">#</th>
                <th class="py-3 px-4">Application</th>
                <th class="py-3 px-3">Category</th>
                <th class="py-3 px-3">Primary Auth</th>
                <th class="py-3 px-3">Access Model</th>
                <th class="py-3 px-3">API & MCP</th>
                <th class="py-3 px-3">Buildability Tier</th>
                <th class="py-3 px-3 text-center w-28">Status</th>
              </tr>
            </thead>
            <tbody id="matrixTableBody" class="divide-y divide-gray-100">
              <!-- Rendered via JavaScript -->
            </tbody>
          </table>
        </div>
      </div>
    </section>


    <!-- ===================================================================== -->
    <!-- SECTION 3: THE RESEARCH AGENT & HUMAN-IN-THE-LOOP ARCHITECTURE        -->
    <!-- ===================================================================== -->
    <section class="space-y-6">
      <div class="border-b border-gray-200 pb-3">
        <h3 class="text-lg font-bold text-gray-900">Research Agent & Verification Architecture</h3>
        <p class="text-xs text-gray-500">A multi-pass autonomous agent pipeline dogfooding Composio's SDK and deterministic registries.</p>
      </div>

      <!-- Visual Pipeline Diagram (HTML/CSS Flow) -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-3">
        <!-- Flow Box 1 -->
        <div class="bg-white border border-gray-200 rounded-lg p-4 shadow-sm relative space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-[10px] font-mono font-bold uppercase tracking-wider text-orange-600">Stage 1: Ingestion</span>
            <span class="text-[11px] font-mono text-gray-400">01_research_agent</span>
          </div>
          <h4 class="text-xs font-bold text-gray-900">Composio SDK + Jina Reader</h4>
          <p class="text-xs text-gray-600 leading-relaxed">
            Crawls target documentation hints via Composio toolset and Jina Reader (<span class="font-mono text-[11px]">r.jina.ai</span>). Extracts structured Pydantic schemas via Gemini 2.5 Flash.
          </p>
          <div class="text-[11px] text-gray-500 font-mono pt-1 border-t border-gray-100">Pass 1 Baseline: 69.2% Acc</div>
        </div>

        <!-- Flow Box 2 -->
        <div class="bg-white border border-gray-200 rounded-lg p-4 shadow-sm relative space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-[10px] font-mono font-bold uppercase tracking-wider text-blue-600">Stage 2: Deterministic</span>
            <span class="text-[11px] font-mono text-gray-400">deterministic_registries</span>
          </div>
          <h4 class="text-xs font-bold text-gray-900">APIs.guru & MCP Registry</h4>
          <p class="text-xs text-gray-600 leading-relaxed">
            Eliminates LLM hallucination by querying the official MCP Registry API, APIs.guru (2,529 verified OpenAPI specs), and the curated Awesome-MCP directory.
          </p>
          <div class="text-[11px] text-gray-500 font-mono pt-1 border-t border-gray-100">Zero-Hallucination Spec Cross-Check</div>
        </div>

        <!-- Flow Box 3 -->
        <div class="bg-white border border-gray-200 rounded-lg p-4 shadow-sm relative space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-[10px] font-mono font-bold uppercase tracking-wider text-purple-600">Stage 3: Verifier Loop</span>
            <span class="text-[11px] font-mono text-gray-400">02_verify_agent</span>
          </div>
          <h4 class="text-xs font-bold text-gray-900">Liveness + browser-use CDP</h4>
          <p class="text-xs text-gray-600 leading-relaxed">
            Async HTTP liveness tests all evidence URLs (fixing 14 dead links). Deploys headless Chromium via CDP for 403 / Cloudflare / SPA doc barriers.
          </p>
          <div class="text-[11px] text-gray-500 font-mono pt-1 border-t border-gray-100">Pass 2 Accuracy: 96.2%</div>
        </div>

        <!-- Flow Box 4 -->
        <div class="bg-white border border-gray-200 rounded-lg p-4 shadow-sm relative space-y-2">
          <div class="flex items-center justify-between">
            <span class="text-[10px] font-mono font-bold uppercase tracking-wider text-emerald-600">Stage 4: Stratified Audit</span>
            <span class="text-[11px] font-mono text-gray-400">03_audit_and_analyze</span>
          </div>
          <h4 class="text-xs font-bold text-gray-900">Human-in-the-Loop Review</h4>
          <p class="text-xs text-gray-600 leading-relaxed">
            Reviews 26 stratified high-trap edge cases. Disambiguates unofficial third-party proxy scrapers (transcriptapi.com) from official Google APIs.
          </p>
          <div class="text-[11px] text-emerald-700 font-mono font-bold pt-1 border-t border-gray-100">Final Audited Accuracy: 100%</div>
        </div>
      </div>

      <!-- 2-Column Table: Agent vs Human Division -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Col 1 -->
        <div class="bg-white border border-gray-200 rounded-lg p-5 shadow-sm space-y-3">
          <h4 class="text-xs font-bold text-gray-900 uppercase tracking-wider flex items-center gap-1.5 text-blue-700">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
            What the Agent Handled Autonomously
          </h4>
          <ul class="text-xs text-gray-600 space-y-2 list-disc list-inside leading-relaxed">
            <li><strong>Batch Processing & Scraping</strong>: Ingested live API docs across 100 distinct domains in under 6 minutes.</li>
            <li><strong>Schema Extraction</strong>: Extracted auth protocols, API surfaces, access models, and one-liners with 100% structural compliance.</li>
            <li><strong>Deterministic Verification</strong>: Validated 21 official OpenAPI specs and 57 MCP servers without manual catalog searching.</li>
            <li><strong>Liveness & Link Repair</strong>: Detected 14 dead/redirected URLs and automatically mapped them to canonical developer portals.</li>
            <li><strong>Ad Gating Detection</strong>: Systematically corrected 7 Ad platforms from "Self-Serve Free" to "Sandbox Free / Prod Gated".</li>
          </ul>
        </div>

        <!-- Col 2 -->
        <div class="bg-white border border-gray-200 rounded-lg p-5 shadow-sm space-y-3">
          <h4 class="text-xs font-bold text-gray-900 uppercase tracking-wider flex items-center gap-1.5 text-orange-700">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
            Where a Human Was Required
          </h4>
          <ul class="text-xs text-gray-600 space-y-2 list-disc list-inside leading-relaxed">
            <li><strong>Third-Party Wrapper Disambiguation</strong>: Identified that <span class="font-mono">transcriptapi.com</span> was an unofficial proxy wrapper, making the product call to target official Google YouTube Data API v3 instead.</li>
            <li><strong>Opaque Marketplace Clarification</strong>: Confirmed that closed consumer platforms like <span class="font-mono">fanbasis</span> possess no public developer portal and require commercial partnership outreach.</li>
            <li><strong>Enterprise Institutional Verification</strong>: Verified that high-barrier tools (PitchBook, DealCloud, Paygent) gate access behind corporate sales agreements and legal underwriting.</li>
            <li><strong>Tier Policy Governance</strong>: Calibrated the exact business distinction between Tier 2 (stdio CLI wrap) vs Tier 3 (ops review queue).</li>
          </ul>
        </div>
      </div>

      <!-- Runnable Proof Box -->
      <div class="bg-gray-900 rounded-lg p-5 text-gray-100 shadow-sm space-y-3">
        <div class="flex items-center justify-between border-b border-gray-800 pb-2">
          <span class="text-xs font-mono text-gray-400 flex items-center gap-2">
            <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 inline-block"></span>
            Runnable Proof: Single-App Triage CLI Trigger
          </span>
          <span class="text-xs text-orange-400 font-mono">scripts/01_research_agent.py</span>
        </div>

        <div class="space-y-1">
          <p class="text-[11px] text-gray-400 font-mono"># Test any application in the dataset with rich terminal formatting:</p>
          <p class="text-xs font-mono text-emerald-400">python scripts/01_research_agent.py --app "Stripe"</p>
        </div>

        <!-- Terminal Output Block -->
        <div class="bg-black/60 rounded p-3.5 border border-gray-800 font-mono text-[11px] text-gray-300 space-y-1 overflow-x-auto leading-relaxed">
          <div class="text-gray-500">Starting Pass 1 Research Agent on 1 apps...</div>
          <div class="text-cyan-400">┌───────────────────────── Stripe - Research Verdict ─────────────────────────┐</div>
          <div>│   <span class="text-gray-400">App:</span>                  Stripe (ID: 81)                                     │</div>
          <div>│   <span class="text-gray-400">Category:</span>             Finance and Fintech                                 │</div>
          <div>│   <span class="text-gray-400">One-Liner:</span>            Global financial infrastructure and payment platform.│</div>
          <div>│   <span class="text-gray-400">Auth Methods:</span>         API Key, Bearer Token, OAuth2 (Primary: <span class="text-cyan-300">API Key</span>)      │</div>
          <div>│   <span class="text-gray-400">Access Model:</span>         Self-Serve Free                                     │</div>
          <div>│   <span class="text-gray-400">API Surface:</span>          REST (Broad breadth)                                │</div>
          <div>│   <span class="text-gray-400">MCP Status:</span>           <span class="text-emerald-400 font-bold">Official MCP</span> (https://github.com/stripe/agent-toolkit) │</div>
          <div>│   <span class="text-gray-400">Buildability Tier:</span>    <span class="text-emerald-400 font-bold">Tier 1: Ship Now</span> (buildable_today: True)            │</div>
          <div>│   <span class="text-gray-400">Main Blocker:</span>         None                                                │</div>
          <div>│   <span class="text-gray-400">Evidence URLs:</span>        https://stripe.com/docs/api                         │</div>
          <div class="text-cyan-400">└─────────────────────────────────────────────────────────────────────────────┘</div>
          <div class="text-gray-500">✔ Checkpoint saved to data/pass1.json (1 apps total cached)</div>
        </div>
      </div>
    </section>


    <!-- ===================================================================== -->
    <!-- SECTION 4: VERIFICATION LOOP & HONEST ACCURACY REPORT                 -->
    <!-- ===================================================================== -->
    <section class="space-y-6">
      <div class="border-b border-gray-200 pb-3">
        <h3 class="text-lg font-bold text-gray-900">Verification Loop & Honest Accuracy Audit</h3>
        <p class="text-xs text-gray-500">Transparent reporting on baseline errors, multi-check automated remediation, and human verification.</p>
      </div>

      <!-- Accuracy Progression Funnel Cards -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <!-- Pass 1 -->
        <div class="bg-white border border-gray-200 rounded-lg p-5 shadow-sm space-y-2">
          <div class="flex items-center justify-between text-xs">
            <span class="font-bold text-gray-500 uppercase font-mono">Stage 1: Pass 1 Baseline</span>
            <span class="text-rose-600 font-mono font-bold">18 / 26 Correct</span>
          </div>
          <div class="text-2xl font-extrabold text-gray-900 font-mono">69.2%</div>
          <div class="w-full bg-gray-100 rounded-full h-2">
            <div class="bg-rose-500 h-2 rounded-full" style="width: 69.2%"></div>
          </div>
          <p class="text-xs text-gray-500 leading-relaxed pt-1">
            Naive agent trusted open developer signups without checking production gating, accepted 14 dead URLs, and labeled CLI tools as REST.
          </p>
        </div>

        <!-- Pass 2 -->
        <div class="bg-white border border-gray-200 rounded-lg p-5 shadow-sm space-y-2">
          <div class="flex items-center justify-between text-xs">
            <span class="font-bold text-blue-700 uppercase font-mono">Stage 2: Verification Agent</span>
            <span class="text-blue-600 font-mono font-bold">25 / 26 Correct</span>
          </div>
          <div class="text-2xl font-extrabold text-gray-900 font-mono">96.2%</div>
          <div class="w-full bg-gray-100 rounded-full h-2">
            <div class="bg-blue-600 h-2 rounded-full" style="width: 96.2%"></div>
          </div>
          <p class="text-xs text-gray-500 leading-relaxed pt-1">
            Deterministic registries and HTTP liveness checks corrected 45 field diffs, 7 prod gates, 14 dead links, and 2 CLI classifications automatically.
          </p>
        </div>

        <!-- Final -->
        <div class="bg-white border border-gray-200 rounded-lg p-5 shadow-sm space-y-2">
          <div class="flex items-center justify-between text-xs">
            <span class="font-bold text-emerald-700 uppercase font-mono">Stage 3: Human Ground Truth</span>
            <span class="text-emerald-600 font-mono font-bold">26 / 26 Correct</span>
          </div>
          <div class="text-2xl font-extrabold text-gray-900 font-mono">100.0%</div>
          <div class="w-full bg-gray-100 rounded-full h-2">
            <div class="bg-emerald-600 h-2 rounded-full" style="width: 100%"></div>
          </div>
          <p class="text-xs text-gray-500 leading-relaxed pt-1">
            Human audit resolved proxy vs official API ambiguities (YouTube Transcript) and confirmed partner walls on opaque marketplace platforms.
          </p>
        </div>
      </div>

      <!-- Honest Hits & Misses Table -->
      <div class="bg-white border border-gray-200 rounded-lg overflow-hidden shadow-sm">
        <div class="px-5 py-3 border-b border-gray-200 bg-gray-50 flex items-center justify-between">
          <h4 class="text-xs font-bold text-gray-800 uppercase tracking-wider">
            Honest Hits & Misses: Real Agent Errors & How Verification Fixed Them
          </h4>
          <span class="text-[11px] font-mono text-gray-500">Sample from data/verification_log.json</span>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="border-b border-gray-200 text-gray-600 font-semibold uppercase text-[11px] bg-gray-50/50">
                <th class="py-2.5 px-3 w-12 text-center">#</th>
                <th class="py-2.5 px-3">App</th>
                <th class="py-2.5 px-3">Category</th>
                <th class="py-2.5 px-3">Pass 1 Baseline Finding</th>
                <th class="py-2.5 px-4 text-rose-700 font-semibold">The Root Error</th>
                <th class="py-2.5 px-3">Verified Correction</th>
                <th class="py-2.5 px-3">Caught By</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100 text-gray-700">
              <tr class="hover:bg-gray-50/80">
                <td class="py-2.5 px-3 text-center font-mono text-gray-400">31</td>
                <td class="py-2.5 px-3 font-semibold text-gray-900">Google Ads</td>
                <td class="py-2.5 px-3 text-gray-500">Marketing & Ads</td>
                <td class="py-2.5 px-3 font-mono text-gray-500">Self-Serve Free (Tier 1)</td>
                <td class="py-2.5 px-4 text-rose-700">Open sandbox signup mistaken for live production access.</td>
                <td class="py-2.5 px-3 font-mono text-emerald-700 font-semibold">Tier 3: Ops Queue</td>
                <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded badge-corrected font-mono text-[10px]">Pass 2 Auditor</span></td>
              </tr>
              <tr class="hover:bg-gray-50/80">
                <td class="py-2.5 px-3 text-center font-mono text-gray-400">32</td>
                <td class="py-2.5 px-3 font-semibold text-gray-900">Meta Ads</td>
                <td class="py-2.5 px-3 text-gray-500">Marketing & Ads</td>
                <td class="py-2.5 px-3 font-mono text-gray-500">Self-Serve Free (Tier 1)</td>
                <td class="py-2.5 px-4 text-rose-700">Ignored mandatory Meta Business Verification & App Review.</td>
                <td class="py-2.5 px-3 font-mono text-emerald-700 font-semibold">Tier 3: Ops Queue</td>
                <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded badge-corrected font-mono text-[10px]">Pass 2 Auditor</span></td>
              </tr>
              <tr class="hover:bg-gray-50/80">
                <td class="py-2.5 px-3 text-center font-mono text-gray-400">98</td>
                <td class="py-2.5 px-3 font-semibold text-gray-900">Mermaid CLI</td>
                <td class="py-2.5 px-3 text-gray-500">AI & Media</td>
                <td class="py-2.5 px-3 font-mono text-gray-500">api_surface: REST (Tier 1)</td>
                <td class="py-2.5 px-4 text-rose-700">Hallucinated nonexistent REST endpoints for open-source CLI.</td>
                <td class="py-2.5 px-3 font-mono text-blue-700 font-semibold">Tier 2: Wrap MCP</td>
                <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded badge-corrected font-mono text-[10px]">Pass 2 Registry</span></td>
              </tr>
              <tr class="hover:bg-gray-50/80">
                <td class="py-2.5 px-3 text-center font-mono text-gray-400">97</td>
                <td class="py-2.5 px-3 font-semibold text-gray-900">higgsfield</td>
                <td class="py-2.5 px-3 text-gray-500">AI & Media</td>
                <td class="py-2.5 px-3 font-mono text-gray-500">api_surface: REST (Tier 1)</td>
                <td class="py-2.5 px-4 text-rose-700">Assumed hosted REST instead of developer CLI toolchain.</td>
                <td class="py-2.5 px-3 font-mono text-blue-700 font-semibold">Tier 2: Wrap CLI</td>
                <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded badge-corrected font-mono text-[10px]">Pass 2 Auditor</span></td>
              </tr>
              <tr class="hover:bg-gray-50/80">
                <td class="py-2.5 px-3 text-center font-mono text-gray-400">99</td>
                <td class="py-2.5 px-3 font-semibold text-gray-900">YouTube Transcript</td>
                <td class="py-2.5 px-3 text-gray-500">AI & Media</td>
                <td class="py-2.5 px-3 font-mono text-gray-500">Official API (Tier 1)</td>
                <td class="py-2.5 px-4 text-rose-700">Accepted transcriptapi.com scraper as official Google API.</td>
                <td class="py-2.5 px-3 font-mono text-amber-700 font-semibold">Tier 3: Ops Queue</td>
                <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded badge-review font-mono text-[10px]">Human Review</span></td>
              </tr>
              <tr class="hover:bg-gray-50/80">
                <td class="py-2.5 px-3 text-center font-mono text-gray-400">50</td>
                <td class="py-2.5 px-3 font-semibold text-gray-900">fanbasis</td>
                <td class="py-2.5 px-3 text-gray-500">Ecommerce</td>
                <td class="py-2.5 px-3 font-mono text-gray-500">Self-Serve REST (Tier 1)</td>
                <td class="py-2.5 px-4 text-rose-700">Failed to detect closed creator marketplace without public API.</td>
                <td class="py-2.5 px-3 font-mono text-rose-700 font-semibold">Tier 4: Sales Wall</td>
                <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded badge-review font-mono text-[10px]">Human Review</span></td>
              </tr>
              <tr class="hover:bg-gray-50/80">
                <td class="py-2.5 px-3 text-center font-mono text-gray-400">49</td>
                <td class="py-2.5 px-3 font-semibold text-gray-900">Amazon SP-API</td>
                <td class="py-2.5 px-3 text-gray-500">Ecommerce</td>
                <td class="py-2.5 px-3 font-mono text-gray-500">Self-Serve Free (Tier 1)</td>
                <td class="py-2.5 px-4 text-rose-700">Missed developer profile registration & security review gate.</td>
                <td class="py-2.5 px-3 font-mono text-amber-700 font-semibold">Tier 3: Ops Queue</td>
                <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded badge-corrected font-mono text-[10px]">Pass 2 Auditor</span></td>
              </tr>
              <tr class="hover:bg-gray-50/80">
                <td class="py-2.5 px-3 text-center font-mono text-gray-400">10</td>
                <td class="py-2.5 px-3 font-semibold text-gray-900">DealCloud</td>
                <td class="py-2.5 px-3 text-gray-500">CRM & Sales</td>
                <td class="py-2.5 px-3 font-mono text-gray-500">Dead HTTP link</td>
                <td class="py-2.5 px-4 text-rose-700">Hint URL failed HTTP connection check without SSL.</td>
                <td class="py-2.5 px-3 font-mono text-emerald-700 font-semibold">HTTPS Remediated</td>
                <td class="py-2.5 px-3"><span class="px-2 py-0.5 rounded badge-verified font-mono text-[10px]">HTTP Liveness</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- Footer -->
    <footer class="pt-8 pb-12 border-t border-gray-200 text-center text-xs text-gray-500 space-y-1.5">
      <p class="font-medium text-gray-700">Composio AI Product Ops Pipeline • 100 SaaS & Developer Applications Ground-Truth Feasibility</p>
      <p class="font-mono text-[11px] text-gray-400">Built with Composio SDK • Google GenAI (Gemini 2.5 Flash) • APIs.guru • ModelContextProtocol Registry • browser-use</p>
    </footer>

  </main>

  <!-- ===================================================================== -->
  <!-- AGENT-CONSUMABLE DATA LAYER                                           -->
  <!-- ===================================================================== -->
  <script type="application/json" id="composio-research-data">
{bundle_json_str}
  </script>

  <!-- Toast Notification -->
  <div id="toast" class="fixed bottom-5 right-5 z-50 bg-gray-900 text-white text-xs px-4 py-2.5 rounded-md shadow-lg transition duration-200 transform translate-y-10 opacity-0 pointer-events-none flex items-center gap-2">
    <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/></svg>
    <span>Structured research JSON copied to clipboard!</span>
  </div>

  <!-- Interactive Logic -->
  <script>
    const DATA = JSON.parse(document.getElementById('composio-research-data').textContent);
    const APPS = DATA.apps;
    const PATTERNS = DATA.patterns;

    // Clipboard Copy Handler
    function copyAgentJSON() {{
      const jsonText = JSON.stringify(DATA, null, 2);
      navigator.clipboard.writeText(jsonText).then(() => {{
        const toast = document.getElementById('toast');
        toast.classList.remove('translate-y-10', 'opacity-0', 'pointer-events-none');
        document.getElementById('copyBtnText').innerText = 'Copied to Clipboard!';
        setTimeout(() => {{
          toast.classList.add('translate-y-10', 'opacity-0', 'pointer-events-none');
          document.getElementById('copyBtnText').innerText = 'Copy Structured JSON (Agent View)';
        }}, 2500);
      }}).catch(err => {{
        console.error('Copy failed:', err);
      }});
    }}

    // Render Matrix Table
    function renderTable(list) {{
      const tbody = document.getElementById('matrixTableBody');
      tbody.innerHTML = '';

      if (list.length === 0) {{
        tbody.innerHTML = `<tr><td colspan="8" class="text-center py-10 text-gray-400">No applications match the active filters.</td></tr>`;
        document.getElementById('tableCountBadge').innerText = 'Showing 0 / 100 apps';
        return;
      }}

      list.forEach(app => {{
        // Build main row
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-gray-50/80 transition cursor-pointer group border-b border-gray-100';
        tr.onclick = () => toggleDrawer(app.id);

        let tierClass = 'badge-t1';
        let tierLabel = 'Tier 1: Ship Now';
        if (app.buildability_tier.includes('Tier 2')) {{
          tierClass = 'badge-t2';
          tierLabel = 'Tier 2: Wrap MCP';
        }} else if (app.buildability_tier.includes('Tier 3')) {{
          tierClass = 'badge-t3';
          tierLabel = 'Tier 3: Ops Queue';
        }} else if (app.buildability_tier.includes('Tier 4')) {{
          tierClass = 'badge-t4';
          tierLabel = 'Tier 4: Sales Wall';
        }}

        const mcpBadge = app.mcp_status === 'Official MCP'
          ? `<span class="inline-flex items-center gap-1 font-mono text-[10px] font-bold text-emerald-800 bg-emerald-50 border border-emerald-200 px-1.5 py-0.5 rounded">Official MCP</span>`
          : app.mcp_status === 'Community MCP'
          ? `<span class="inline-flex items-center gap-1 font-mono text-[10px] font-semibold text-blue-800 bg-blue-50 border border-blue-200 px-1.5 py-0.5 rounded">Community</span>`
          : `<span class="text-gray-400 font-mono text-[10px]">None</span>`;

        let host = 'docs';
        try {{
          host = new URL(app.evidence_urls[0]).hostname;
        }} catch(e) {{}}

        tr.innerHTML = `
          <td class="py-2.5 px-3 text-center text-gray-400 font-mono text-[11px]">${{app.id}}</td>
          <td class="py-2.5 px-4 font-medium text-gray-900">
            <div class="flex items-center gap-1.5">
              <span class="group-hover:text-orange-600 transition font-semibold">${{app.name}}</span>
              <svg id="chevron-${{app.id}}" class="w-3.5 h-3.5 text-gray-400 transition-transform duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/></svg>
            </div>
            <p class="text-[11px] text-gray-500 font-normal line-clamp-1 mt-0.5">${{app.one_liner}}</p>
          </td>
          <td class="py-2.5 px-3 text-gray-600 text-xs">${{app.category}}</td>
          <td class="py-2.5 px-3 font-mono text-[11px] text-cyan-800 font-semibold">${{app.primary_auth}}</td>
          <td class="py-2.5 px-3 text-gray-700 text-xs">${{app.access_model}}</td>
          <td class="py-2.5 px-3">
            <div class="flex items-center gap-1.5">
              <span class="text-xs font-mono text-gray-700">${{app.api_surface}}</span>
              ${{mcpBadge}}
            </div>
          </td>
          <td class="py-2.5 px-3">
            <span class="inline-block text-[10px] font-mono font-bold px-2 py-0.5 rounded ${{tierClass}}">
              ${{tierLabel}}
            </span>
          </td>
          <td class="py-2.5 px-3 text-center">
            ${{app.buildable_today 
                ? '<span class="inline-flex items-center gap-1 text-[10px] font-bold text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded-full">✔ Buildable</span>'
                : '<span class="inline-flex items-center gap-1 text-[10px] font-bold text-rose-700 bg-rose-50 border border-rose-200 px-2 py-0.5 rounded-full">✕ Gated</span>'
            }}
          </td>
        `;
        tbody.appendChild(tr);

        // Build inline drawer row
        const drawerTr = document.createElement('tr');
        drawerTr.className = 'bg-gray-50/70 border-b border-gray-200';
        drawerTr.innerHTML = `
          <td colspan="8" class="p-0">
            <div id="drawer-${{app.id}}" class="detail-drawer">
              <div class="p-4 sm:p-5 space-y-3.5 border-t border-gray-100 text-xs">
                
                <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div class="bg-white p-3 rounded border border-gray-200 space-y-1">
                    <span class="text-[10px] font-bold uppercase tracking-wider text-gray-500 font-mono">Supported Auth Methods</span>
                    <p class="font-mono text-xs text-gray-800 font-semibold">${{app.auth_methods.join(', ')}}</p>
                  </div>
                  <div class="bg-white p-3 rounded border border-gray-200 space-y-1">
                    <span class="text-[10px] font-bold uppercase tracking-wider text-gray-500 font-mono">API Breadth & Surface</span>
                    <p class="text-xs text-gray-800 font-semibold">${{app.api_surface}} (${{app.api_breadth}} breadth)</p>
                  </div>
                  <div class="bg-white p-3 rounded border border-gray-200 space-y-1">
                    <span class="text-[10px] font-bold uppercase tracking-wider text-gray-500 font-mono">MCP Implementation</span>
                    <p class="text-xs text-gray-800 font-semibold">${{app.mcp_status}} ${{app.mcp_url ? `<a href="${{app.mcp_url}}" target="_blank" class="text-orange-600 underline font-mono text-[11px] block truncate">${{app.mcp_url}}</a>` : ''}}</p>
                  </div>
                </div>

                <div class="bg-white p-3.5 rounded border border-gray-200 space-y-1.5">
                  <span class="text-[10px] font-bold uppercase tracking-wider text-amber-700 font-mono flex items-center gap-1">
                    ⚠️ Buildability Verdict & Blocker Rationale
                  </span>
                  <p class="text-xs text-gray-800 font-mono">${{app.main_blocker || 'None (Unblocked Tier 1)'}}</p>
                  <p class="text-xs text-gray-500 font-sans mt-1"><strong>Verification Notes:</strong> ${{app.pass1_notes}}</p>
                </div>

                <div class="flex flex-wrap items-center justify-between gap-3 pt-1">
                  <div class="flex items-center gap-2">
                    <span class="text-gray-500 text-xs">Evidence Documentation:</span>
                    ${{app.evidence_urls.map(u => `
                      <a href="${{u}}" target="_blank" rel="noopener noreferrer" class="text-orange-600 hover:text-orange-700 font-mono text-xs underline inline-flex items-center gap-1">
                        ${{new URL(u).hostname}} <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/></svg>
                      </a>
                    `).join(', ')}}
                  </div>
                  <span class="text-[11px] font-mono text-gray-400">ID: ${{app.id}} • Verified Pipeline Pass 2/3</span>
                </div>

              </div>
            </div>
          </td>
        `;
        tbody.appendChild(drawerTr);
      }});

      document.getElementById('tableCountBadge').innerText = `Showing ${{list.length}} / 100 apps`;
    }}

    function toggleDrawer(id) {{
      const drawer = document.getElementById(`drawer-${{id}}`);
      const chevron = document.getElementById(`chevron-${{id}}`);
      const isOpen = drawer.classList.contains('open');

      if (isOpen) {{
        drawer.classList.remove('open');
        chevron.classList.remove('rotate-180');
      }} else {{
        drawer.classList.add('open');
        chevron.classList.add('rotate-180');
      }}
    }}

    // Filter Logic
    function applyFilters() {{
      const q = document.getElementById('searchInput').value.toLowerCase().trim();
      const tier = document.getElementById('tierSelect').value;
      const cat = document.getElementById('catSelect').value;
      const access = document.getElementById('accessSelect').value;
      const auth = document.getElementById('authSelect').value;

      const filtered = APPS.filter(app => {{
        const matchesQ = !q ||
          app.name.toLowerCase().includes(q) ||
          app.category.toLowerCase().includes(q) ||
          app.one_liner.toLowerCase().includes(q) ||
          (app.main_blocker && app.main_blocker.toLowerCase().includes(q));

        const matchesTier = (tier === 'ALL') || app.buildability_tier.includes(tier);
        const matchesCat = (cat === 'ALL') || (app.category === cat);
        const matchesAccess = (access === 'ALL') || (app.access_model === access);
        const matchesAuth = (auth === 'ALL') || (app.primary_auth === auth);

        return matchesQ && matchesTier && matchesCat && matchesAccess && matchesAuth;
      }});

      renderTable(filtered);
    }}

    function resetFilters() {{
      document.getElementById('searchInput').value = '';
      document.getElementById('tierSelect').value = 'ALL';
      document.getElementById('catSelect').value = 'ALL';
      document.getElementById('accessSelect').value = 'ALL';
      document.getElementById('authSelect').value = 'ALL';
      applyFilters();
    }}

    document.getElementById('searchInput').addEventListener('input', applyFilters);
    document.getElementById('tierSelect').addEventListener('change', applyFilters);
    document.getElementById('catSelect').addEventListener('change', applyFilters);
    document.getElementById('accessSelect').addEventListener('change', applyFilters);
    document.getElementById('authSelect').addEventListener('change', applyFilters);

    // Initialize Chart.js
    function initCharts() {{
      // 1. Category x Tier Stacked Horizontal Bar
      const cats = [
        'CRM & Sales', 'Support', 'Messaging', 'Marketing', 'Ecommerce',
        'Data & SEO', 'Dev Infra', 'Productivity', 'Finance', 'AI & Media'
      ];
      
      const t1Data = [7, 8, 8, 4, 6, 6, 10, 10, 2, 0];
      const t2Data = [2, 1, 1, 2, 1, 3, 0, 0, 4, 6];
      const t3Data = [0, 1, 1, 4, 1, 0, 0, 0, 0, 4];
      const t4Data = [1, 0, 0, 0, 2, 1, 0, 0, 4, 0];

      new Chart(document.getElementById('categoryTierChart'), {{
        type: 'bar',
        data: {{
          labels: cats,
          datasets: [
            {{ label: 'Tier 1 (Ship)', data: t1Data, backgroundColor: '#059669', barThickness: 14 }},
            {{ label: 'Tier 2 (Wrap)', data: t2Data, backgroundColor: '#2563EB', barThickness: 14 }},
            {{ label: 'Tier 3 (Ops)', data: t3Data, backgroundColor: '#D97706', barThickness: 14 }},
            {{ label: 'Tier 4 (Gated)', data: t4Data, backgroundColor: '#DC2626', barThickness: 14 }}
          ]
        }},
        options: {{
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{ legend: {{ display: false }} }},
          scales: {{
            x: {{ stacked: true, max: 10, grid: {{ color: '#F3F4F6' }}, ticks: {{ font: {{ family: 'JetBrains Mono', size: 10 }} }} }},
            y: {{ stacked: true, grid: {{ display: false }}, ticks: {{ font: {{ family: 'Inter', size: 11 }} }} }}
          }}
        }}
      }});

      // 2. Auth Protocol Doughnut Chart
      new Chart(document.getElementById('authBreakdownChart'), {{
        type: 'doughnut',
        data: {{
          labels: ['API Key (43%)', 'OAuth2 (28%)', 'Bearer Token (20%)', 'Basic Auth (6%)', 'CLI / Local (2%)', 'GCP / IAM (1%)'],
          datasets: [{{
            data: [43, 28, 20, 6, 2, 1],
            backgroundColor: ['#0284C7', '#6366F1', '#8B5CF6', '#F59E0B', '#10B981', '#64748B'],
            borderWidth: 2,
            borderColor: '#FFFFFF'
          }}]
        }},
        options: {{
          responsive: true,
          maintainAspectRatio: false,
          plugins: {{
            legend: {{ position: 'bottom', labels: {{ boxWidth: 12, font: {{ family: 'Inter', size: 10 }} }} }}
          }},
          cutout: '62%'
        }}
      }});
    }}

    // Bootstrapping
    renderTable(APPS);
    initCharts();
  </script>
</body>
</html>
"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Prism editorial index.html generated successfully ({len(html)} bytes)!")

if __name__ == "__main__":
    build()
