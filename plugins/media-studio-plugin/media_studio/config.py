import os

DEFAULT_API_KEY = os.getenv("STUDIO_API_KEY", "")
DEFAULT_BASE_URL = os.getenv("STUDIO_BASE_URL", "https://api.stepfun.com/v1")

class StudioConfig:
    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key or DEFAULT_API_KEY
        self.base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        
        if not self.api_key:
            raise ValueError("STUDIO_API_KEY is not set. Please set STUDIO_API_KEY environment variable or pass api_key parameter.")

    @property
    def headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
        }
