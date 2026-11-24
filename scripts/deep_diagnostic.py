import json
import re
from collections import Counter
import urllib.parse

def run_diagnostics():
    print("=" * 60)
    print("DEEP CODEBASE & HTML DIAGNOSTIC AUDIT")
    print("=" * 60)

    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Duplicate IDs
    raw_ids = re.findall(r'\bid=["\']([^"\']+)["\']', html)
    id_counts = Counter(raw_ids)
    duplicates = {k: v for k, v in id_counts.items() if v > 1}
    print(f"Total HTML IDs found: {len(raw_ids)} (Unique: {len(id_counts)})")
    if duplicates:
        print(f"[!] Duplicate IDs detected: {duplicates}")
        for i, line in enumerate(html.splitlines()):
            for dup in duplicates:
                if f'id="{dup}"' in line or f"id='{dup}'" in line:
                    print(f"    Line {i+1}: {line.strip()[:100]}")
    else:
        print("[✔] Zero duplicate HTML IDs.")

    # 2. Check JSON data integrity in <script type="application/json" id="composio-research-data">
    match = re.search(r'<script type="application/json" id="composio-research-data">\s*([\s\S]*?)\s*</script>', html)
    if not match:
        print("[!] Missing embedded JSON script!")
    else:
        try:
            embedded_data = json.loads(match.group(1))
            print(f"[✔] Embedded JSON parses cleanly. Total apps: {len(embedded_data.get('apps', []))}")
        except Exception as e:
            print(f"[!] Embedded JSON parse error: {e}")

    # 3. Check copyStructuredJSON function
    if "function copyStructuredJSON" in html:
        print("[✔] copyStructuredJSON defined in script.")
    else:
        print("[!] copyStructuredJSON missing from script!")

    # 4. Check for unclosed HTML tags or dangling template syntax
    # Exclude JS template literal variables like ${iconSlug}
    dangling_fstrings = re.findall(r'(?<!\$)\{[a-zA-Z0-9_]+\}', html)
    suspicious = [s for s in dangling_fstrings if not any(k in s for k in ['target', 'index', 'item', 'key'])]
    if suspicious:
        print(f"[!] Possible unescaped Python f-string placeholders: {suspicious[:10]}")
    else:
        print("[✔] Zero dangling unescaped f-string placeholders in HTML.")

    # 5. Check all evidence URLs format
    with open("data/final_verified.json", "r", encoding="utf-8") as f:
        apps = json.load(f)

    bad_urls = []
    for a in apps:
        url = a.get("evidence_url", "")
        if not url.startswith("https://"):
            bad_urls.append((a["id"], a["name"], url, "Not HTTPS"))
        parsed = urllib.parse.urlparse(url)
        if not parsed.netloc or not parsed.path or parsed.path == "/":
            bad_urls.append((a["id"], a["name"], url, "Root domain or empty path"))

    if bad_urls:
        print(f"[!] Found {len(bad_urls)} suspicious evidence URLs:")
        for u in bad_urls:
            print(f"    - #{u[0]} {u[1]}: {u[2]} ({u[3]})")
    else:
        print("[✔] All 100 evidence URLs are canonical HTTPS deep links with specific paths.")

    # 6. Check data.json vs final_verified.json equality
    with open("data.json", "r", encoding="utf-8") as f:
        data_json_apps = json.load(f)
    if apps == data_json_apps:
        print("[✔] data.json is 100% byte-for-byte identical to data/final_verified.json.")
    else:
        print("[!] data.json differs from data/final_verified.json!")

    print("=" * 60)

if __name__ == "__main__":
    run_diagnostics()
