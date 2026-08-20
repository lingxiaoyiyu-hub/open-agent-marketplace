"""
Cookie storage and persistence for multi-platform crawlers.
"""
import os
import json
from typing import Dict, Any, Optional

COOKIE_DIR = os.path.expanduser("~/.media_crawler_cookies")

class CookieManager:
    def __init__(self, storage_dir: str = COOKIE_DIR):
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)

    def _get_cookie_file(self, platform: str) -> str:
        return os.path.join(self.storage_dir, f"{platform}_cookies.json")

    def save_cookies(self, platform: str, cookies: Dict[str, Any]) -> None:
        filepath = self._get_cookie_file(platform)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(cookies, f, ensure_ascii=False, indent=2)

    def load_cookies(self, platform: str) -> Optional[Dict[str, Any]]:
        filepath = self._get_cookie_file(platform)
        if os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return None
        return None

    def get_cookie_string(self, platform: str) -> str:
        cookies = self.load_cookies(platform)
        if not cookies:
            return ""
        if isinstance(cookies, dict):
            return "; ".join([f"{k}={v}" for k, v in cookies.items()])
        elif isinstance(cookies, list):
            return "; ".join([f"{c.get('name')}={c.get('value')}" for c in cookies if 'name' in c and 'value' in c])
        return ""
