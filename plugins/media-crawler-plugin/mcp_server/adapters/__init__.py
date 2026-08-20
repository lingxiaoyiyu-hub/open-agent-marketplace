"""
Multi-platform Adapters for Media Crawler MCP Server.
"""
from .toutiao_adapter import ToutiaoAdapter
from .weibo_adapter import WeiboAdapter
from .zhihu_adapter import ZhihuAdapter
from .bilibili_adapter import BilibiliAdapter
from .xhs_adapter import XhsAdapter
from .douyin_adapter import DouyinAdapter

__all__ = [
    "ToutiaoAdapter",
    "WeiboAdapter",
    "ZhihuAdapter",
    "BilibiliAdapter",
    "XhsAdapter",
    "DouyinAdapter",
]
