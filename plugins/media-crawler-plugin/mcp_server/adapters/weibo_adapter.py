"""
微博 (Weibo) Data Adapter.
Supports: Real-time hot search ranking and keyword post search.
"""
from typing import List, Dict, Any, Optional
import urllib.parse
import re
try:
    from ..core.api_client import APIClient
except (ImportError, ValueError):
    from core.api_client import APIClient

class WeiboAdapter:
    def __init__(self, api_client: Optional[APIClient] = None):
        self.client = api_client or APIClient()

    async def get_trending(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch real-time Weibo hot search list."""
        url = "https://weibo.com/ajax/side/hotSearch"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Referer": "https://weibo.com/"
        }
        res = await self.client.get_json(url, headers=headers)
        items = []
        if res and "data" in res and "realtime" in res["data"]:
            for i, raw in enumerate(res["data"]["realtime"][:limit], 1):
                word = raw.get("word", "") or raw.get("note", "")
                items.append({
                    "rank": i,
                    "platform": "weibo",
                    "title": word,
                    "hot_value": raw.get("num", 0),
                    "label": raw.get("label_name", "") or raw.get("category", ""),
                    "url": f"https://s.weibo.com/weibo?q={urllib.parse.quote(word)}"
                })
        return items

    async def search_posts(self, keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search Weibo posts via open JSON search API."""
        encoded = urllib.parse.quote(keyword)
        url = f"https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D1%26q%3D{encoded}&page_type=searchall"
        res = await self.client.get_json(url)
        posts = []
        if res and "data" in res and "cards" in res["data"]:
            for card in res["data"]["cards"]:
                mblog = card.get("mblog")
                if mblog:
                    raw_text = mblog.get("text", "")
                    clean_text = re.sub(r'<[^>]+>', '', raw_text).strip()
                    posts.append({
                        "platform": "weibo",
                        "title": clean_text[:60] + "..." if len(clean_text) > 60 else clean_text,
                        "content": clean_text,
                        "author": mblog.get("user", {}).get("screen_name", ""),
                        "likes": mblog.get("attitudes_count", 0),
                        "comments": mblog.get("comments_count", 0),
                        "reposts": mblog.get("reposts_count", 0),
                        "publish_time": mblog.get("created_at", ""),
                        "url": f"https://m.weibo.cn/detail/{mblog.get('id', '')}"
                    })
        return posts[:limit]
