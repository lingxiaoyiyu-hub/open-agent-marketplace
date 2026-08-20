"""
Media Crawler Multi-Platform MCP Server.
Provides standardized tools for fetching viral content, hot search trends, and analyzing content structure.
"""
import sys
import asyncio
from typing import List, Dict, Any, Optional

# Ensure utf-8 encoding on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from fastmcp import FastMCP

from adapters.toutiao_adapter import ToutiaoAdapter
from adapters.weibo_adapter import WeiboAdapter
from adapters.zhihu_adapter import ZhihuAdapter
from adapters.bilibili_adapter import BilibiliAdapter
from adapters.xhs_adapter import XhsAdapter
from adapters.douyin_adapter import DouyinAdapter
from analyzer.viral_scorer import ViralScorer

mcp = FastMCP("media-crawler-plugin", dependencies=["httpx", "beautifulsoup4", "pydantic"])

# Initialize adapters
toutiao = ToutiaoAdapter()
weibo = WeiboAdapter()
zhihu = ZhihuAdapter()
bilibili = BilibiliAdapter()
xhs = XhsAdapter()
douyin = DouyinAdapter()

@mcp.tool()
async def get_multi_platform_trending(platforms: Optional[List[str]] = None, limit: int = 15) -> Dict[str, Any]:
    """
    Fetch real-time hot trending lists from multiple platforms simultaneously.
    Supported platforms: 'toutiao' (今日头条), 'weibo' (微博), 'zhihu' (知乎), 'douyin' (抖音), 'bilibili' (B站).
    """
    target_platforms = platforms or ["toutiao", "weibo", "zhihu", "douyin", "bilibili"]
    tasks = {}

    if "toutiao" in target_platforms:
        tasks["toutiao"] = toutiao.get_trending(limit)
    if "weibo" in target_platforms:
        tasks["weibo"] = weibo.get_trending(limit)
    if "zhihu" in target_platforms:
        tasks["zhihu"] = zhihu.get_trending(limit)
    if "douyin" in target_platforms:
        tasks["douyin"] = douyin.get_trending(limit)
    if "bilibili" in target_platforms:
        tasks["bilibili"] = bilibili.get_trending(limit)

    results = {}
    for name, coro in tasks.items():
        try:
            results[name] = await coro
        except Exception as e:
            results[name] = {"error": str(e)}

    return {
        "status": "success",
        "platforms_count": len(results),
        "data": results
    }

@mcp.tool()
async def search_viral_posts(platform: str, keyword: str, limit: int = 15) -> Dict[str, Any]:
    """
    Search for viral posts and high-engagement content by keyword on a specific platform.
    Platform options: 'toutiao', 'weibo', 'zhihu', 'bilibili', 'xiaohongshu'.
    """
    platform = platform.lower().strip()
    try:
        if platform in ["toutiao", "今日头条", "头条"]:
            data = await toutiao.search_articles(keyword, limit)
        elif platform in ["weibo", "微博"]:
            data = await weibo.search_posts(keyword, limit)
        elif platform in ["zhihu", "知乎"]:
            data = await zhihu.search_posts(keyword, limit)
        elif platform in ["bilibili", "b站", "哔哩哔哩"]:
            data = await bilibili.search_posts(keyword, limit)
        elif platform in ["xhs", "xiaohongshu", "小红书"]:
            data = await xhs.search_notes(keyword, limit=limit)
        else:
            return {"status": "error", "message": f"Unsupported platform '{platform}'. Choose from toutiao, weibo, zhihu, bilibili, xiaohongshu."}

        return {
            "status": "success",
            "platform": platform,
            "keyword": keyword,
            "count": len(data),
            "results": data
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
async def extract_post_details(platform: str, url: str) -> Dict[str, Any]:
    """
    Extract the full text content, word count, and details of a specific article or post.
    """
    platform = platform.lower().strip()
    try:
        if platform in ["toutiao", "今日头条", "头条"]:
            res = await toutiao.extract_article(url)
        elif platform in ["xhs", "xiaohongshu", "小红书"]:
            res = await xhs.extract_note(url)
        else:
            # Generic extraction fallback
            from core.api_client import APIClient
            import re
            client = APIClient()
            html = await client.get_text(url)
            if html:
                title_match = re.search(r'<title>([\s\S]*?)</title>', html, re.I)
                clean_title = title_match.group(1).strip() if title_match else ""
                clean_text = re.sub(r'<[^>]+>', ' ', html)
                clean_text = re.sub(r'\s+', ' ', clean_text)[:3000].strip()
                res = {"platform": platform, "url": url, "title": clean_title, "content": clean_text, "word_count": len(clean_text)}
            else:
                res = {"error": "Failed to retrieve page"}
        return {"status": "success", "data": res}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def analyze_viral_structure(title: str, content: str) -> Dict[str, Any]:
    """
    Analyze the viral structure of an article: golden hook (3-second hook), emotional tension triggers, reading time, and CTA questions.
    """
    return ViralScorer.analyze_structure(title, content)

@mcp.tool()
def calculate_viral_score(comments: int = 0, likes: int = 0, shares: int = 0, collects: int = 0) -> Dict[str, Any]:
    """
    Calculate the weighted viral heat score (HeatScore) based on engagement metrics.
    """
    score = ViralScorer.calculate_score(comments, likes, shares, collects)
    grade = "S (超级爆款)" if score >= 5000 else "A (高潜爆款)" if score >= 1000 else "B (常规热门)" if score >= 300 else "C (普通作品)"
    return {
        "score": score,
        "grade": grade,
        "breakdown": {
            "comments_weight": comments * 5.0,
            "shares_weight": shares * 3.5,
            "collects_weight": collects * 2.0,
            "likes_weight": likes * 1.0
        }
    }

if __name__ == "__main__":
    mcp.run()
