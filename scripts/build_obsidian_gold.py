"""
Compiles index.html into a minimal, museum-grade Swiss-editorial case study.
Strict Color System:
- Primary Canvas: Matte Obsidian #09090B
- Elevated Cards: Deep Charcoal #111113 with 1px solid #222225 borders
- Crisp White: #FFFFFF for headlines and primary text; #A1A1A6 secondary; #6E6E73 metadata
- Brushed Champagne Gold (~10% MAX): #C9A86A / #9E7F47
- Anti-AI: 0 emojis, 0 glowing borders/purple gradients, Instrument Serif + Inter + JetBrains Mono
- Embedded live JSON agent layer with copy toast
"""

import os
import json

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
FINAL_JSON = os.path.join(ROOT_DIR, "data", "final_verified.json")
PATTERNS_JSON = os.path.join(ROOT_DIR, "data", "patterns_summary.json")
LOG_JSON = os.path.join(ROOT_DIR, "data", "verification_log.json")
SLUGS_JSON = os.path.join(ROOT_DIR, "data", "verified_slugs.json")
OUTPUT_HTML = os.path.join(ROOT_DIR, "index.html")

def get_monogram(name: str) -> str:
    cleaned = "".join(c for c in name if c.isalnum() or c.isspace()).strip()
    words = cleaned.split()
    if len(words) >= 2:
        return (words[0][0] + words[1][0]).upper()
    elif len(cleaned) >= 2:
        return cleaned[:2].upper()
    return cleaned.upper() if cleaned else "AP"

def build():
    with open(FINAL_JSON, "r", encoding="utf-8") as f:
        apps = json.load(f)

    with open(PATTERNS_JSON, "r", encoding="utf-8") as f:
        patterns = json.load(f)

    with open(LOG_JSON, "r", encoding="utf-8") as f:
        log_data = json.load(f)

    with open(SLUGS_JSON, "r", encoding="utf-8") as f:
        verified_slugs = json.load(f)

    for a in apps:
        a["slug"] = verified_slugs.get(a["name"], "")
        a["monogram"] = get_monogram(a["name"])

    # Macro numbers
    tier_counts = patterns["macro_metrics"]["buildability_tiers"]
    t1_count = tier_counts.get("Tier 1: Ship Now", 61)
    t2_count = tier_counts.get("Tier 2: Wrap MCP / CLI", 20)
    t3_count = tier_counts.get("Tier 3: Ops / Review Queue", 10)
    t4_count = tier_counts.get("Tier 4: BD / Sales Wall", 9)
    buildable_count = t1_count + t2_count

    comp_meta = patterns.get("composio_catalog_comparison", {})
    already_comp_count = comp_meta.get("already_in_composio_count", 76)
    net_new_count = comp_meta.get("net_new_apps_count", 24)
    net_new_qw_count = comp_meta.get("net_new_quick_wins_count", 15)

    acc = patterns.get("accuracy_progression", {})
    p1_acc = acc.get("pass1_accuracy", "69.2%")
    p2_acc = acc.get("pass2_accuracy", "96.2%")
    final_acc = acc.get("final_verified_accuracy", "100.0%")

    bundle = {
        "metadata": {
            "title": "Composio 100-App Agent Toolkit Buildability Study",
            "version": "3.0.0",
            "date": "2026-11-24",
            "total_apps": len(apps),
            "buildable_today_count": buildable_count,
            "already_in_composio_count": already_comp_count,
            "net_new_opportunities_count": net_new_count,
            "net_new_quick_wins_count": net_new_qw_count
        },
        "patterns": patterns,
        "apps": apps
    }
    bundle_json_str = json.dumps(bundle, indent=2)
    apps_json_str = json.dumps(apps)
    patterns_json_str = json.dumps(patterns)

    # Compute Sankey data
    categories = sorted(list({a["category"] for a in apps}))
    auths = sorted(list({a["primary_auth"] for a in apps}))
    tiers = ["Tier 1: Ship Now", "Tier 2: Wrap MCP / CLI", "Tier 3: Ops / Review Queue", "Tier 4: BD / Sales Wall"]

    sankey_nodes = []
    for c in categories:
        sankey_nodes.append({"name": c, "itemStyle": {"color": "#3F3F46"}})
    for au in auths:
        sankey_nodes.append({"name": au, "itemStyle": {"color": "#52525B"}})
    
    tier_colors = {
        "Tier 1: Ship Now": "#C9A86A",       # Champagne gold accent
        "Tier 2: Wrap MCP / CLI": "#E4E4E7", # Crisp silver
        "Tier 3: Ops / Review Queue": "#A1A1A6", # Slate
        "Tier 4: BD / Sales Wall": "#52525B"  # Zinc
    }
    for t in tiers:
        sankey_nodes.append({"name": t, "itemStyle": {"color": tier_colors.get(t, "#52525B")}})

    cat_auth_counts = {}
    auth_tier_counts = {}
    for a in apps:
        c = a["category"]
        au = a["primary_auth"]
        t = a["buildability_tier"]
        k1 = (c, au)
        cat_auth_counts[k1] = cat_auth_counts.get(k1, 0) + 1
        k2 = (au, t)
        auth_tier_counts[k2] = auth_tier_counts.get(k2, 0) + 1

    sankey_links = []
    for (src, tgt), count in sorted(cat_auth_counts.items()):
        sankey_links.append({"source": src, "target": tgt, "value": count, "lineStyle": {"color": "#3F3F46", "opacity": 0.25}})
    for (src, tgt), count in sorted(auth_tier_counts.items()):
        # Gold highlight for Tier 1 paths
        is_gold = (tgt == "Tier 1: Ship Now")
        link_color = "#C9A86A" if is_gold else "#52525B"
        opacity = 0.45 if is_gold else 0.25
        sankey_links.append({"source": src, "target": tgt, "value": count, "lineStyle": {"color": link_color, "opacity": opacity}})

    sankey_data_js = json.dumps({"nodes": sankey_nodes, "links": sankey_links})

    # Category x Access Model Bar Chart Data
    cat_access_matrix = patterns.get("category_access_matrix", {})
    all_access_models = [
        "Self-Serve Free",
        "Self-Serve Paid/Trial",
        "Sandbox Self-Serve / Prod Gated",
        "Enterprise / Sales Gated",
        "Open-Source / Local"
    ]
    bar_categories = list(cat_access_matrix.keys())
    bar_series = []
    model_colors = {
        "Self-Serve Free": "#FFFFFF",               # Pure crisp white
        "Self-Serve Paid/Trial": "#A1A1A6",         # Silver
        "Sandbox Self-Serve / Prod Gated": "#C9A86A", # Champagne gold (highlights trap!)
        "Enterprise / Sales Gated": "#52525B",      # Zinc
        "Open-Source / Local": "#3F3F46"            # Dark charcoal
    }
    for model in all_access_models:
        data = [cat_access_matrix.get(cat, {}).get(model, 0) for cat in bar_categories]
        bar_series.append({
            "name": model,
            "type": "bar",
            "stack": "total",
            "emphasis": {"focus": "series"},
            "itemStyle": {"color": model_colors.get(model, "#52525B")},
            "data": data
        })

    bar_data_js = json.dumps({
        "categories": bar_categories,
        "models": all_access_models,
        "series": bar_series
    })

    html = f"""<!DOCTYPE html>
<html lang="en" class="bg-[#09090B] text-[#FFFFFF] overflow-x-hidden">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0">
  <title>100-App Agent Toolkit Feasibility Study | Composio Product Ops</title>
  
  <!-- Editorial Typography: Instrument Serif + Inter + JetBrains Mono -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  
  <!-- Libraries (CDNs) -->
  <link rel="stylesheet" href="https://unpkg.com/lenis@1.1.18/dist/lenis.css">
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/lucide@latest"></script>
  <script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
  <script src="https://unpkg.com/roughjs@latest/bundled/rough.js"></script>
  <script src="https://unpkg.com/lenis@1.1.18/dist/lenis.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
  
  <style>
    :root {{
      --obsidian: #09090B;
      --surface: #111113;
      --surface-elevated: #161619;
      --hairline: #222225;
      --hairline-subtle: #1E1E22;
      --text-white: #FFFFFF;
      --text-muted: #A1A1A6;
      --text-dim: #6E6E73;
      --gold: #C9A86A;
      --gold-muted: #9E7F47;
    }}
    
    *, *::before, *::after {{
      box-sizing: border-box;
      min-width: 0;
    }}

    html, body {{
      width: 100%;
      max-width: 100vw;
      overflow-x: hidden;
      margin: 0;
      padding: 0;
    }}

    /* Lenis Smooth Scroll Core */
    html.lenis, html.lenis body {{
      height: auto;
    }}
    .lenis.lenis-smooth {{
      scroll-behavior: auto !important;
    }}
    .lenis.lenis-smooth [data-lenis-prevent] {{
      overscroll-behavior: contain;
    }}
    .lenis.lenis-stopped {{
      overflow: hidden;
    }}
    .lenis.lenis-smooth iframe {{
      pointer-events: none;
    }}

    canvas {{
      max-width: 100% !important;
    }}

    #echarts-sankey, #echarts-stacked-bar,
    #echarts-sankey > div, #echarts-stacked-bar > div {{
      max-width: 100% !important;
      width: 100% !important;
    }}

    input, select, textarea {{
      min-width: 0 !important;
      max-width: 100% !important;
    }}

    main, section, header, footer {{
      width: 100%;
      max-width: 100%;
      overflow-x: hidden;
    }}
    .allow-scroll-x {{
      overflow-x: auto !important;
      max-width: 100% !important;
      -webkit-overflow-scrolling: touch;
    }}

    body {{
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background-color: var(--obsidian);
      color: var(--text-white);
      -webkit-font-smoothing: antialiased;
    }}
    
    .font-serif {{
      font-family: 'Instrument Serif', Georgia, serif;
    }}
    .font-mono {{
      font-family: 'JetBrains Mono', monospace;
      font-variant-numeric: tabular-nums;
    }}
    
    /* Clean hairline card */
    .obsidian-card {{
      background-color: var(--surface);
      border: 1px solid var(--hairline);
    }}

    /* Ultra-muted semantic tier badges */
    .pill-t1 {{
      background-color: #1C1C1F;
      color: #FFFFFF;
      border: 1px solid #27272A;
    }}
    .pill-t2 {{
      background-color: #18181B;
      color: #E4E4E7;
      border: 1px solid #27272A;
    }}
    .pill-t3 {{
      background-color: #18181B;
      color: #D4D4D8;
      border: 1px solid #8E8E93;
    }}
    .pill-t4 {{
      background-color: #121214;
      color: #71717A;
      border: 1px solid #27272A;
    }}

    .pill-comp {{
      background-color: #18181B;
      color: #A1A1A6;
      border: 1px solid #27272A;
    }}
    .pill-netnew {{
      background-color: #1C1A14;
      color: #C9A86A;
      border: 1px solid #3F3622;
    }}

    /* Detail drawer */
    .detail-drawer {{
      transition: max-height 0.3s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.25s ease;
      max-height: 0;
      overflow: hidden;
      opacity: 0;
    }}
    .detail-drawer.open {{
      max-height: 800px;
      opacity: 1;
    }}

    /* Sticky table header */
    thead th {{
      position: sticky;
      top: 0;
      z-index: 10;
      background-color: #111113;
    }}

    /* Custom scrollbar */
    ::-webkit-scrollbar {{
      width: 6px;
      height: 6px;
    }}
    ::-webkit-scrollbar-track {{
      background: #09090B;
    }}
    ::-webkit-scrollbar-thumb {{
      background: #27272A;
      border-radius: 3px;
    }}
    ::-webkit-scrollbar-thumb:hover {{
      background: #3F3F46;
    }}
  </style>
</head>
<body class="min-h-screen text-[#FFFFFF] antialiased selection:bg-[#C9A86A] selection:text-[#09090B] overflow-x-hidden w-full max-w-full">

  <!-- Top 2px Brushed Gold Editorial Hairline -->
  <div class="h-[2px] bg-[#C9A86A] w-full"></div>

  <!-- Minimal Sticky Top Bar -->
  <header class="border-b border-[#1E1E22] bg-[#09090B]/95 backdrop-blur-none sticky top-0 z-40 w-full overflow-hidden">
    <div class="max-w-[1240px] mx-auto px-3 sm:px-6 h-14 flex items-center justify-between gap-2 overflow-hidden">
      <div class="flex items-center space-x-2 sm:space-x-3 min-w-0">
        <span class="text-xs font-mono tracking-widest text-[#FFFFFF] font-semibold truncate">
          COMPOSIO <span class="hidden md:inline">// 100-APP TOOLKIT AUDIT</span>
        </span>
        <div class="hidden md:block h-3 w-px bg-[#222225]"></div>
        <span class="hidden md:inline-block text-[11px] font-mono text-[#6E6E73] tracking-wide">
          PRODUCT OPS RESEARCH
        </span>
      </div>

      <nav class="hidden lg:flex items-center space-x-6 text-xs font-mono text-[#A1A1A6]">
        <a href="#patterns" class="hover:text-[#FFFFFF] transition-colors">Patterns</a>
        <a href="#matrix" class="hover:text-[#FFFFFF] transition-colors">100-App Matrix</a>
        <a href="#architecture" class="hover:text-[#FFFFFF] transition-colors">Agent & Proof</a>
        <a href="#verification" class="hover:text-[#FFFFFF] transition-colors">Verification</a>
      </nav>

      <div class="flex items-center space-x-2 sm:space-x-3 text-xs font-mono flex-shrink-0">
        <button id="copy-json-btn" onclick="copyStructuredJSON()" class="inline-flex items-center space-x-1.5 px-2.5 sm:px-3 py-1.5 rounded-sm bg-[#FFFFFF] text-[#09090B] font-medium hover:bg-[#E4E4E7] transition-colors text-[11px] sm:text-xs">
          <i data-lucide="copy" class="w-3.5 h-3.5 stroke-[1.5]"></i>
          <span>Copy JSON</span>
          <span class="hidden md:inline">(Agent View)</span>
        </button>
        <a href="data.json" download="composio_100_apps_verified.json" class="hidden md:inline-flex items-center space-x-1 px-2.5 py-1.5 rounded-sm border border-[#222225] bg-[#111113] text-[#A1A1A6] hover:text-[#FFFFFF] hover:border-[#3F3F46] transition-colors">
          <i data-lucide="download" class="w-3.5 h-3.5 stroke-[1.5]"></i>
          <span>data.json</span>
        </a>
        <a href="llms.txt" class="hidden md:inline-flex items-center space-x-1 px-2.5 py-1.5 rounded-sm border border-[#222225] bg-[#111113] text-[#A1A1A6] hover:text-[#FFFFFF] hover:border-[#3F3F46] transition-colors">
          <i data-lucide="file-text" class="w-3.5 h-3.5 stroke-[1.5]"></i>
          <span>/llms.txt</span>
        </a>
        <a id="github-repo-link" href="https://github.com/prajwal1-1/AI-Product-Ops" target="_blank" rel="noopener noreferrer" class="hidden md:inline-flex items-center space-x-1.5 px-2.5 py-1.5 rounded-sm border border-[#222225] bg-[#111113] text-[#A1A1A6] hover:text-[#FFFFFF] hover:border-[#3F3F46] transition-colors" title="View GitHub Repository">
          <i data-lucide="github" class="w-3.5 h-3.5 stroke-[1.5]"></i>
          <span>GitHub</span>
        </a>
      </div>
    </div>
  </header>

  <!-- Content Container -->
  <main class="max-w-[1240px] mx-auto px-3 sm:px-6 py-8 sm:py-12 space-y-12 sm:space-y-20 w-full min-w-0 overflow-hidden">

    <!-- HERO & SECTION 1: EXECUTIVE HEADLINE & 4 KPI BLOCKS -->
    <section class="space-y-8 pt-2">
      <div class="space-y-3">
        <div class="inline-flex items-center space-x-2 text-[11px] font-mono tracking-wider text-[#C9A86A] uppercase font-semibold">
          <span class="w-1.5 h-1.5 rounded-full bg-[#C9A86A]"></span>
          <span>Verified Feasibility Study & Buildability Triage</span>
        </div>
        <h1 class="text-3xl sm:text-5xl lg:text-6xl font-serif tracking-tight text-[#FFFFFF] leading-[1.05]">
          100-App Agent Toolkit Feasibility Study
        </h1>
        <p class="text-sm sm:text-base lg:text-lg text-[#A1A1A6] max-w-4xl font-normal leading-relaxed">
          An automated research audit and 3-check verification loop across 100 enterprise integrations. 
          Triaged into immediate buildability tiers, exposing developer traps, gated production APIs, and 
          unlocked MCP/CLI integration surfaces for Composio agent engineers.
        </p>
      </div>

      <!-- 4 Minimal KPI Stat Blocks Separated by 1px Hairlines (1-col on mobile, 2-col on tablet, 4-col on desktop) -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-0 border border-[#222225] rounded-sm bg-[#111113] divide-y md:divide-y-0 divide-[#222225] w-full min-w-0">
        <!-- Tier 1 -->
        <div onclick="filterByTier('Tier 1: Ship Now')" class="p-4 sm:p-6 cursor-pointer hover:bg-[#161619] transition-colors group md:border-r md:border-b lg:border-b-0 border-[#222225]">
          <div class="flex items-center justify-between">
            <span class="text-xs font-mono uppercase tracking-wider text-[#A1A1A6] flex items-center">
              <span class="w-1.5 h-1.5 rounded-full bg-[#C9A86A] mr-1.5"></span>
              Tier 1: Ship Now
            </span>
            <i data-lucide="arrow-down-right" class="w-3.5 h-3.5 stroke-[1.5] text-[#6E6E73] group-hover:text-[#FFFFFF] transition-colors"></i>
          </div>
          <div class="mt-4 flex items-baseline space-x-2">
            <span id="kpi-t1" class="text-3xl sm:text-5xl font-serif text-[#FFFFFF] kpi-num" data-target="{t1_count}">{t1_count}</span>
            <span class="text-xs font-mono text-[#6E6E73]">({t1_count}.0%)</span>
          </div>
          <p class="mt-2 text-xs text-[#A1A1A6] leading-relaxed">
            Public docs, self-serve credentials, open REST/GraphQL. Zero human gating.
          </p>
        </div>

        <!-- Tier 2 -->
        <div onclick="filterByTier('Tier 2: Wrap MCP / CLI')" class="p-4 sm:p-6 cursor-pointer hover:bg-[#161619] transition-colors group lg:border-r md:border-b lg:border-b-0 border-[#222225]">
          <div class="flex items-center justify-between">
            <span class="text-xs font-mono uppercase tracking-wider text-[#A1A1A6] flex items-center">
              <span class="w-1.5 h-1.5 rounded-full bg-[#FFFFFF] mr-1.5"></span>
              Tier 2: Wrap MCP / CLI
            </span>
            <i data-lucide="arrow-down-right" class="w-3.5 h-3.5 stroke-[1.5] text-[#6E6E73] group-hover:text-[#FFFFFF] transition-colors"></i>
          </div>
          <div class="mt-4 flex items-baseline space-x-2">
            <span id="kpi-t2" class="text-3xl sm:text-5xl font-serif text-[#FFFFFF] kpi-num" data-target="{t2_count}">{t2_count}</span>
            <span class="text-xs font-mono text-[#6E6E73]">({t2_count}.0%)</span>
          </div>
          <p class="mt-2 text-xs text-[#A1A1A6] leading-relaxed">
            Existing official/community MCP server or CLI wrapper available today.
          </p>
        </div>

        <!-- Tier 3 -->
        <div onclick="filterByTier('Tier 3: Ops / Review Queue')" class="p-4 sm:p-6 cursor-pointer hover:bg-[#161619] transition-colors group md:border-r border-[#222225]">
          <div class="flex items-center justify-between">
            <span class="text-xs font-mono uppercase tracking-wider text-[#A1A1A6] flex items-center">
              <span class="w-1.5 h-1.5 rounded-full border border-[#8E8E93] mr-1.5"></span>
              Tier 3: Ops Queue
            </span>
            <i data-lucide="arrow-down-right" class="w-3.5 h-3.5 stroke-[1.5] text-[#6E6E73] group-hover:text-[#FFFFFF] transition-colors"></i>
          </div>
          <div class="mt-4 flex items-baseline space-x-2">
            <span id="kpi-t3" class="text-3xl sm:text-5xl font-serif text-[#FFFFFF] kpi-num" data-target="{t3_count}">{t3_count}</span>
            <span class="text-xs font-mono text-[#6E6E73]">({t3_count}.0%)</span>
          </div>
          <p class="mt-2 text-xs text-[#A1A1A6] leading-relaxed">
            Sandbox self-serve, but production requires App Review, compliance, or phone checks.
          </p>
        </div>

        <!-- Tier 4 -->
        <div onclick="filterByTier('Tier 4: BD / Sales Wall')" class="p-4 sm:p-6 cursor-pointer hover:bg-[#161619] transition-colors group">
          <div class="flex items-center justify-between">
            <span class="text-xs font-mono uppercase tracking-wider text-[#71717A] flex items-center">
              <span class="w-1.5 h-1.5 rounded-full bg-[#27272A] mr-1.5"></span>
              Tier 4: Sales Wall
            </span>
            <i data-lucide="arrow-down-right" class="w-3.5 h-3.5 stroke-[1.5] text-[#6E6E73] group-hover:text-[#FFFFFF] transition-colors"></i>
          </div>
          <div class="mt-4 flex items-baseline space-x-2">
            <span id="kpi-t4" class="text-3xl sm:text-5xl font-serif text-[#FFFFFF] kpi-num" data-target="{t4_count}">{t4_count}</span>
            <span class="text-xs font-mono text-[#6E6E73]">({t4_count}.0%)</span>
          </div>
          <p class="mt-2 text-xs text-[#71717A] leading-relaxed">
            Gated behind enterprise sales, NDAs, bespoke licenses, or closed ecosystems.
          </p>
        </div>
      </div>
    </section>

    <!-- 5 EDITORIAL PATTERN TAKEAWAYS & ECHARTS -->
    <section id="patterns" class="space-y-8 pt-4">
      <div class="border-t border-[#1E1E22] pt-8">
        <h2 class="text-xs font-mono uppercase tracking-widest text-[#6E6E73] font-semibold mb-2">
          Macro Patterns & Analysis
        </h2>
        <h3 class="text-2xl sm:text-3xl font-serif tracking-tight text-[#FFFFFF]">
          Architectural Insights Across 100 Platforms
        </h3>
      </div>

      <!-- 5 Editorial Takeaways List -->
      <div class="grid grid-cols-1 md:grid-cols-5 gap-3 text-xs font-sans">
        <div class="obsidian-card p-4 rounded-sm space-y-1.5">
          <span class="font-mono text-[#C9A86A] text-xs font-semibold">01 // DOMINANT AUTH</span>
          <p class="text-[#A1A1A6] leading-relaxed">
            <strong class="text-[#FFFFFF]">API Key & Bearer Token (63%)</strong> dominate developer toolkits. OAuth2 (28%) is mandatory in CRM, Email, and Google/Meta suites.
          </p>
        </div>

        <div class="obsidian-card p-4 rounded-sm space-y-1.5">
          <span class="font-mono text-[#C9A86A] text-xs font-semibold">02 // THE GATED TRAP</span>
          <p class="text-[#A1A1A6] leading-relaxed">
            <strong class="text-[#FFFFFF]">9 apps appear self-serve</strong> (Google Ads, Meta Ads, Amazon SP-API, WhatsApp) but block production agent execution behind compliance reviews.
          </p>
        </div>

        <div class="obsidian-card p-4 rounded-sm space-y-1.5">
          <span class="font-mono text-[#C9A86A] text-xs font-semibold">03 // COMPOSIO COVERAGE</span>
          <p class="text-[#A1A1A6] leading-relaxed">
            <strong class="text-[#FFFFFF]">{already_comp_count}% ({already_comp_count}/100)</strong> are already in Composio. <strong class="text-[#FFFFFF]">{net_new_count} platforms</strong> are net-new, including <strong class="text-[#C9A86A]">{net_new_qw_count} Tier 1/2 Quick Wins</strong>.
          </p>
        </div>

        <div class="obsidian-card p-4 rounded-sm space-y-1.5">
          <span class="font-mono text-[#C9A86A] text-xs font-semibold">04 // 81% BUILDABLE TODAY</span>
          <p class="text-[#A1A1A6] leading-relaxed">
            <strong class="text-[#FFFFFF]">{buildable_count} platforms (Tiers 1 & 2)</strong> can be wired and deployed immediately with zero commercial dependencies or developer account delays.
          </p>
        </div>

        <div class="obsidian-card p-4 rounded-sm space-y-1.5">
          <span class="font-mono text-[#C9A86A] text-xs font-semibold">05 // HARD BD WALLS</span>
          <p class="text-[#A1A1A6] leading-relaxed">
            <strong class="text-[#FFFFFF]">{t4_count} platforms (Tier 4)</strong> (DealCloud, PitchBook, Gladly, Paygent) require enterprise sales contracts, NDAs, or partner agreements.
          </p>
        </div>
      </div>

      <!-- ECharts: Sankey + Stacked Bar in Dark Obsidian Cards -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 min-w-0 w-full">
        
        <!-- SANKEY DIAGRAM -->
        <div class="obsidian-card p-4 sm:p-5 rounded-sm flex flex-col min-w-0 overflow-hidden w-full">
          <div class="flex items-center justify-between pb-3 border-b border-[#222225] gap-2">
            <div class="min-w-0">
              <h4 class="text-xs font-mono font-semibold uppercase tracking-wider text-[#FFFFFF] truncate">
                Category → Auth Method → Tier
              </h4>
              <p class="text-[11px] text-[#A1A1A6] mt-0.5 truncate">Interactive flow across 100 apps. Click node to filter.</p>
            </div>
            <span class="text-[10px] font-mono px-2 py-0.5 rounded-sm bg-[#161619] text-[#A1A1A6] border border-[#222225] flex-shrink-0">
              Sankey
            </span>
          </div>
          <div id="echarts-sankey" class="w-full h-[360px] sm:h-[440px] mt-2 min-w-0"></div>
        </div>

        <!-- STACKED BAR: Category x Access Model -->
        <div class="obsidian-card p-4 sm:p-5 rounded-sm flex flex-col min-w-0 overflow-hidden w-full">
          <div class="flex items-center justify-between pb-3 border-b border-[#222225] gap-2">
            <div class="min-w-0">
              <h4 class="text-xs font-mono font-semibold uppercase tracking-wider text-[#FFFFFF] truncate">
                Category × Access Model
              </h4>
              <p class="text-[11px] text-[#A1A1A6] mt-0.5 truncate">Gold bar highlights the "Sandbox Free / Prod Gated" trap.</p>
            </div>
            <span class="text-[10px] font-mono px-2 py-0.5 rounded-sm bg-[#161619] text-[#A1A1A6] border border-[#222225] flex-shrink-0">
              Stacked Bar
            </span>
          </div>
          <div id="echarts-stacked-bar" class="w-full h-[360px] sm:h-[440px] mt-2 min-w-0"></div>
        </div>

      </div>
    </section>

    <!-- SECTION 2: INTERACTIVE 100-APP RESEARCH MATRIX -->
    <section id="matrix" class="space-y-6 pt-4 w-full min-w-0">
      <div class="border-t border-[#1E1E22] pt-8 flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <h2 class="text-xs font-mono uppercase tracking-widest text-[#6E6E73] font-semibold mb-2">
            Dataset & Triage Surface
          </h2>
          <h3 class="text-2xl sm:text-3xl font-serif tracking-tight text-[#FFFFFF]">
            100-App Verified Research Matrix
          </h3>
          <p class="text-xs text-[#A1A1A6] mt-1 font-mono">
            Showing <span id="filtered-count" class="font-bold text-[#FFFFFF]">100</span> of 100 apps. Click any row to expand evidence, auth details, and verification notes.
          </p>
        </div>

        <button onclick="resetFilters()" class="text-xs font-mono text-[#A1A1A6] hover:text-[#FFFFFF] underline flex items-center self-start sm:self-auto">
          <i data-lucide="refresh-cw" class="w-3 h-3 stroke-[1.5] mr-1"></i> Reset all filters
        </button>
      </div>

      <!-- Search & Filters Toolbar -->
      <div class="obsidian-card p-3 sm:p-4 rounded-sm space-y-3 w-full min-w-0">
        <!-- Search Input -->
        <div class="relative w-full">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-[#6E6E73]">
            <i data-lucide="search" class="w-4 h-4 stroke-[1.5]"></i>
          </div>
          <input type="text" id="search-input" oninput="applyFilters()" placeholder="Search apps, categories, blockers (e.g. Stripe, Ads, OAuth2)..."
                 class="w-full pl-9 pr-4 py-2 border border-[#222225] rounded-sm text-xs font-mono bg-[#09090B] text-[#FFFFFF] placeholder-[#6E6E73] focus:bg-[#111113] focus:outline-none focus:border-[#C9A86A] transition-colors" />
        </div>

        <!-- Filter Selects Grid: 1 col on mobile, 2 col on sm, 3 col on md, 6 col on xl -->
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-2 text-xs font-mono w-full min-w-0">
          <!-- Composio Status Filter -->
          <div>
            <label class="block text-[10px] uppercase text-[#6E6E73] mb-1">Composio Status</label>
            <select id="filter-composio" onchange="applyFilters()" class="w-full p-1.5 border border-[#222225] rounded-sm bg-[#09090B] text-[#FFFFFF] focus:outline-none focus:border-[#C9A86A]">
              <option value="">All Statuses (100)</option>
              <option value="in_composio">In Composio ({already_comp_count})</option>
              <option value="net_new">Net-New ({net_new_count})</option>
              <option value="net_new_quick_wins">Net-New Quick Wins ({net_new_qw_count})</option>
            </select>
          </div>

          <!-- Category Filter -->
          <div>
            <label class="block text-[10px] uppercase text-[#6E6E73] mb-1">Category</label>
            <select id="filter-category" onchange="applyFilters()" class="w-full p-1.5 border border-[#222225] rounded-sm bg-[#09090B] text-[#FFFFFF] focus:outline-none focus:border-[#C9A86A]">
              <option value="">All Categories (10)</option>
              {"".join(f'<option value="{c}">{c}</option>' for c in categories)}
            </select>
          </div>

          <!-- Tier Filter -->
          <div>
            <label class="block text-[10px] uppercase text-[#6E6E73] mb-1">Buildability Tier</label>
            <select id="filter-tier" onchange="applyFilters()" class="w-full p-1.5 border border-[#222225] rounded-sm bg-[#09090B] text-[#FFFFFF] focus:outline-none focus:border-[#C9A86A]">
              <option value="">All Tiers (4)</option>
              <option value="Tier 1: Ship Now">Tier 1: Ship Now ({t1_count})</option>
              <option value="Tier 2: Wrap MCP / CLI">Tier 2: Wrap MCP / CLI ({t2_count})</option>
              <option value="Tier 3: Ops / Review Queue">Tier 3: Ops Queue ({t3_count})</option>
              <option value="Tier 4: BD / Sales Wall">Tier 4: Sales Wall ({t4_count})</option>
            </select>
          </div>

          <!-- Auth Filter -->
          <div>
            <label class="block text-[10px] uppercase text-[#6E6E73] mb-1">Auth Method</label>
            <select id="filter-auth" onchange="applyFilters()" class="w-full p-1.5 border border-[#222225] rounded-sm bg-[#09090B] text-[#FFFFFF] focus:outline-none focus:border-[#C9A86A]">
              <option value="">All Auth Methods</option>
              <option value="API Key">API Key</option>
              <option value="OAuth2">OAuth2</option>
              <option value="Bearer Token">Bearer Token</option>
              <option value="Basic Auth">Basic Auth</option>
              <option value="CLI/Local (No Auth)">CLI/Local</option>
              <option value="GCP/IAM">GCP/IAM</option>
            </select>
          </div>

          <!-- Access Model Filter -->
          <div>
            <label class="block text-[10px] uppercase text-[#6E6E73] mb-1">Access Model</label>
            <select id="filter-access" onchange="applyFilters()" class="w-full p-1.5 border border-[#222225] rounded-sm bg-[#09090B] text-[#FFFFFF] focus:outline-none focus:border-[#C9A86A]">
              <option value="">All Access Models</option>
              <option value="Self-Serve Free">Self-Serve Free</option>
              <option value="Self-Serve Paid/Trial">Self-Serve Paid/Trial</option>
              <option value="Sandbox Self-Serve / Prod Gated">Sandbox Free / Prod Gated</option>
              <option value="Enterprise / Sales Gated">Enterprise / Sales Gated</option>
              <option value="Open-Source / Local">Open-Source / Local</option>
            </select>
          </div>

          <!-- MCP Status Filter -->
          <div>
            <label class="block text-[10px] uppercase text-[#6E6E73] mb-1">MCP Ecosystem</label>
            <select id="filter-mcp" onchange="applyFilters()" class="w-full p-1.5 border border-[#222225] rounded-sm bg-[#09090B] text-[#FFFFFF] focus:outline-none focus:border-[#C9A86A]">
              <option value="">All MCP Statuses</option>
              <option value="Official MCP">Official MCP</option>
              <option value="Community MCP">Community MCP</option>
              <option value="None">None</option>
            </select>
          </div>
        </div>
      </div>

      <!-- Dense Table Container -->
      <div class="obsidian-card rounded-sm overflow-hidden w-full min-w-0">
        <div class="allow-scroll-x max-h-[660px] w-full">
          <table class="w-full min-w-[720px] text-left text-xs border-collapse">
            <thead>
              <tr class="border-b border-[#222225] text-[11px] font-mono uppercase tracking-wider text-[#6E6E73]">
                <th class="py-3 px-3 w-10 text-center font-normal">#</th>
                <th class="py-3 px-3 font-normal">Platform</th>
                <th class="py-3 px-3 font-normal">Category</th>
                <th class="py-3 px-3 font-normal">Composio</th>
                <th class="py-3 px-3 font-normal">Primary Auth</th>
                <th class="py-3 px-3 font-normal">Access Model</th>
                <th class="py-3 px-3 font-normal">Surface & MCP</th>
                <th class="py-3 px-3 font-normal">Tier</th>
                <th class="py-3 px-3 font-normal text-right">Verification</th>
              </tr>
            </thead>
            <tbody id="app-table-body" class="divide-y divide-[#1E1E22] font-mono text-[12px]">
              <!-- Dynamically populated via JS -->
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- SECTION 3: ARCHITECTURE & RUNNABLE CLI PROOF -->
    <section id="architecture" class="space-y-6 pt-4 w-full min-w-0">
      <div class="border-t border-[#1E1E22] pt-8">
        <h2 class="text-xs font-mono uppercase tracking-widest text-[#6E6E73] font-semibold mb-2">
          Methodology & Loop Pipeline
        </h2>
        <h3 class="text-2xl sm:text-3xl font-serif tracking-tight text-[#FFFFFF]">
          The Research Agent & Human-in-the-Loop Architecture
        </h3>
        <p class="text-xs text-[#A1A1A6] max-w-3xl mt-1">
          A multi-tiered verification pipeline designed to prevent agent hallucinations, catch developer portal redirects, 
          and cleanly surface gated enterprise sales requirements.
        </p>
      </div>

      <!-- Rough.js Hand-Drawn Architecture Schematic -->
      <div class="obsidian-card p-4 sm:p-6 rounded-sm overflow-hidden w-full min-w-0">
        <div class="flex items-center justify-between mb-4 pb-2 border-b border-[#222225] gap-2">
          <span class="text-xs font-mono uppercase font-semibold text-[#FFFFFF] flex items-center space-x-1.5 truncate">
            <i data-lucide="git-branch" class="w-3.5 h-3.5 stroke-[1.5] flex-shrink-0"></i>
            <span class="truncate">Autonomous Pipeline Topology</span>
          </span>
          <span class="text-[11px] font-mono text-[#6E6E73] flex-shrink-0">Rough.js Engine</span>
        </div>
        <div class="allow-scroll-x w-full">
          <svg id="pipeline-svg" class="w-full min-w-[780px] h-[220px]" viewBox="0 0 1000 240"></svg>
        </div>
      </div>

      <!-- 2-Column: Agent vs Human -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 w-full min-w-0">
        <div class="obsidian-card p-4 sm:p-5 rounded-sm space-y-3 min-w-0">
          <div class="flex items-center space-x-2 text-xs font-mono uppercase font-semibold text-[#FFFFFF]">
            <i data-lucide="cpu" class="w-4 h-4 stroke-[1.5] text-[#C9A86A]"></i>
            <span>What the Agent Handled Autonomously</span>
          </div>
          <ul class="text-xs text-[#A1A1A6] space-y-2 list-disc list-inside leading-relaxed font-sans">
            <li><strong class="text-[#FFFFFF]">Broad-Spectrum Extraction:</strong> Parsed 100 integration docs, SDK references, and community repos in parallel via Composio SDK & Gemini Flash.</li>
            <li><strong class="text-[#FFFFFF]">Automated Liveness Testing:</strong> Tested HTTP status codes across all 100 documentation URLs. Automatically remediated 14 broken or redirected links using Firecrawl scraping.</li>
            <li><strong class="text-[#FFFFFF]">MCP Ecosystem Discovery:</strong> Cross-referenced GitHub and official registries, identifying 18 official MCP servers and 39 community MCP wrappers.</li>
            <li><strong class="text-[#FFFFFF]">Strict Schema Validation:</strong> Enforced normalized auth types, buildability tiers, and access models across all 100 structured outputs.</li>
          </ul>
        </div>

        <div class="obsidian-card p-4 sm:p-5 rounded-sm space-y-3 min-w-0">
          <div class="flex items-center space-x-2 text-xs font-mono uppercase font-semibold text-[#FFFFFF]">
            <i data-lucide="user-check" class="w-4 h-4 stroke-[1.5] text-[#C9A86A]"></i>
            <span>Where a Human Was Required</span>
          </div>
          <ul class="text-xs text-[#A1A1A6] space-y-2 list-disc list-inside leading-relaxed font-sans">
            <li><strong class="text-[#FFFFFF]">The "Fake Self-Serve" Gating Trap:</strong> Identifying that Google Ads and Meta Ads allow instant sandbox signups, but require human App Review and business phone verification before mutating live data.</li>
            <li><strong class="text-[#FFFFFF]">CLI vs Cloud Disambiguation:</strong> Catching that tools like Mermaid CLI have no hosted REST API, but run entirely as local binaries.</li>
            <li><strong class="text-[#FFFFFF]">Enterprise Gate Nuances:</strong> Confirming that platforms like DealCloud, Gladly, and PitchBook lack public developer consoles and require licensed customer admin enablement.</li>
            <li><strong class="text-[#FFFFFF]">Multi-Tenancy Verification:</strong> Resolving whether third-party connectors (e.g. Fanbasis, iPayX) were official developer APIs or wrapper services.</li>
          </ul>
        </div>
      </div>

      <!-- Minimal Matte-Black Terminal Card (#050506, 1px solid #222225) -->
      <div class="rounded-sm bg-[#050506] border border-[#222225] p-4 sm:p-5 space-y-3 w-full min-w-0 overflow-hidden">
        <div class="flex items-center justify-between text-xs font-mono pb-2 border-b border-[#1E1E22]">
          <span class="flex items-center space-x-2 text-[#6E6E73]">
            <i data-lucide="terminal" class="w-3.5 h-3.5 stroke-[1.5] text-[#C9A86A]"></i>
            <span class="text-[#A1A1A6]">Autonomous Reproduction CLI Command</span>
          </span>
          <span class="text-[#C9A86A] font-semibold">1-Command Verification</span>
        </div>
        <div class="font-mono text-xs space-y-2 overflow-x-auto">
          <div class="text-[#FFFFFF] select-all">$ python scripts/01_research_agent.py --app "Stripe"</div>
          <div class="text-[#6E6E73] text-[11px] leading-relaxed">
            [Pass 1] Inspecting Composio registry & developer portal for Stripe...<br>
            [Pass 2] Checking documentation URL https://docs.stripe.com/api -> Status 200 OK<br>
            [Pass 2] Validating auth models: API Key (Restricted) + OAuth2 Connect...<br>
            [Pass 2] MCP check: Official Composio & Community Stripe MCP detected.<br>
            [Result] App: Stripe | Tier: Tier 1: Ship Now | Auth: API Key | Access: Self-Serve Free | Confidence: 0.98
          </div>
        </div>
      </div>
    </section>

    <!-- SECTION 4: VERIFICATION REPORT & HONEST ACCURACY AUDIT -->
    <section id="verification" class="space-y-6 pt-4">
      <div class="border-t border-[#1E1E22] pt-8">
        <h2 class="text-xs font-mono uppercase tracking-widest text-[#6E6E73] font-semibold mb-2">
          Quality Control & Auditing
        </h2>
        <h3 class="text-2xl sm:text-3xl font-serif tracking-tight text-[#FFFFFF]">
          Verification Loop & Honest Accuracy Progression
        </h3>
        <p class="text-xs text-[#A1A1A6] max-w-3xl mt-1">
          Measured across the stratified 26-app human audit sample (covering all flagged apps and high-trap edge cases).
        </p>
      </div>

      <!-- Accuracy Progression Funnel -->
      <div class="obsidian-card p-6 rounded-sm space-y-4">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 text-center">
          <!-- Pass 1 -->
          <div class="p-4 rounded-sm border border-[#222225] bg-[#0E0E10]">
            <div class="text-xs font-mono uppercase text-[#6E6E73]">Pass 1 (Initial Agent Output)</div>
            <div class="text-3xl sm:text-4xl font-serif text-[#FFFFFF] mt-1">{p1_acc}</div>
            <div class="text-[11px] font-mono text-[#6E6E73] mt-0.5">18 / 26 correct</div>
            <div class="w-full bg-[#1E1E22] h-1.5 rounded-sm mt-3 overflow-hidden">
              <div class="acc-bar-1 bg-[#52525B] h-full" style="width: 0%;"></div>
            </div>
            <p class="text-[11px] text-[#A1A1A6] mt-2 text-left font-sans">
              Missed sandbox-vs-prod gating; fell into redirects and dead links on edge platforms.
            </p>
          </div>

          <!-- Pass 2 -->
          <div class="p-4 rounded-sm border border-[#222225] bg-[#0E0E10]">
            <div class="text-xs font-mono uppercase text-[#A1A1A6]">Pass 2 (Verifier Loop + HTTP)</div>
            <div class="text-3xl sm:text-4xl font-serif text-[#FFFFFF] mt-1">{p2_acc}</div>
            <div class="text-[11px] font-mono text-[#A1A1A6] mt-0.5">25 / 26 correct (+27.0%)</div>
            <div class="w-full bg-[#1E1E22] h-1.5 rounded-sm mt-3 overflow-hidden">
              <div class="acc-bar-2 bg-[#E4E4E7] h-full" style="width: 0%;"></div>
            </div>
            <p class="text-[11px] text-[#A1A1A6] mt-2 text-left font-sans">
              HTTP liveness caught 14 dead URLs; Verifier LLM corrected 45 metadata fields.
            </p>
          </div>

          <!-- Final Ground Truth (Highlighted in Gold) -->
          <div class="p-4 rounded-sm border border-[#3F3622] bg-[#14120C]">
            <div class="text-xs font-mono uppercase text-[#C9A86A]">Final Audited Ground Truth</div>
            <div class="text-3xl sm:text-4xl font-serif text-[#C9A86A] mt-1">{final_acc}</div>
            <div class="text-[11px] font-mono text-[#C9A86A] mt-0.5">26 / 26 verified (Human Audited)</div>
            <div class="w-full bg-[#2A2315] h-1.5 rounded-sm mt-3 overflow-hidden">
              <div class="acc-bar-3 bg-[#C9A86A] h-full" style="width: 0%;"></div>
            </div>
            <p class="text-[11px] text-[#A1A1A6] mt-2 text-left font-sans">
              Human review resolved enterprise license prerequisites and local CLI topologies.
            </p>
          </div>
        </div>
      </div>

      <!-- Honest Hits & Misses Table -->
      <div class="obsidian-card rounded-sm overflow-hidden">
        <div class="p-4 border-b border-[#222225] flex items-center justify-between">
          <span class="text-xs font-mono font-semibold uppercase text-[#FFFFFF] flex items-center space-x-1.5">
            <i data-lucide="crosshair" class="w-3.5 h-3.5 stroke-[1.5] text-[#C9A86A]"></i>
            <span>Honest Post-Mortem: Real Errors Caught in the Verification Loop</span>
          </span>
          <span class="text-[11px] font-mono text-[#6E6E73]">6 Critical Case Studies</span>
        </div>
        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs font-mono divide-y divide-[#222225]">
            <thead class="bg-[#161619] text-[11px] uppercase text-[#6E6E73]">
              <tr>
                <th class="py-2.5 px-3">Platform</th>
                <th class="py-2.5 px-3">Pass 1 Error (What Failed)</th>
                <th class="py-2.5 px-3">Pass 2 Catch (Automated Remediation)</th>
                <th class="py-2.5 px-3">Human Audit Resolution</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-[#1E1E22] text-[11px]">
              <tr class="hover:bg-[#161619]/50">
                <td class="py-3 px-3 font-semibold text-[#FFFFFF]">Google Ads</td>
                <td class="py-3 px-3 text-[#A1A1A6]">Classified as Self-Serve Free (Tier 1) based on developer portal.</td>
                <td class="py-3 px-3 text-[#E4E4E7]">Flagged Developer Token gating requirement in docs.</td>
                <td class="py-3 px-3 text-[#C9A86A]">Set to Tier 3 (Ops Queue). Test accounts are free, but live mutating API requires approved Developer Token.</td>
              </tr>
              <tr class="hover:bg-[#161619]/50">
                <td class="py-3 px-3 font-semibold text-[#FFFFFF]">Meta Ads</td>
                <td class="py-3 px-3 text-[#A1A1A6]">Marked as Self-Serve Free with standard access tokens.</td>
                <td class="py-3 px-3 text-[#E4E4E7]">Verifier caught Marketing API App Review prerequisite.</td>
                <td class="py-3 px-3 text-[#C9A86A]">Reclassified to Tier 3. Meta Business Verification required for live campaigns.</td>
              </tr>
              <tr class="hover:bg-[#161619]/50">
                <td class="py-3 px-3 font-semibold text-[#FFFFFF]">Amazon SP-API</td>
                <td class="py-3 px-3 text-[#A1A1A6]">Classified as standard AWS IAM API key.</td>
                <td class="py-3 px-3 text-[#E4E4E7]">Identified Selling Partner Developer Registration requirement.</td>
                <td class="py-3 px-3 text-[#C9A86A]">Tiers updated to Tier 3. Requires registered Professional Selling account & developer profile.</td>
              </tr>
              <tr class="hover:bg-[#161619]/50">
                <td class="py-3 px-3 font-semibold text-[#FFFFFF]">Mermaid CLI</td>
                <td class="py-3 px-3 text-[#A1A1A6]">Guessed REST API with Bearer Token auth.</td>
                <td class="py-3 px-3 text-[#E4E4E7]">Detected 404 on API endpoint; scraped GitHub repo.</td>
                <td class="py-3 px-3 text-[#C9A86A]">Fixed to Tier 2 (CLI/Local No Auth). Runs as a local npm binary (`@mermaid-js/mermaid-cli`).</td>
              </tr>
              <tr class="hover:bg-[#161619]/50">
                <td class="py-3 px-3 font-semibold text-[#FFFFFF]">DealCloud</td>
                <td class="py-3 px-3 text-[#A1A1A6]">Classified as Self-Serve Paid API.</td>
                <td class="py-3 px-3 text-[#E4E4E7]">Flagged 403 on public documentation link.</td>
                <td class="py-3 px-3 text-[#C9A86A]">Reclassified to Tier 4 (BD / Sales Wall). Gated behind enterprise Intapp contract & client admin setup.</td>
              </tr>
              <tr class="hover:bg-[#161619]/50">
                <td class="py-3 px-3 font-semibold text-[#FFFFFF]">NotebookLM</td>
                <td class="py-3 px-3 text-[#A1A1A6]">Assumed Gemini API wrapper with API Key.</td>
                <td class="py-3 px-3 text-[#E4E4E7]">Noted lack of public developer documentation.</td>
                <td class="py-3 px-3 text-[#C9A86A]">Classified as Tier 4 (No Public API). Closed Google consumer product with enterprise Vertex AI access only.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <!-- SECTION 5: AGENT-CONSUMABLE FOOTER & EMBEDDED DATA -->
    <section class="space-y-4 pt-4">
      <div class="border-t border-[#1E1E22] pt-8 flex items-center justify-between">
        <div>
          <h2 class="text-xs font-mono uppercase tracking-widest text-[#6E6E73] font-semibold">
            Machine Consumable Agent Interface
          </h2>
          <h3 class="text-xl font-serif text-[#FFFFFF]">
            Embedded Structured Schema Layer
          </h3>
        </div>
        <button onclick="copyStructuredJSON()" class="text-xs font-mono px-3 py-1.5 rounded-sm bg-[#FFFFFF] text-[#09090B] font-medium hover:bg-[#E4E4E7] transition-colors flex items-center space-x-1.5">
          <i data-lucide="copy" class="w-3.5 h-3.5 stroke-[1.5]"></i>
          <span>Copy Complete Dataset JSON</span>
        </button>
      </div>

      <div class="obsidian-card p-4 rounded-sm font-mono text-[11px] text-[#A1A1A6] space-y-2">
        <p>
          The complete, verified dataset (100 apps, macro patterns, and audit logs) is embedded below within 
          <code class="text-[#FFFFFF] bg-[#18181B] px-1 py-0.5 rounded border border-[#27272A]">&lt;script type=&quot;application/json&quot; id=&quot;composio-research-data&quot;&gt;</code>. 
          External agents, LLMs, and Python scripts can consume this document directly without running scrapers.
        </p>
      </div>
    </section>

  </main>

  <!-- MINIMAL FOOTER -->
  <footer class="border-t border-[#1E1E22] bg-[#09090B] mt-20 py-8">
    <div class="max-w-[1240px] mx-auto px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between text-xs font-mono text-[#6E6E73] gap-4">
      <div>
        <span>Composio Product Ops Feasibility Study</span>
        <span class="mx-2">•</span>
        <span>Generated Nov 24, 2026</span>
        <span class="mx-2">•</span>
        <span>100 Apps Audited</span>
      </div>
      <div class="flex items-center space-x-4 text-[#A1A1A6]">
        <a href="#matrix" class="hover:text-[#FFFFFF]">Matrix</a>
        <a href="data.json" class="hover:text-[#FFFFFF]">data.json</a>
        <a href="llms.txt" class="hover:text-[#FFFFFF]">/llms.txt</a>
        <a id="footer-github-link" href="https://github.com/prajwal1-1/AI-Product-Ops" target="_blank" rel="noopener noreferrer" class="hover:text-[#FFFFFF] flex items-center space-x-1">
          <i data-lucide="github" class="w-3 h-3 stroke-[1.5]"></i>
          <span>GitHub</span>
        </a>
        <button onclick="if(window.lenis) {{ lenis.scrollTo(0, {{ duration: 1.2 }}); }} else {{ window.scrollTo({{top: 0, behavior: 'smooth'}}); }}" class="hover:text-[#FFFFFF]">Top ↑</button>
      </div>
    </div>
  </footer>

  <!-- EMBEDDED STRUCTURED DATA LAYER -->
  <script type="application/json" id="composio-research-data">
{bundle_json_str}
  </script>

  <!-- ES Module for AutoAnimate -->
  <script type="module">
    try {{
      const module = await import('https://cdn.jsdelivr.net/npm/@formkit/auto-animate@0.8.2/index.mjs');
      window.autoAnimate = module.default;
      const tbody = document.getElementById('app-table-body');
      if (tbody && window.autoAnimate) {{
        window.autoAnimate(tbody);
      }}
    }} catch (e) {{
      console.warn('AutoAnimate module failed to load:', e);
    }}
  </script>

  <!-- INTERACTIVE APPLICATION LOGIC -->
  <script>
    const RAW_APPS = {apps_json_str};
    const PATTERNS = {patterns_json_str};
    const SANKEY_DATA = {sankey_data_js};
    const BAR_DATA = {bar_data_js};

    let filteredApps = [...RAW_APPS];
    const expandedRowIds = new Set();

    // Initialize Award-Winning Lenis Smooth Scroll (v1.1.18)
    let lenis;
    try {{
      lenis = new Lenis({{
        duration: 1.25,
        easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
        orientation: 'vertical',
        gestureOrientation: 'vertical',
        smoothWheel: true,
        wheelMultiplier: 1.05,
        touchMultiplier: 1.8,
        infinite: false,
      }});
      window.lenis = lenis;

      // Sync Lenis with GSAP ScrollTrigger
      if (typeof ScrollTrigger !== 'undefined') {{
        lenis.on('scroll', ScrollTrigger.update);
      }}

      // Drive Lenis directly via GSAP ticker for zero-jitter rendering
      if (typeof gsap !== 'undefined') {{
        gsap.ticker.add((time) => {{
          lenis.raf(time * 1000);
        }});
        gsap.ticker.lagSmoothing(0);
      }} else {{
        function raf(time) {{
          lenis.raf(time);
          requestAnimationFrame(raf);
        }}
        requestAnimationFrame(raf);
      }}

      // Smooth scroll navigation for all in-page anchors
      document.querySelectorAll('a[href^="#"]').forEach((anchor) => {{
        anchor.addEventListener('click', function(e) {{
          const href = this.getAttribute('href');
          if (href && href !== '#' && document.querySelector(href)) {{
            e.preventDefault();
            lenis.scrollTo(href, {{ offset: -60, duration: 1.2 }});
          }}
        }});
      }});
    }} catch(e) {{
      console.warn('Lenis could not be initialized:', e);
    }}

    // Initialize Lucide Icons & Components
    document.addEventListener("DOMContentLoaded", () => {{
      lucide.createIcons();
      renderTable();
      initECharts();
      initRoughDiagram();
      initGSAPAnimations();
    }});

    // GSAP Motion
    function initGSAPAnimations() {{
      const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
      if (prefersReducedMotion || typeof gsap === 'undefined') return;

      if (typeof ScrollTrigger !== 'undefined') {{
        gsap.registerPlugin(ScrollTrigger);
      }}

      // KPI Numbers Count-Up
      document.querySelectorAll('.kpi-num').forEach(el => {{
        const target = parseInt(el.getAttribute('data-target') || '0', 10);
        gsap.to({{ val: 0 }}, {{
          val: target,
          duration: 0.7,
          ease: "power2.out",
          scrollTrigger: {{
            trigger: el,
            start: "top 95%"
          }},
          onUpdate: function() {{
            el.textContent = Math.round(this.targets()[0].val);
          }}
        }});
      }});

      // Accuracy Progress Funnel Bars
      gsap.to(".acc-bar-1", {{
        width: "69.2%",
        duration: 0.8,
        ease: "power2.out",
        scrollTrigger: {{ trigger: "#verification", start: "top 85%" }}
      }});
      gsap.to(".acc-bar-2", {{
        width: "96.2%",
        duration: 0.8,
        delay: 0.15,
        ease: "power2.out",
        scrollTrigger: {{ trigger: "#verification", start: "top 85%" }}
      }});
      gsap.to(".acc-bar-3", {{
        width: "100%",
        duration: 0.8,
        delay: 0.3,
        ease: "power2.out",
        scrollTrigger: {{ trigger: "#verification", start: "top 85%" }}
      }});
    }}

    // Render Table
    function renderTable() {{
      const tbody = document.getElementById("app-table-body");
      const countEl = document.getElementById("filtered-count");
      countEl.textContent = filteredApps.length;

      if (filteredApps.length === 0) {{
        tbody.innerHTML = `<tr><td colspan="9" class="text-center py-10 text-[#6E6E73] font-mono text-xs">No matching platforms found. Try resetting filters.</td></tr>`;
        return;
      }}

      let html = "";
      filteredApps.forEach((app, idx) => {{
        const isExpanded = expandedRowIds.has(Number(app.id));
        const tierBadgeClass = getTierBadgeClass(app.buildability_tier);
        const verBadge = getVerificationBadge(app.verification_status);
        const iconSlug = app.slug;
        const monogram = app.monogram || 'AP';
        const inComp = app.in_composio;

        html += `
          <tr class="hover:bg-[#141417] cursor-pointer transition-colors" onclick="toggleRow(${{app.id}})">
            <td class="py-3 px-3 text-center text-[#6E6E73] font-normal">${{app.id}}</td>
            <td class="py-3 px-3 font-semibold text-[#FFFFFF]">
              <div class="flex items-center space-x-2.5">
                <div class="w-6 h-6 rounded-sm border border-[#27272A] bg-[#18181B] flex items-center justify-center overflow-hidden flex-shrink-0">
                  ${{iconSlug ? 
                    `<img src="https://cdn.jsdelivr.net/npm/simple-icons@v11/icons/${{iconSlug}}.svg" alt="${{app.name}}" class="w-3.5 h-3.5 object-contain brightness-0 invert opacity-80" />` :
                    `<span class="w-full h-full text-[9px] font-mono font-bold text-[#A1A1A6] flex items-center justify-center">${{monogram}}</span>`
                  }}
                </div>
                <div class="truncate max-w-[130px] sm:max-w-[160px]">
                  <span>${{app.name}}</span>
                </div>
              </div>
            </td>
            <td class="py-3 px-3 text-[#A1A1A6]">${{app.category}}</td>
            <td class="py-3 px-3">
              ${{inComp ? 
                `<span class="px-1.5 py-0.5 rounded-sm text-[10px] font-mono pill-comp">In Composio</span>` : 
                `<span class="px-1.5 py-0.5 rounded-sm text-[10px] font-mono font-medium pill-netnew">Net-New</span>`
              }}
            </td>
            <td class="py-3 px-3">
              <span class="px-2 py-0.5 rounded-sm bg-[#18181B] text-[#D4D4D8] border border-[#27272A] text-[11px]">
                ${{app.primary_auth}}
              </span>
            </td>
            <td class="py-3 px-3 text-[#A1A1A6]">${{app.access_model}}</td>
            <td class="py-3 px-3">
              <div class="flex items-center space-x-1.5 text-[11px]">
                <span class="text-[#D4D4D8]">${{app.api_surface}}</span>
                ${{app.mcp_status !== 'None' ? `<span class="px-1.5 py-0.2 rounded-sm text-[10px] font-medium bg-[#1C1A14] text-[#C9A86A] border border-[#3F3622]">MCP</span>` : ''}}
              </div>
            </td>
            <td class="py-3 px-3">
              <span class="px-2 py-0.5 rounded-sm text-[11px] font-medium ${{tierBadgeClass.pill}}">
                ${{tierBadgeClass.dot ? `<span class="w-1.5 h-1.5 rounded-full ${{tierBadgeClass.dot}} mr-1.5 inline-block"></span>` : ''}}
                ${{app.buildability_tier.split(':')[0]}}
              </span>
            </td>
            <td class="py-3 px-3 text-right">
              <span class="inline-flex items-center space-x-1 text-[11px] ${{verBadge.class}}">
                <span>${{verBadge.label}}</span>
                <i data-lucide="${{isExpanded ? 'chevron-up' : 'chevron-down'}}" class="w-3 h-3 stroke-[1.5] ml-1 text-[#6E6E73]"></i>
              </span>
            </td>
          </tr>

          <!-- Expandable Inline Editorial Detail Drawer -->
          <tr id="drawer-row-${{app.id}}" class="${{isExpanded ? '' : 'hidden'}}">
            <td colspan="9" class="p-0 border-b border-[#222225]">
              <div class="detail-drawer ${{isExpanded ? 'open' : ''}} bg-[#0E0E10] p-5 border-l-2 border-l-[#C9A86A] space-y-4 font-sans text-xs">
                <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div class="md:col-span-3 space-y-2">
                    <div class="font-mono text-[11px] uppercase tracking-wider text-[#6E6E73]">Platform Overview & Purpose</div>
                    <p class="text-sm font-medium text-[#FFFFFF]">${{app.one_liner}}</p>
                    <div class="pt-1 flex flex-wrap items-center gap-2 font-mono text-[11px]">
                      <span class="text-[#6E6E73]">All Auth Supported:</span>
                      ${{app.auth_methods.map(m => `<span class="px-1.5 py-0.5 rounded-sm bg-[#161619] border border-[#27272A] text-[#E4E4E7]">${{m}}</span>`).join('')}}
                    </div>
                  </div>
                  <div class="space-y-1">
                    <div class="font-mono text-[11px] uppercase tracking-wider text-[#6E6E73]">Ecosystem Reference</div>
                    <div>
                      <a href="${{app.evidence_url}}" target="_blank" rel="noopener noreferrer" class="inline-flex items-center space-x-1 text-[#C9A86A] hover:underline font-mono text-xs">
                        <span>Docs Portal</span>
                        <i data-lucide="external-link" class="w-3 h-3 stroke-[1.5]"></i>
                      </a>
                    </div>
                    <div class="text-[11px] font-mono text-[#A1A1A6] pt-1">
                      Composio: <strong class="${{inComp ? 'text-[#FFFFFF]' : 'text-[#C9A86A]'}}">${{inComp ? 'Official Toolkit (' + (app.composio_meta.slug || '') + ')' : 'Net-New Opportunity'}}</strong>
                    </div>
                    <div class="text-[11px] font-mono text-[#A1A1A6]">
                      MCP: <strong class="text-[#FFFFFF]">${{app.mcp_status}}</strong>
                    </div>
                  </div>
                </div>

                <!-- Blocker Rationale & Verification Notes -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 pt-2 border-t border-[#1E1E22]">
                  <div class="p-3 bg-[#111113] rounded-sm border border-[#222225] space-y-1">
                    <div class="font-mono text-[11px] uppercase text-[#C9A86A] font-semibold flex items-center space-x-1">
                      <i data-lucide="alert-circle" class="w-3 h-3 stroke-[1.5]"></i>
                      <span>Buildability Barrier & Access Gate</span>
                    </div>
                    <p class="text-xs text-[#A1A1A6] leading-relaxed">
                      ${{app.blocker_rationale}}
                    </p>
                  </div>

                  <div class="p-3 bg-[#111113] rounded-sm border border-[#222225] space-y-1">
                    <div class="font-mono text-[11px] uppercase text-[#E4E4E7] font-semibold flex items-center space-x-1">
                      <i data-lucide="check-circle" class="w-3 h-3 stroke-[1.5]"></i>
                      <span>Verification Audit Trail</span>
                    </div>
                    <p class="text-xs text-[#A1A1A6] leading-relaxed font-mono text-[11px]">
                      ${{app.verification_notes}}
                    </p>
                  </div>
                </div>
              </div>
            </td>
          </tr>
        `;
      }});

      tbody.innerHTML = html;
      lucide.createIcons();
    }}

    function toggleRow(id) {{
      const numId = Number(id);
      if (expandedRowIds.has(numId)) {{
        expandedRowIds.delete(numId);
      }} else {{
        expandedRowIds.add(numId);
      }}
      renderTable();
    }}
    window.toggleRow = toggleRow;

    function getTierBadgeClass(tier) {{
      if (tier.startsWith("Tier 1")) return {{ pill: "pill-t1", dot: "bg-[#C9A86A]" }};
      if (tier.startsWith("Tier 2")) return {{ pill: "pill-t2", dot: "bg-[#FFFFFF]" }};
      if (tier.startsWith("Tier 3")) return {{ pill: "pill-t3", dot: "" }};
      return {{ pill: "pill-t4", dot: "" }};
    }}

    function getVerificationBadge(status) {{
      if (status === "Verified Ground Truth") return {{ label: "Verified", class: "text-[#E4E4E7]" }};
      if (status === "Verified & Corrected") return {{ label: "Remediated", class: "text-[#C9A86A]" }};
      return {{ label: "Audited", class: "text-[#A1A1A6]" }};
    }}

    // Filter Logic
    function applyFilters() {{
      const search = document.getElementById("search-input").value.toLowerCase().trim();
      const comp = document.getElementById("filter-composio").value;
      const cat = document.getElementById("filter-category").value;
      const tier = document.getElementById("filter-tier").value;
      const auth = document.getElementById("filter-auth").value;
      const access = document.getElementById("filter-access").value;
      const mcp = document.getElementById("filter-mcp").value;

      filteredApps = RAW_APPS.filter(app => {{
        if (comp === "in_composio" && !app.in_composio) return false;
        if (comp === "net_new" && app.in_composio) return false;
        if (comp === "net_new_quick_wins" && (app.in_composio || !app.buildable_today)) return false;

        if (cat && app.category !== cat) return false;
        if (tier && app.buildability_tier !== tier) return false;
        if (auth && app.primary_auth !== auth) return false;
        if (access && app.access_model !== access) return false;
        if (mcp && app.mcp_status !== mcp) return false;
        if (search) {{
          const target = (app.name + " " + app.category + " " + app.one_liner + " " + (app.blocker_rationale || '') + " " + app.primary_auth + " " + (app.in_composio ? "in composio" : "net new")).toLowerCase();
          if (!target.includes(search)) return false;
        }}
        return true;
      }});

      renderTable();
    }}
    window.applyFilters = applyFilters;

    function resetFilters() {{
      document.getElementById("search-input").value = "";
      document.getElementById("filter-composio").value = "";
      document.getElementById("filter-category").value = "";
      document.getElementById("filter-tier").value = "";
      document.getElementById("filter-auth").value = "";
      document.getElementById("filter-access").value = "";
      document.getElementById("filter-mcp").value = "";
      filteredApps = [...RAW_APPS];
      renderTable();
    }}
    window.resetFilters = resetFilters;

    function filterByTier(tierName) {{
      document.getElementById("filter-tier").value = tierName;
      applyFilters();
      if (window.lenis) {{
        lenis.scrollTo('#matrix', {{ offset: -60, duration: 1.0 }});
      }} else {{
        const el = document.getElementById("matrix");
        if (el) el.scrollIntoView({{ behavior: "smooth" }});
      }}
    }}
    window.filterByTier = filterByTier;

    function filterByCategory(catName) {{
      document.getElementById("filter-category").value = catName;
      applyFilters();
      if (window.lenis) {{
        lenis.scrollTo('#matrix', {{ offset: -60, duration: 1.0 }});
      }} else {{
        const el = document.getElementById("matrix");
        if (el) el.scrollIntoView({{ behavior: "smooth" }});
      }}
    }}
    window.filterByCategory = filterByCategory;

    let sankeyChart = null;
    let barChart = null;

    // ECharts Initialization
    function initECharts() {{
      if (typeof echarts === 'undefined') return;

      // 1. SANKEY DIAGRAM
      const sankeyDom = document.getElementById('echarts-sankey');
      if (sankeyDom) {{
        sankeyChart = echarts.init(sankeyDom);
        const sankeyOption = {{
          tooltip: {{
            trigger: 'item',
            triggerOn: 'mousemove',
            confine: true,
            backgroundColor: '#111113',
            borderColor: '#27272A',
            borderWidth: 1,
            textStyle: {{ color: '#FFFFFF', fontFamily: 'JetBrains Mono, monospace', fontSize: 11 }},
            formatter: function(params) {{
              if (params.dataType === 'edge') {{
                return `<strong>${{params.data.source}}</strong> → <strong>${{params.data.target}}</strong><br/>Apps: <strong>${{params.data.value}}</strong>`;
              }}
              return `<strong>${{params.name}}</strong>`;
            }}
          }},
          series: [
            {{
              type: 'sankey',
              data: SANKEY_DATA.nodes,
              links: SANKEY_DATA.links,
              emphasis: {{ focus: 'adjacency' }},
              nodeAlign: 'justify',
              nodeWidth: 14,
              nodeGap: 10,
              orient: 'horizontal',
              draggable: true,
              label: {{
                color: '#A1A1A6',
                fontSize: 10,
                fontFamily: 'JetBrains Mono, monospace'
              }},
              lineStyle: {{
                curveness: 0.5
              }}
            }}
          ]
        }};
        sankeyChart.setOption(sankeyOption);

        sankeyChart.on('click', function(params) {{
          if (params.dataType === 'node') {{
            const name = params.name;
            if (name.startsWith('Tier')) {{
              filterByTier(name);
            }} else if (BAR_DATA.categories.includes(name)) {{
              filterByCategory(name);
            }} else {{
              document.getElementById("search-input").value = name;
              applyFilters();
              document.getElementById("matrix").scrollIntoView({{ behavior: "smooth" }});
            }}
          }}
        }});
      }}

      // 2. STACKED HORIZONTAL BAR (Category x Access Model)
      const barDom = document.getElementById('echarts-stacked-bar');
      if (barDom) {{
        barChart = echarts.init(barDom);
        const barOption = {{
          tooltip: {{
            trigger: 'axis',
            axisPointer: {{ type: 'shadow' }},
            confine: true,
            backgroundColor: '#111113',
            borderColor: '#27272A',
            borderWidth: 1,
            textStyle: {{ color: '#FFFFFF', fontFamily: 'JetBrains Mono, monospace', fontSize: 11 }}
          }},
          legend: {{
            top: '0%',
            itemWidth: 10,
            itemHeight: 10,
            textStyle: {{ fontFamily: 'Inter, sans-serif', fontSize: 10, color: '#A1A1A6' }}
          }},
          grid: {{
            left: '3%',
            right: '4%',
            bottom: '3%',
            top: '12%',
            containLabel: true
          }},
          xAxis: {{
            type: 'value',
            splitLine: {{ lineStyle: {{ color: '#1E1E22' }} }},
            axisLabel: {{ fontFamily: 'JetBrains Mono, monospace', fontSize: 10, color: '#6E6E73' }}
          }},
          yAxis: {{
            type: 'category',
            data: BAR_DATA.categories,
            axisLabel: {{
              fontFamily: 'Inter, sans-serif',
              fontSize: 10,
              color: '#A1A1A6',
              formatter: function(val) {{
                return val.length > 18 ? val.substring(0, 16) + '..' : val;
              }}
            }}
          }},
          series: BAR_DATA.series
        }};
        barChart.setOption(barOption);

        barChart.on('click', function(params) {{
          if (params.name) {{
            filterByCategory(params.name);
          }}
        }});
      }}

      window.addEventListener('resize', () => {{
        if (sankeyChart) sankeyChart.resize();
        if (barChart) barChart.resize();
      }});

      setTimeout(() => {{
        if (sankeyChart) sankeyChart.resize();
        if (barChart) barChart.resize();
      }}, 150);
    }}

    // Rough.js Hand-Drawn Architecture Schematic on Dark SVG
    function initRoughDiagram() {{
      const svg = document.getElementById('pipeline-svg');
      if (!svg || typeof rough === 'undefined') return;

      const rc = rough.svg(svg);

      // Box 1: Pass 1
      svg.appendChild(rc.rectangle(15, 30, 210, 160, {{ fill: '#141417', fillWeight: 0.6, roughness: 1.0, stroke: '#3F3F46', strokeWidth: 1.2 }}));
      // Box 2: Pass 2
      svg.appendChild(rc.rectangle(265, 30, 235, 160, {{ fill: '#141417', fillWeight: 0.6, roughness: 1.0, stroke: '#52525B', strokeWidth: 1.2 }}));
      // Box 3: Pass 3
      svg.appendChild(rc.rectangle(540, 30, 205, 160, {{ fill: '#141417', fillWeight: 0.6, roughness: 1.0, stroke: '#52525B', strokeWidth: 1.2 }}));
      // Box 4: Output
      svg.appendChild(rc.rectangle(785, 30, 200, 160, {{ fill: '#18181B', fillWeight: 0.6, roughness: 1.0, stroke: '#C9A86A', strokeWidth: 1.4 }}));

      // Flow Connectors
      svg.appendChild(rc.line(225, 110, 260, 110, {{ roughness: 0.8, stroke: '#A1A1A6', strokeWidth: 1.5 }}));
      svg.appendChild(rc.line(252, 104, 260, 110, {{ roughness: 0.8, stroke: '#A1A1A6', strokeWidth: 1.5 }}));
      svg.appendChild(rc.line(252, 116, 260, 110, {{ roughness: 0.8, stroke: '#A1A1A6', strokeWidth: 1.5 }}));

      svg.appendChild(rc.line(500, 110, 535, 110, {{ roughness: 0.8, stroke: '#A1A1A6', strokeWidth: 1.5 }}));
      svg.appendChild(rc.line(527, 104, 535, 110, {{ roughness: 0.8, stroke: '#A1A1A6', strokeWidth: 1.5 }}));
      svg.appendChild(rc.line(527, 116, 535, 110, {{ roughness: 0.8, stroke: '#A1A1A6', strokeWidth: 1.5 }}));

      svg.appendChild(rc.line(745, 110, 780, 110, {{ roughness: 0.8, stroke: '#C9A86A', strokeWidth: 1.5 }}));
      svg.appendChild(rc.line(772, 104, 780, 110, {{ roughness: 0.8, stroke: '#C9A86A', strokeWidth: 1.5 }}));
      svg.appendChild(rc.line(772, 116, 780, 110, {{ roughness: 0.8, stroke: '#C9A86A', strokeWidth: 1.5 }}));

      // Remediation Loop arc above Box 2 in Gold (#C9A86A)
      svg.appendChild(rc.curve([[330, 30], [380, 8], [435, 30]], {{ roughness: 1.2, stroke: '#C9A86A', strokeWidth: 1.5 }}));
      svg.appendChild(rc.line(428, 22, 435, 30, {{ roughness: 0.8, stroke: '#C9A86A', strokeWidth: 1.5 }}));

      // JetBrains Mono crisp labels
      const labels = [
        // Box 1
        {{ x: 28, y: 55, text: "PASS 1: DISCOVERY", weight: "bold", fill: "#FFFFFF", size: "11" }},
        {{ x: 28, y: 75, text: "• 100 Apps in Scope", fill: "#A1A1A6", size: "10" }},
        {{ x: 28, y: 95, text: "• Composio SDK Registry", fill: "#A1A1A6", size: "10" }},
        {{ x: 28, y: 115, text: "• Gemini Flash Research", fill: "#A1A1A6", size: "10" }},
        {{ x: 28, y: 135, text: "• 69.2% Initial Acc.", fill: "#6E6E73", size: "10" }},
        {{ x: 28, y: 165, text: "Baseline Extractor", fill: "#D4D4D8", size: "9" }},

        // Box 2
        {{ x: 278, y: 55, text: "PASS 2: VERIFICATION", weight: "bold", fill: "#FFFFFF", size: "11" }},
        {{ x: 278, y: 75, text: "• HTTP Liveness Checks", fill: "#A1A1A6", size: "10" }},
        {{ x: 278, y: 95, text: "• Firecrawl Doc Grounding", fill: "#A1A1A6", size: "10" }},
        {{ x: 278, y: 115, text: "• 14 Dead URLs Fixed", fill: "#A1A1A6", size: "10" }},
        {{ x: 278, y: 135, text: "• Verifier LLM Strict Rubric", fill: "#A1A1A6", size: "10" }},
        {{ x: 278, y: 165, text: "96.2% Sample Accuracy", fill: "#C9A86A", size: "10" }},
        {{ x: 335, y: 18, text: "Remediation Loop", fill: "#C9A86A", size: "9" }},

        // Box 3
        {{ x: 552, y: 55, text: "PASS 3: HUMAN AUDIT", weight: "bold", fill: "#FFFFFF", size: "11" }},
        {{ x: 552, y: 75, text: "• 26 Edge Cases & Traps", fill: "#A1A1A6", size: "10" }},
        {{ x: 552, y: 95, text: "• Gated Sandbox Overrides", fill: "#A1A1A6", size: "10" }},
        {{ x: 552, y: 115, text: "• CLI vs REST Topologies", fill: "#A1A1A6", size: "10" }},
        {{ x: 552, y: 135, text: "• Enterprise Licensing Check", fill: "#A1A1A6", size: "10" }},
        {{ x: 552, y: 165, text: "100.0% Audited Truth", fill: "#C9A86A", size: "10" }},

        // Box 4
        {{ x: 798, y: 55, text: "OUTPUT: TRIAGED MATRIX", weight: "bold", fill: "#C9A86A", size: "11" }},
        {{ x: 798, y: 75, text: "• Tier 1: {t1_count} Ship Now", fill: "#FFFFFF", size: "10" }},
        {{ x: 798, y: 95, text: "• Tier 2: {t2_count} Wrap MCP", fill: "#E4E4E7", size: "10" }},
        {{ x: 798, y: 115, text: "• Tier 3: {t3_count} Ops Queue", fill: "#A1A1A6", size: "10" }},
        {{ x: 798, y: 135, text: "• Tier 4: {t4_count} Sales Wall", fill: "#71717A", size: "10" }},
        {{ x: 798, y: 165, text: "{buildable_count}% Immediate Wins", fill: "#C9A86A", size: "10" }}
      ];

      labels.forEach(l => {{
        const textNode = document.createElementNS("http://www.w3.org/2000/svg", "text");
        textNode.setAttribute("x", l.x);
        textNode.setAttribute("y", l.y);
        textNode.setAttribute("font-family", "JetBrains Mono, monospace");
        textNode.setAttribute("font-size", l.size || "10");
        if (l.weight) textNode.setAttribute("font-weight", l.weight);
        textNode.setAttribute("fill", l.fill || "#FFFFFF");
        textNode.textContent = l.text;
        svg.appendChild(textNode);
      }});
    }}

    // Clipboard Copy with robust fallback
    function copyStructuredJSON() {{
      const dataEl = document.getElementById("composio-research-data");
      const text = dataEl.textContent.trim();
      
      function showSuccess() {{
        const btn = document.getElementById("copy-json-btn");
        if (!btn) return;
        const orig = btn.innerHTML;
        btn.innerHTML = `<i data-lucide="check" class="w-3.5 h-3.5 stroke-[1.5]"></i><span>Copied to Clipboard!</span>`;
        btn.classList.add("border-[#C9A86A]", "text-[#C9A86A]");
        lucide.createIcons();
        setTimeout(() => {{
          btn.innerHTML = orig;
          btn.classList.remove("border-[#C9A86A]", "text-[#C9A86A]");
          lucide.createIcons();
        }}, 2200);
      }}

      function fallbackCopy(str) {{
        const temp = document.createElement("textarea");
        temp.value = str;
        temp.style.position = "fixed";
        temp.style.left = "-9999px";
        document.body.appendChild(temp);
        temp.select();
        try {{
          document.execCommand("copy");
          showSuccess();
        }} catch (e) {{
          console.warn("Fallback copy error:", e);
        }}
        document.body.removeChild(temp);
      }}

      if (navigator.clipboard && navigator.clipboard.writeText) {{
        navigator.clipboard.writeText(text).then(showSuccess).catch(() => fallbackCopy(text));
      }} else {{
        fallbackCopy(text);
      }}
    }}
    window.copyStructuredJSON = copyStructuredJSON;
  </script>
</body>
</html>
"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✔ Successfully generated museum-grade Obsidian & Gold index.html ({len(html)} bytes)")

if __name__ == "__main__":
    build()
