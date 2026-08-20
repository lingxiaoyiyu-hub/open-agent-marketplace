"""
哔哩哔哩 (Bilibili) Data Adapter.
Supports: Bilibili Popular/Trending list and video/column search.
"""
from typing import List, Dict, Any, Optional
import urllib.parse
import re
try:
    from ..core.api_client import APIClient
except (ImportError, ValueError):
    from core.api_client import APIClient

class BilibiliAdapter:
    def __init__(self, api_client: Optional[APIClient] = None):
        self.client = api_client or APIClient()

    async def get_trending(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch Bilibili real-time popular videos/ranking."""
        url = "https://api.bilibili.com/x/web-interface/popular?ps=50&pn=1"
        res = await self.client.get_json(url)
        items = []
        if res and "data" in res and "list" in res["data"]:
            for i, raw in enumerate(res["data"]["list"][:limit], 1):
                stat = raw.get("stat", {})
                items.append({
                    "rank": i,
                    "platform": "bilibili",
                    "title": raw.get("title", ""),
                    "author": raw.get("owner", {}).get("name", ""),
                    "views": stat.get("view", 0),
                    "likes": stat.get("like", 0),
                    "danmaku": stat.get("danmaku", 0),
                    "comments": stat.get("reply", 0),
                    "url": f"https://www.bilibili.com/video/{raw.get('bvid', '')}",
                    "cover_image": raw.get("pic", "")
                })
        return items

    async def search_posts(self, keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search Bilibili videos/articles."""
        url = f"https://api.bilibili.com/x/web-interface/search/type?keyword={urllib.parse.quote(keyword)}&search_type=video&page=1&page_size={limit}&order=click"
        res = await self.client.get_json(url)
        results = []
        if res and "data" in res and "result" in res["data"]:
            for item in res["data"]["result"][:limit]:
                clean_title = re.sub(r'<[^>]+>', '', item.get("title", ""))
                results.append({
                    "platform": "bilibili",
                    "title": clean_title,
                    "author": item.get("author", ""),
                    "description": item.get("description", ""),
                    "views": item.get("play", 0),
                    "likes": item.get("favorites", 0),
                    "comments": item.get("review", 0),
                    "url": f"https://www.bilibili.com/video/{item.get('bvid', '')}"
                })
        return results
