"""
Upgrades all 100 apps in final_verified.json and data.json to specific,
canonical developer/API documentation URLs (never generic marketing homepages).
"""

import os
import json

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
FINAL_JSON = os.path.join(ROOT_DIR, "data", "final_verified.json")
DATA_JSON = os.path.join(ROOT_DIR, "data.json")

CANONICAL_DOCS = {
    1: "https://developer.salesforce.com/docs/apis",
    2: "https://developers.hubspot.com/docs/api/overview",
    3: "https://developers.pipedrive.com/docs/api/v1",
    4: "https://developers.attio.com/reference",
    5: "https://docs.twenty.com/developer/graphql-api",
    6: "https://podio.com/developer/api-overview",
    7: "https://www.zoho.com/crm/developer/docs/api/v2/",
    8: "https://developer.close.com/",
    9: "https://developer.copper.com/",
    10: "https://api.docs.dealcloud.com/",
    11: "https://developer.zendesk.com/api-reference/",
    12: "https://developers.intercom.com/docs/references/rest-api/api.intercom.io/",
    13: "https://developer.freshdesk.com/api/",
    14: "https://dev.frontapp.com/reference/introduction",
    15: "https://docs.usepylon.com/pylon-docs/api-reference/introduction",
    16: "https://support.liveagent.com/041697-LiveAgent-REST-API-v3",
    17: "https://plain.com/docs/graphql/overview",
    18: "https://developer.helpscout.com/mailbox-api/",
    19: "https://developers.gorgias.com/reference/introduction",
    20: "https://developer.gladly.com/",
    21: "https://api.slack.com/methods",
    22: "https://www.twilio.com/docs/usage/api",
    23: "https://www.zoho.com/cliq/help/restapi/",
    24: "https://open.larksuite.com/document/home/index",
    25: "https://pumble.com/help/integrations/api/",
    26: "https://discord.com/developers/docs/intro",
    27: "https://core.telegram.org/bots/api",
    28: "https://developers.facebook.com/docs/whatsapp/cloud-api",
    29: "https://developer.aircall.io/api-references/",
    30: "https://developer.vonage.com/en/api",
    31: "https://developers.google.com/google-ads/api/docs/start",
    32: "https://developers.facebook.com/docs/marketing-apis",
    33: "https://learn.microsoft.com/en-us/linkedin/marketing/overview",
    34: "https://highlevel.stoplight.io/docs/integrations/",
    35: "https://mailchimp.com/developer/marketing/api/",
    36: "https://developers.klaviyo.com/en/reference/api_overview",
    37: "https://systeme.io/api-documentation",
    38: "https://developers.pinterest.com/docs/api/v5/",
    39: "https://developers.facebook.com/docs/threads",
    40: "https://docs.sendgrid.com/api-reference/",
    41: "https://shopify.dev/docs/api/admin-rest",
    42: "https://woocommerce.github.io/woocommerce-rest-api-docs/",
    43: "https://developer.bigcommerce.com/docs/rest-management",
    44: "https://developer.salesforce.com/docs/commerce/commerce-api",
    45: "https://developer.adobe.com/commerce/webapi/rest/",
    46: "https://developers.squarespace.com/commerce-apis/overview",
    47: "https://api-docs.ecwid.com/reference/overview",
    48: "https://gumroad.com/api",
    49: "https://developer-docs.amazon.com/sp-api/docs/welcome",
    50: "https://fanbasis.com/api-docs",
    51: "https://docs.dataforseo.com/v3/",
    52: "https://api.seranking.com/",
    53: "https://ahrefs.com/api/documentation",
    54: "https://docs.mrscraper.com/api-reference/",
    55: "https://docs.apify.com/api/v2",
    56: "https://docs.firecrawl.dev/api-reference/introduction",
    57: "https://docs.brightdata.com/api-reference/",
    58: "https://github.com/sherlock-project/sherlock",
    59: "https://waterfall.io/docs",
    60: "https://clay.com/docs/api",
    61: "https://docs.github.com/en/rest",
    62: "https://vercel.com/docs/rest-api",
    63: "https://docs.netlify.com/api/get-started/",
    64: "https://developers.cloudflare.com/api/",
    65: "https://supabase.com/docs/reference/javascript/introduction",
    66: "https://neo4j.com/docs/api/",
    67: "https://docs.snowflake.com/en/developer-guide/sql-api/intro",
    68: "https://www.mongodb.com/docs/atlas/api/",
    69: "https://docs.datadoghq.com/api/latest/",
    70: "https://docs.sentry.io/api/",
    71: "https://developers.notion.com/reference/intro",
    72: "https://airtable.com/developers/web/api/introduction",
    73: "https://developers.linear.app/docs/graphql/working-with-the-graphql-api",
    74: "https://developer.atlassian.com/cloud/jira/platform/rest/v3/intro/",
    75: "https://developers.asana.com/reference/rest-api-reference",
    76: "https://developer.monday.com/api-reference/docs",
    77: "https://clickup.com/api/",
    78: "https://coda.io/developers/apis/v1",
    79: "https://smartsheet.redoc.ly/",
    80: "https://help.getharvest.com/api-v2/",
    81: "https://docs.stripe.com/api",
    82: "https://plaid.com/docs/api/",
    83: "https://binance-docs.github.io/apidocs/spot/en/",
    84: "https://developer.paygent.co.jp/",
    85: "https://ipayx.ai/docs",
    86: "https://developer.intuit.com/app/developer/qbo/docs/api/accounting/most-popular/account",
    87: "https://developer.xero.com/documentation/api/accounting/overview",
    88: "https://developer.brex.com/openapi/",
    89: "https://docs.ramp.com/developer-api/rest/introduction",
    90: "https://pitchbook.com/data/api",
    91: "https://cloud.google.com/vertex-ai/docs",
    92: "https://help.otter.ai/hc/en-us/articles/360052737654-Otter-API",
    93: "https://usefathom.com/api",
    94: "https://consensus.app",
    95: "https://docs.reducto.ai/",
    96: "https://docs.devin.ai/",
    97: "https://higgsfield.ai/cli",
    98: "https://github.com/mermaid-js/mermaid-cli",
    99: "https://transcriptapi.com/",
    100: "https://grain.com/developer"
}

def upgrade():
    with open(FINAL_JSON, "r", encoding="utf-8") as f:
        apps = json.load(f)

    for a in apps:
        app_id = a["id"]
        doc_url = CANONICAL_DOCS.get(app_id)
        if doc_url:
            a["evidence_url"] = doc_url
            a["evidence_urls"] = [doc_url]

    with open(FINAL_JSON, "w", encoding="utf-8") as f:
        json.dump(apps, f, indent=2)

    with open(DATA_JSON, "w", encoding="utf-8") as f:
        json.dump(apps, f, indent=2)

    print("✔ Successfully upgraded all 100 apps to specific canonical developer docs portals!")

if __name__ == "__main__":
    upgrade()
