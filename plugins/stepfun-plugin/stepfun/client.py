import json
import urllib.request
import urllib.error
import uuid
from typing import Dict, Any, Union
from .config import StepFunConfig

class StepFunClient:
    def __init__(self, config: StepFunConfig = None):
        self.config = config or StepFunConfig()

    def get_json(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Perform a GET request and parse the JSON response."""
        import urllib.parse
        url = f"{self.config.base_url}{endpoint}"
        if params:
            url += "?" + urllib.parse.urlencode(params)
        headers = self.config.headers
        req = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(req) as resp:
                content = resp.read()
                return json.loads(content.decode("utf-8"))
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"StepFun API Request Failed [{e.code}]: {err_body}") from e
        except Exception as e:
            raise RuntimeError(f"StepFun API Request Error: {str(e)}") from e

    def post_json(self, endpoint: str, data: Dict[str, Any], raw_response: bool = False) -> Union[Dict[str, Any], bytes]:
        url = f"{self.config.base_url}{endpoint}"
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        
        headers = self.config.headers
        headers["Content-Type"] = "application/json"
        
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req) as resp:
                content = resp.read()
                if raw_response:
                    return content
                try:
                    return json.loads(content.decode("utf-8"))
                except Exception:
                    return content
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"StepFun API Request Failed [{e.code}]: {err_body}") from e
        except Exception as e:
            raise RuntimeError(f"StepFun API Request Error: {str(e)}") from e

    def post_multipart(self, endpoint: str, fields: Dict[str, str], files: Dict[str, tuple]) -> Dict[str, Any]:
        """
        files format: {"field_name": (filename, file_bytes, content_type)}
        """
        url = f"{self.config.base_url}{endpoint}"
        boundary = f"----WebKitFormBoundary{uuid.uuid4().hex}"
        
        body = []
        for key, val in fields.items():
            body.append(f"--{boundary}".encode("utf-8"))
            body.append(f'Content-Disposition: form-data; name="{key}"'.encode("utf-8"))
            body.append(b"")
            body.append(str(val).encode("utf-8"))
            
        for field_name, (filename, file_bytes, content_type) in files.items():
            body.append(f"--{boundary}".encode("utf-8"))
            body.append(f'Content-Disposition: form-data; name="{field_name}"; filename="{filename}"'.encode("utf-8"))
            body.append(f'Content-Type: {content_type}'.encode("utf-8"))
            body.append(b"")
            body.append(file_bytes)
            
        body.append(f"--{boundary}--".encode("utf-8"))
        body.append(b"")
        
        payload = b"\r\n".join(body)
        
        headers = self.config.headers
        headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
        
        req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(req) as resp:
                content = resp.read()
                return json.loads(content.decode("utf-8"))
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"StepFun API Multipart Request Failed [{e.code}]: {err_body}") from e
        except Exception as e:
            raise RuntimeError(f"StepFun API Multipart Error: {str(e)}") from e
