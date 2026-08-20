"""
知乎 (Zhihu) Data Adapter.
Supports: Zhihu Topstory Hot List and Question/Answer extraction.
"""
from typing import List, Dict, Any, Optional
import urllib.parse
import re
try:
    from ..core.api_client import APIClient
except (ImportError, ValueError):
    from core.api_client import APIClient

class ZhihuAdapter:
    def __init__(self, api_client: Optional[APIClient] = None):
        self.client = api_client or APIClient()

    async def get_trending(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch real-time Zhihu hot list via verified endpoint."""
        url = f"https://api.zhihu.com/topstory/hot-list?limit={limit}&reverse_order=0"
        headers = {
            "User-Agent": "Futureve/6.23.0 Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
        }
        res = await self.client.get_json(url, headers=headers)
        items = []
        if res and "data" in res:
            for i, raw in enumerate(res["data"][:limit], 1):
                target = raw.get("target", {})
                title = target.get("title", "")
                detail_text = raw.get("detail_text", "")
                items.append({
                    "rank": i,
                    "platform": "zhihu",
                    "title": title,
                    "hot_value": detail_text,
                    "excerpt": target.get("excerpt", ""),
                    "answer_count": target.get("answer_count", 0),
                    "url": f"https://www.zhihu.com/question/{target.get('id', '')}"
                })
        return items

    async def search_posts(self, keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search Zhihu content via search API."""
        url = f"https://api.zhihu.com/search_v3?t=general&q={urllib.parse.quote(keyword)}&correction=1&offset=0&limit={limit}"
        res = await self.client.get_json(url)
        results = []
        if res and "data" in res:
            for item in res["data"]:
                obj = item.get("object", {})
                if obj and "title" in obj:
                    excerpt = re.sub(r'<[^>]+>', '', obj.get("excerpt", "")).strip()
                    results.append({
                        "platform": "zhihu",
                        "title": re.sub(r'<[^>]+>', '', obj.get("title", "")),
                        "author": obj.get("author", {}).get("name", ""),
                        "content": excerpt,
                        "likes": obj.get("voteup_count", 0),
                        "comments": obj.get("comment_count", 0),
                        "url": obj.get("url", "").replace("api.zhihu.com", "www.zhihu.com")
                    })
        return results[:limit]
