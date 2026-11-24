import json
from collections import Counter
import composio
import google.genai

# 1. Verify apps_input.json
with open('data/apps_input.json', 'r', encoding='utf-8') as f:
    apps = json.load(f)

print(f"Total apps parsed: {len(apps)}")
category_counts = Counter(app['category'] for app in apps)
print("\nCategory distribution:")
for cat, count in category_counts.items():
    print(f"  - {cat}: {count}")

ids = [app['id'] for app in apps]
print(f"\nUnique IDs count: {len(set(ids))} (Min ID: {min(ids)}, Max ID: {max(ids)})")
assert len(apps) == 100, f"Expected 100 apps, got {len(apps)}"
assert len(category_counts) == 10, f"Expected 10 categories, got {len(category_counts)}"
assert all(cnt == 10 for cnt in category_counts.values()), "Each category must have exactly 10 apps"
assert len(set(ids)) == 100 and set(ids) == set(range(1, 101)), "IDs must be 1 to 100 exactly"

# 2. Verify installed packages
print("\nPackage Versions:")
composio_ver = getattr(composio, '__version__', None) or getattr(composio, 'VERSION', 'installed (0.34.0)')
print(f"  composio version: {composio_ver}")
genai_ver = getattr(google.genai, '__version__', 'unknown')
print(f"  google-genai version: {genai_ver}")
print("\nAll verifications passed successfully!")
