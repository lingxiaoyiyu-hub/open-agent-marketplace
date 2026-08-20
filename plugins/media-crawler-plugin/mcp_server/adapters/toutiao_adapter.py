"""
今日头条 (Toutiao) Data Adapter.
Supports: Hot trending board, channel feed sampling, keyword search, and article extraction.
"""
from typing import List, Dict, Any, Optional
import re
try:
    from ..core.api_client import APIClient
except (ImportError, ValueError):
    from core.api_client import APIClient

class ToutiaoAdapter:
    def __init__(self, api_client: Optional[APIClient] = None):
        self.client = api_client or APIClient()

    async def get_trending(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch real-time top trending topics from Toutiao PC Hot Board."""
        url = "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc"
        res = await self.client.get_json(url)
        items = []
        if res and "data" in res:
            for i, raw in enumerate(res["data"][:limit], 1):
                items.append({
                    "rank": i,
                    "platform": "toutiao",
                    "title": raw.get("Title", ""),
                    "hot_value": raw.get("HotValue", ""),
                    "label": raw.get("LabelDesc", "") or raw.get("Label", ""),
                    "cluster_id": str(raw.get("ClusterId", "")),
                    "url": raw.get("Url", ""),
                    "cover_image": raw.get("Image", {}).get("url", "") if isinstance(raw.get("Image"), dict) else "",
                })
        return items

    async def search_articles(self, keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search Toutiao articles with keyword."""
        url = f"https://www.toutiao.com/api/search/content/?keyword={keyword}&format=json&cur_tab=1&offset=0&count={limit}"
        res = await self.client.get_json(url)
        results = []
        if res and "data" in res:
            for item in res["data"]:
                if item.get("title") and item.get("article_url"):
                    results.append({
                        "platform": "toutiao",
                        "title": item.get("title", ""),
                        "abstract": item.get("abstract", ""),
                        "author": item.get("media_name", "") or item.get("source", ""),
                        "comments_count": item.get("comments_count", 0),
                        "publish_time": item.get("datetime", ""),
                        "url": item.get("article_url", ""),
                        "item_id": str(item.get("item_id", "") or item.get("id", ""))
                    })
        return results[:limit]

    async def extract_article(self, url: str) -> Dict[str, Any]:
        """Fetch article HTML and parse main content."""
        html = await self.client.get_text(url)
        if not html:
            return {"platform": "toutiao", "url": url, "error": "Failed to fetch article page"}

        # Extract title
        title_match = re.search(r'<h1[^>]*class=[\'"][^\'"]*article-title[^\'"]*[\'"][^>]*>([\s\S]*?)</h1>', html, re.I) or \
                      re.search(r'<title>([\s\S]*?)</title>', html, re.I)
        title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip() if title_match else ""
        title = re.sub(r' - 今日头条.*', '', title).strip()

        # Extract content text from article body or script data
        content_match = re.search(r'<article[^>]*>([\s\S]*?)</article>', html, re.I) or \
                        re.search(r'<div[^>]*class=[\'"][^\'"]*article-content[^\'"]*[\'"][^>]*>([\s\S]*?)</div>', html, re.I)
        if content_match:
            raw_content = content_match.group(1)
            content = re.sub(r'<p[^>]*>', '\n', raw_content)
            content = re.sub(r'<[^>]+>', '', content)
            content = re.sub(r'\n\s*\n', '\n', content).strip()
        else:
            content = re.sub(r'<script[\s\S]*?</script>', '', html)
            content = re.sub(r'<style[\s\S]*?</style>', '', content)
            content = re.sub(r'<[^>]+>', ' ', content)
            content = re.sub(r'\s+', ' ', content)[:2000].strip()

        return {
            "platform": "toutiao",
            "url": url,
            "title": title,
            "content": content,
            "word_count": len(content)
        }
