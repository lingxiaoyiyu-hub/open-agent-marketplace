"""
Unified Async HTTP API Client with retry, dynamic user-agents, and robust error handling.
"""
import random
import asyncio
from typing import Dict, Any, Optional
import httpx

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
]

class APIClient:
    def __init__(self, timeout: float = 15.0):
        self.timeout = timeout

    def get_random_ua(self) -> str:
        return random.choice(USER_AGENTS)

    async def get_json(self, url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, retries: int = 2) -> Optional[Dict[str, Any]]:
        req_headers = {
            "User-Agent": self.get_random_ua(),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
        if headers:
            req_headers.update(headers)

        for attempt in range(retries + 1):
            try:
                async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                    resp = await client.get(url, headers=req_headers, params=params)
                    if resp.status_code == 200:
                        return resp.json()
            except Exception:
                if attempt == retries:
                    return None
                await asyncio.sleep(0.5 * (attempt + 1))
        return None

    async def get_text(self, url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None) -> Optional[str]:
        req_headers = {
            "User-Agent": self.get_random_ua(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
        if headers:
            req_headers.update(headers)
        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                resp = await client.get(url, headers=req_headers, params=params)
                if resp.status_code == 200:
                    return resp.text
        except Exception:
            return None
        return None
