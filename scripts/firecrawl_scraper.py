"""
Firecrawl Doc Scraper Wrapper.

Uses firecrawl-py (supporting Keyless free usage or authenticated API key)
with automatic fallback to httpx + BeautifulSoup for reliable markdown extraction.
"""

import os
import re
import httpx
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional

try:
    from firecrawl import FirecrawlApp
    HAS_FIRECRAWL = True
except ImportError:
    HAS_FIRECRAWL = False

class DocScraper:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("FIRECRAWL_API_KEY")
        self.firecrawl_client = None
        if HAS_FIRECRAWL and self.api_key:
            try:
                self.firecrawl_client = FirecrawlApp(api_key=self.api_key)
            except Exception as e:
                print(f"[Warning] Firecrawl init failed: {e}")
        self.http_client = httpx.Client(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            },
            timeout=12.0,
            follow_redirects=True
        )

    def scrape(self, url: str) -> Dict[str, Any]:
        # Clean URL if formatted as markdown link [text](url)
        md_match = re.search(r"\((https?://[^)]+)\)", url)
        if md_match:
            target_url = md_match.group(1)
        elif not url.startswith("http"):
            target_url = f"https://{url}"
        else:
            target_url = url

        # Attempt 1: Firecrawl (if configured)
        if self.firecrawl_client:
            try:
                res = self.firecrawl_client.scrape_url(target_url, params={"formats": ["markdown"]})
                if res and "markdown" in res:
                    return {
                        "url": target_url,
                        "success": True,
                        "engine": "firecrawl",
                        "content": res["markdown"][:4000]
                    }
            except Exception as e:
                # Fallback to direct HTTP
                pass

        # Attempt 2: Direct HTTP + BeautifulSoup Markdown extraction
        try:
            resp = self.http_client.get(target_url)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                # Remove scripts, styles, navigations
                for tag in soup(["script", "style", "nav", "footer", "noscript"]):
                    tag.decompose()
                
                # Extract main text
                text = soup.get_text(separator="\n", strip=True)
                lines = [line for line in text.splitlines() if line]
                clean_text = "\n".join(lines[:120])
                return {
                    "url": target_url,
                    "success": True,
                    "engine": "httpx_soup",
                    "content": clean_text[:3500]
                }
            else:
                return {
                    "url": target_url,
                    "success": False,
                    "engine": "httpx_soup",
                    "error": f"HTTP status {resp.status_code}",
                    "content": ""
                }
        except Exception as e:
            return {
                "url": target_url,
                "success": False,
                "engine": "error",
                "error": str(e),
                "content": ""
            }

if __name__ == "__main__":
    scraper = DocScraper()
    test = scraper.scrape("https://twenty.com")
    print(f"Scraped {test['url']} via {test['engine']}: success={test['success']}, length={len(test['content'])}")
