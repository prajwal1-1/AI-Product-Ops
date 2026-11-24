"""
Comprehensive Automated QA Test Suite for Composio 100-App Agent Research.
Runs 5 strict phases of QA validation:
1. Schema & Count Integrity on data.json and data/final_verified.json
2. Numerical Cross-Reconciliation across index.html, llms.txt, and patterns_summary.json
3. Zero-Leak & Hygiene Audit (no API keys, undefined, NaN, or raw TODOs)
4. Environment & Git Boundary Hygiene (.gitignore checks)
5. CLI Smoke Test (reproduction command python scripts/01_research_agent.py --app "Stripe")
"""

import os
import sys
import json
import re
import subprocess

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))

PASSED = "PASS"
FAILED = "FAIL"

class QAException(Exception):
    pass

def log_test(name: str, status: str, details: str = ""):
    symbol = "✔" if status == PASSED else "✖"
    print(f"[{symbol} {status}] {name}")
    if details:
        print(f"         {details}")

def test_phase_1_schema_and_counts():
    """Validates 100 rows, required keys, enum values, and https links."""
    json_paths = [
        os.path.join(ROOT_DIR, "data", "final_verified.json"),
        os.path.join(ROOT_DIR, "data.json")
    ]
    
    required_keys = [
        "id", "name", "category", "one_liner", "auth_methods", "primary_auth",
        "access_model", "api_surface", "mcp_status", "buildability_tier",
        "buildable_today", "main_blocker", "evidence_urls", "evidence_url",
        "in_composio", "composio_meta"
    ]
    
    valid_tiers = {
        "Tier 1: Ship Now", "Tier 2: Wrap MCP / CLI",
        "Tier 3: Ops / Review Queue", "Tier 4: BD / Sales Wall"
    }
    valid_access = {
        "Self-Serve Free", "Self-Serve Paid/Trial",
        "Sandbox Self-Serve / Prod Gated", "Enterprise / Sales Gated",
        "Open-Source / Local"
    }
    valid_surfaces = {
        "REST", "GraphQL", "REST + GraphQL", "SDK/CLI Only", "No Public API"
    }
    valid_mcp = {"Official MCP", "Community MCP", "None"}

    for path in json_paths:
        filename = os.path.basename(path)
        if not os.path.exists(path):
            raise QAException(f"Missing required file: {path}")

        with open(path, "r", encoding="utf-8") as f:
            apps = json.load(f)

        if len(apps) != 100:
            raise QAException(f"{filename} contains {len(apps)} apps, expected exactly 100")

        categories = {}
        for idx, a in enumerate(apps, 1):
            if a["id"] != idx:
                raise QAException(f"{filename} app id mismatch: {a['id']} != {idx}")
            
            for k in required_keys:
                if k not in a:
                    raise QAException(f"{filename} app #{idx} ({a['name']}) missing key: {k}")
                val = a[k]
                if val is None or val == "" or val == "N/A" or val == "TBD" or val == "Unknown":
                    if k not in ["mcp_url"]: # allowed to be null if None
                        raise QAException(f"{filename} app #{idx} has invalid empty/null key: {k}={val}")

            if a["buildability_tier"] not in valid_tiers:
                raise QAException(f"{filename} app #{idx} invalid tier: {a['buildability_tier']}")
            if a["access_model"] not in valid_access:
                raise QAException(f"{filename} app #{idx} invalid access_model: {a['access_model']}")
            if a["api_surface"] not in valid_surfaces:
                raise QAException(f"{filename} app #{idx} invalid api_surface: {a['api_surface']}")
            if a["mcp_status"] not in valid_mcp:
                raise QAException(f"{filename} app #{idx} invalid mcp_status: {a['mcp_status']}")

            # Evidence URL validation
            ev_url = a["evidence_url"]
            if not ev_url.startswith("https://"):
                raise QAException(f"{filename} app #{idx} evidence_url not https: {ev_url}")
            if "google.com/search" in ev_url:
                raise QAException(f"{filename} app #{idx} has fallback search URL: {ev_url}")

            cat = a["category"]
            categories[cat] = categories.get(cat, 0) + 1

        if len(categories) != 10:
            raise QAException(f"{filename} has {len(categories)} categories, expected 10")
        for cat, cnt in categories.items():
            if cnt != 10:
                raise QAException(f"{filename} category '{cat}' has {cnt} apps, expected 10")

    log_test("Phase 1: Schema & Counts", PASSED, "Both final_verified.json and data.json have 100 apps, 10 categories (10 each), valid enums & https URLs.")

def test_phase_2_numerical_reconciliation():
    """Verifies that numbers in patterns_summary.json, index.html, and llms.txt match."""
    patterns_path = os.path.join(ROOT_DIR, "data", "patterns_summary.json")
    index_path = os.path.join(ROOT_DIR, "index.html")
    llms_path = os.path.join(ROOT_DIR, "llms.txt")

    with open(patterns_path, "r", encoding="utf-8") as f:
        patterns = json.load(f)

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    with open(llms_path, "r", encoding="utf-8") as f:
        llms = f.read()

    tiers = patterns["macro_metrics"]["buildability_tiers"]
    t1 = tiers["Tier 1: Ship Now"]
    t2 = tiers["Tier 2: Wrap MCP / CLI"]
    t3 = tiers["Tier 3: Ops / Review Queue"]
    t4 = tiers["Tier 4: BD / Sales Wall"]
    buildable = t1 + t2

    comp = patterns["composio_catalog_comparison"]
    already_comp = comp["already_in_composio_count"]
    net_new = comp["net_new_apps_count"]
    net_new_qw = comp["net_new_quick_wins_count"]

    acc = patterns["accuracy_progression"]
    p1_acc = acc["pass1_accuracy"] # "69.2%"
    p2_acc = acc["pass2_accuracy"] # "96.2%"
    final_acc = acc["final_verified_accuracy"] # "100.0%"

    # Check index.html contains key metrics
    assert str(t1) in html, f"Tier 1 count {t1} missing in index.html"
    assert str(t2) in html, f"Tier 2 count {t2} missing in index.html"
    assert str(t3) in html, f"Tier 3 count {t3} missing in index.html"
    assert str(t4) in html, f"Tier 4 count {t4} missing in index.html"
    assert str(buildable) in html, f"Buildable count {buildable} missing in index.html"
    assert str(already_comp) in html, f"Already in Composio count {already_comp} missing in index.html"
    assert str(net_new) in html, f"Net-new count {net_new} missing in index.html"
    assert p1_acc in html, f"Pass 1 accuracy {p1_acc} missing in index.html"
    assert p2_acc in html, f"Pass 2 accuracy {p2_acc} missing in index.html"
    assert final_acc in html, f"Final accuracy {final_acc} missing in index.html"

    # Check llms.txt contains key metrics
    assert str(t1) in llms, f"Tier 1 count {t1} missing in llms.txt"
    assert str(t2) in llms, f"Tier 2 count {t2} missing in llms.txt"
    assert str(t3) in llms, f"Tier 3 count {t3} missing in llms.txt"
    assert str(t4) in llms, f"Tier 4 count {t4} missing in llms.txt"
    assert str(buildable) in llms, f"Buildable count {buildable} missing in llms.txt"
    assert str(already_comp) in llms, f"Already in Composio count {already_comp} missing in llms.txt"
    assert str(net_new) in llms, f"Net-new count {net_new} missing in llms.txt"
    assert p1_acc in llms, f"Pass 1 accuracy {p1_acc} missing in llms.txt"
    assert p2_acc in llms, f"Pass 2 accuracy {p2_acc} missing in llms.txt"
    assert final_acc in llms, f"Final accuracy {final_acc} missing in llms.txt"

    log_test("Phase 2: Numerical Reconciliation", PASSED, f"All metrics perfectly reconciled across patterns_summary.json, index.html, and llms.txt (T1={t1}, T2={t2}, T3={t3}, T4={t4}, Comp={already_comp}, NetNew={net_new}).")

def test_phase_3_zero_leaks_and_hygiene():
    """Scans for API keys, undefined, NaN, and raw TODO strings."""
    forbidden_tokens = ["AIza", "comp_", "sk-proj-", "sk-ant-", "ghp_"]
    scanned_files = [
        "index.html", "data.json", "llms.txt", "README.md",
        "data/final_verified.json", "data/patterns_summary.json"
    ]

    for rel_path in scanned_files:
        full_path = os.path.join(ROOT_DIR, rel_path)
        if not os.path.exists(full_path):
            continue
        with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        for token in forbidden_tokens:
            if token in content:
                raise QAException(f"Potential secret token '{token}' detected in {rel_path}!")

        # Scan for 'undefined' or 'NaN' in prose or JSON
        if rel_path in ["index.html", "llms.txt"]:
            if " undefined " in content or "NaN" in content:
                raise QAException(f"Unrendered 'undefined' or 'NaN' detected in {rel_path}!")
            if "TODO" in content:
                raise QAException(f"Unresolved 'TODO' found in {rel_path}!")

    log_test("Phase 3: Zero-Leak & Hygiene Audit", PASSED, "Zero leaked keys (AIza, comp_), zero undefined/NaN, and zero raw TODOs across tracked files.")

def test_phase_4_git_boundary():
    """Verifies .gitignore exists and properly ignores .env and .venv/."""
    gitignore_path = os.path.join(ROOT_DIR, ".gitignore")
    if not os.path.exists(gitignore_path):
        raise QAException("Missing .gitignore file in project root!")

    with open(gitignore_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines()]

    if ".env" not in lines:
        raise QAException(".gitignore must explicitly ignore .env")
    if not any(v in lines for v in [".venv", ".venv/"]):
        raise QAException(".gitignore must explicitly ignore .venv/")

    log_test("Phase 4: Git Boundary & Security", PASSED, ".gitignore properly enforces isolation for .env and .venv/.")

def test_phase_5_smoke_test_cli():
    """Runs a live smoke test of python scripts/01_research_agent.py --app 'Stripe'."""
    script_path = os.path.join(ROOT_DIR, "scripts", "01_research_agent.py")
    python_exe = sys.executable

    res = subprocess.run(
        [python_exe, script_path, "--app", "Stripe"],
        capture_output=True,
        text=True,
        timeout=30
    )

    if res.returncode != 0:
        raise QAException(f"CLI smoke test failed with code {res.returncode}:\n{res.stderr}")
    
    if "Stripe" not in res.stdout:
        raise QAException(f"CLI smoke test output did not contain 'Stripe':\n{res.stdout}")

    log_test("Phase 5: CLI Smoke Test", PASSED, "Successfully executed 'python scripts/01_research_agent.py --app \"Stripe\"' with exit code 0.")

def run_all_qa():
    print("=" * 60)
    print("  COMPOSIO 100-APP RESEARCH PIPELINE - PRE-FLIGHT QA SUITE  ")
    print("=" * 60)
    
    failures = 0
    try:
        test_phase_1_schema_and_counts()
    except Exception as e:
        log_test("Phase 1: Schema & Counts", FAILED, str(e))
        failures += 1

    try:
        test_phase_2_numerical_reconciliation()
    except Exception as e:
        log_test("Phase 2: Numerical Reconciliation", FAILED, str(e))
        failures += 1

    try:
        test_phase_3_zero_leaks_and_hygiene()
    except Exception as e:
        log_test("Phase 3: Zero-Leak & Hygiene Audit", FAILED, str(e))
        failures += 1

    try:
        test_phase_4_git_boundary()
    except Exception as e:
        log_test("Phase 4: Git Boundary & Security", FAILED, str(e))
        failures += 1

    try:
        test_phase_5_smoke_test_cli()
    except Exception as e:
        log_test("Phase 5: CLI Smoke Test", FAILED, str(e))
        failures += 1

    print("=" * 60)
    if failures == 0:
        print("  ALL 5 QA PHASES PASSED WITH ZERO ERRORS. READY FOR DEPLOY! ")
        print("=" * 60)
        sys.exit(0)
    else:
        print(f"  FAILED: {failures} QA check(s) did not pass. Please fix above errors.")
        print("=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    run_all_qa()
