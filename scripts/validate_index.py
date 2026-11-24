import json

with open("index.html", "r", encoding="utf-8") as f:
    html = f.read()

tag = '<script type="application/json" id="composio-research-data">'
start = html.find(tag) + len(tag)
end = html.find('</script>', start)
embedded_json = html[start:end].strip()

data = json.loads(embedded_json)
print("✔ Total apps embedded in index.html:", len(data["apps"]))
print("✔ Total patterns embedded:", len(data["patterns"]))
print("✔ Metadata:", data["metadata"])
print("✔ index.html verified successfully!")
