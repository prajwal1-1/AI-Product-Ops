import json

URL_UPDATES = {
    8: "https://developer.close.com/resources/",
    9: "https://developer.copper.com/overview/getting-started",
    10: "https://api.docs.dealcloud.com/docs/getting-started",
    20: "https://developer.gladly.com/rest/",
    52: "https://seranking.com/api.html",
    79: "https://smartsheet.redoc.ly/tag/sheets",
    84: "https://developer.paygent.co.jp/doc/",
    94: "https://consensus.app/search/",
    95: "https://docs.reducto.ai/introduction",
    96: "https://docs.devin.ai/api-reference/introduction",
    99: "https://transcriptapi.com/docs"
}

with open("data/final_verified.json", "r", encoding="utf-8") as f:
    apps = json.load(f)

updated_count = 0
for app in apps:
    app_id = app.get("id")
    if app_id in URL_UPDATES:
        new_url = URL_UPDATES[app_id]
        app["evidence_url"] = new_url
        app["evidence_urls"] = [new_url]
        updated_count += 1
        print(f"Updated #{app_id} {app['name']} -> {new_url}")

with open("data/final_verified.json", "w", encoding="utf-8") as f:
    json.dump(apps, f, indent=2)

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(apps, f, indent=2)

print(f"✔ Successfully updated {updated_count} URLs across data/final_verified.json and data.json")
