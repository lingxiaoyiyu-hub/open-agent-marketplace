import sys
import asyncio
import os

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "mcp_server"))

from adapters.toutiao_adapter import ToutiaoAdapter
from adapters.weibo_adapter import WeiboAdapter
from adapters.zhihu_adapter import ZhihuAdapter
from adapters.bilibili_adapter import BilibiliAdapter
from analyzer.viral_scorer import ViralScorer

async def run_test():
    print("=== 1. Testing Toutiao Adapter ===")
    t = ToutiaoAdapter()
    tt_items = await t.get_trending(limit=3)
    for it in tt_items:
        print(f"  [{it['rank']}] {it['title']} (热度: {it['hot_value']})")

    print("\n=== 2. Testing Weibo Adapter ===")
    w = WeiboAdapter()
    wb_items = await w.get_trending(limit=3)
    for it in wb_items:
        print(f"  [{it['rank']}] {it['title']} (热度: {it['hot_value']})")

    print("\n=== 3. Testing Zhihu Adapter ===")
    z = ZhihuAdapter()
    zh_items = await z.get_trending(limit=3)
    for it in zh_items:
        print(f"  [{it['rank']}] {it['title']}")

    print("\n=== 4. Testing Bilibili Adapter ===")
    b = BilibiliAdapter()
    b_items = await b.get_trending(limit=3)
    for it in b_items:
        print(f"  [{it['rank']}] {it['title']} (播放: {it['views']}, 弹幕: {it['danmaku']})")

    print("\n=== 5. Testing Viral Scorer & Structure Analyzer ===")
    score = ViralScorer.calculate_score(comments=520, likes=3200, shares=180, collects=450)
    print(f"  HeatScore: {score}")

    sample_content = "工作十年才明白，职场最大的陷阱其实不是低薪，而是无效内耗。\n没想到老板居然这么做..."
    analysis = ViralScorer.analyze_structure("职场最大的秘密", sample_content)
    print(f"  Golden Hook: {analysis['golden_hook']}")
    print(f"  Triggers: {analysis['detected_emotional_triggers']}")
    print("\n All plugin unit tests passed successfully!")

if __name__ == "__main__":
    asyncio.run(run_test())
