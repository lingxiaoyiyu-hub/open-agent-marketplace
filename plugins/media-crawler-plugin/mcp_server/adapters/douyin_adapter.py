"""
抖音 (Douyin) Data Adapter.
Supports: Hot trending search and video script extraction.
"""
from typing import List, Dict, Any, Optional
import urllib.parse
try:
    from ..core.api_client import APIClient
except (ImportError, ValueError):
    from core.api_client import APIClient

class DouyinAdapter:
    def __init__(self, api_client: Optional[APIClient] = None):
        self.client = api_client or APIClient()

    async def get_trending(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch Douyin billboard hot search list."""
        url = "https://www.iesdouyin.com/web/api/v2/hotsearch/billboard/word/"
        res = await self.client.get_json(url)
        items = []
        if res and "word_list" in res:
            for i, raw in enumerate(res["word_list"][:limit], 1):
                word = raw.get("word", "")
                items.append({
                    "rank": i,
                    "platform": "douyin",
                    "title": word,
                    "hot_value": raw.get("hot_value", 0),
                    "label": raw.get("label", ""),
                    "url": f"https://www.douyin.com/search/{urllib.parse.quote(word)}"
                })
        return items
