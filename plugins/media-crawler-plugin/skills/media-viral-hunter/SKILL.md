---
name: media-viral-hunter
description: 全网跨平台热点雷达与自媒体爆文挖掘协议 | Multi-platform Viral & Trending Hunter Protocol
---

# Media Viral Hunter | 全网热点与爆文挖掘协议

本技能为 Agent 提供全网跨平台实时热点聚合、垂直赛道高潜爆发内容嗅探与多维度互动量加权打分能力。

## 适用平台
- **今日头条**：官方 Top 50 热榜、垂直频道（`news_story`, `news_emotion`, `news_history` 等）高互动流
- **微博**：实时全网热搜榜、文娱榜、要闻榜
- **知乎**：知乎热榜、高赞回答、热点圆桌
- **抖音 / 快手**：实时上升热点、热搜短视频文案
- **B站 (Bilibili)**：全站热门、各分区排行榜
- **百度**：实时热搜榜、热点事件追踪

## 核心工作流

### 1. 跨平台热点对比与同温层发现
当用户需要寻找选题时：
1. 调用 `get_multi_platform_trending` 获取头条、微博、知乎、抖音等平台 Top 榜单。
2. 跨平台对比共现热点（在 3 个以上平台同时上榜的通常属于**全网级超级母题**）。
3. 提炼各平台用户情绪画像（例如知乎偏理性分析、头条偏社会共鸣、小红书偏生活方式与情绪消费）。

### 2. 垂直赛道隐形爆款挖掘
当用户需要寻找非热搜的长尾爆文（如情感故事、民间怪谈、生活窍门）：
1. 调用 `search_viral_posts`，输入关键词并指定按 `likes`（点赞）或 `comments`（评论）降序排列。
2. 应用加权热度公式过滤：
   $$\text{HeatScore} = \text{Comments} \times 5.0 + \text{Likes} \times 1.0 + \text{Shares} \times 3.0$$
3. 输出格式化的爆款列表，包含：标题、平台、发布时间、互动数据、核心观点提要。
