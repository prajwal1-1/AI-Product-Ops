import csv
import httpx

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
client = httpx.Client(headers=headers, timeout=10.0, follow_redirects=True)

with open("data/human_audit_sample.csv", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        url = r["evidence_url"]
        try:
            res = client.get(url)
            status = res.status_code
        except Exception as e:
            status = f"ERR: {str(e)[:30]}"
        print(f"[{status}] {r['id']}. {r['name']}: {url}")
