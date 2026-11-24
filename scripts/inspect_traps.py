import json

apps = json.load(open('data/final_verified.json', encoding='utf-8'))
traps = [10, 20, 28, 31, 32, 33, 49, 58, 90, 91, 92, 94, 96, 97, 98, 99]

print("=== AUDITING 12+ TRAP APPS ===")
for a in apps:
    if a['id'] in traps:
        blocker = a.get('main_blocker') or a.get('blocker_rationale')
        notes = a.get('verification_notes') or a.get('pass1_notes')
        print(f"#{a['id']:02d} {a['name']}")
        print(f"  Tier: {a['buildability_tier']}")
        print(f"  Primary Auth: {a['primary_auth']}")
        print(f"  Access Model: {a['access_model']}")
        print(f"  API Surface: {a['api_surface']}")
        print(f"  MCP: {a['mcp_status']}")
        print(f"  One-liner: {a['one_liner']}")
        print(f"  Blocker: {blocker}")
        print(f"  Evidence: {a['evidence_urls']}")
        print(f"  Notes: {notes}")
        print("-" * 60)
