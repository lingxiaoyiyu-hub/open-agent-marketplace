# Media Crawler All-in-One Plugin

全网自媒体爆文与多平台数据采集插件 (Multi-platform Social Media & News Viral Miner Plugin)。

统一整合了 **今日头条、微博、知乎、抖音、B站、小红书、快手** 等国内主流内容平台的数据采集、热榜雷达、爆款结构拆解与矩阵创作能力，完全兼容 `open-agent-marketplace` 插件标准与 MCP (Model Context Protocol) 协议。

---

## 🌟 核心特性

1. **跨平台实时热点雷达**：
   - 一键并发聚合今日头条 Top 50 热榜、微博热搜、知乎热榜、抖音热搜、B站全站排行榜。
2. **垂直领域爆文挖掘**：
   - 支持按关键词搜索各平台高赞、高评、高转发的 10w+ 爆款文章与图文笔记。
3. **爆款结构深度拆解 (AIDA+)**：
   - 自动提取“黄金 3 秒开头钩子”、情绪矛盾主线、争议站队设计与文末互动引导。
4. **爆款热度综合打分模型**：
   - 基于 `评论(5.0x) + 转发(3.5x) + 收藏(2.0x) + 点赞(1.0x)` 科学推算真实爆款量级。

---

## 🛠️ MCP 工具列表 (Tools)

| 工具名称 | 功能描述 | 参数说明 |
| :--- | :--- | :--- |
| `get_multi_platform_trending` | 批量并发获取全网主流平台实时热搜/热榜 | `platforms` (列表), `limit` (返回条数) |
| `search_viral_posts` | 在指定平台按关键词搜索高互动爆款文章/帖子 | `platform`, `keyword`, `limit` |
| `extract_post_details` | 解析提取单篇爆文的完整正文、字数与段落 | `platform`, `url` |
| `analyze_viral_structure` | 拆解爆文开头钩子、情绪触发词与互动点 | `title`, `content` |
| `calculate_viral_score` | 计算爆款综合热度指数 (HeatScore) 与评级 | `comments`, `likes`, `shares`, `collects` |

---

## 🎯 内置 Agent Skills

- **`media-viral-hunter`**：全网跨平台热点雷达与自媒体爆文挖掘。
- **`viral-content-creator`**：爆款文章结构拆解与多平台矩阵重构改写。
- **`creator-benchmark`**：竞品大V对标分析与账号体检。

---

## 🚀 安装与使用

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 在 AI 工具中配置 (MCP)
在 `claude_desktop_config.json` 或 Antigravity MCP 配置文件中添加：
```json
{
  "mcpServers": {
    "media-crawler": {
      "command": "python",
      "args": ["-u", "C:/Users/lingx/.gemini/config/plugins/media-crawler-plugin/mcp_server/server.py"],
      "env": {
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

### 3. 自然语言调用示例
- “*帮我查看今天头条和微博上前 10 的热搜，对比一下大家最关注什么*”
- “*在知乎和头条上搜一下关于‘民间故事’的高赞爆文，挑出 3 篇帮我拆解开头钩子*”
- “*根据这篇文章的评论量和点赞量，帮我计算它的爆款指数评级*”
