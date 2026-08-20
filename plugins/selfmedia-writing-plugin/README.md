# SelfMedia Writing Plugin

自媒体中文写作去 AI 味与二创改写套件。把 AI 辅助写的稿子改得像真人写的,并支持把已有内容改写成新的原创表达。

适配平台:公众号、头条号、百家号、小红书等。

## 包含的 skill

| Skill | 触发场景 | 职责 |
|---|---|---|
| `remove-ai-flavor` | 去 AI 味 / 不像人写 / 模板腔 / 翻译腔 | 识别并改写 AI 痕迹:二元对比壳、序列壳、本质宣称、助手套话、假互动结尾等 |
| `rewrite-paraphrase` | 二创 / 改写 / 降重 / 查重率太高 | 24 类 AI 痕迹评分 + 轻/中/深三级改写强度,输出诊断报告 |

## 使用

安装后,直接说:

- 「帮我把这篇稿子去一下 AI 味」
- 「这段太像机器人写的,改得像人写」
- 「把这篇做成二创,降一下查重」

skill 会根据自然语言自动触发。

## 来源与许可

本插件为整合改编作品,整合自以下开源项目:

- [op7418/Humanizer-zh](https://github.com/op7418/humanizer-zh) — 基于 Wikipedia: Signs of AI writing
- [B1lli/remove-ai-flavor-writing-skill](https://github.com/B1lli/remove-ai-flavor-writing-skill)
- [1-SKILL/shuorenhua](https://github.com/1-SKILL/shuorenhua)(说人话)

本插件以 MIT 许可发布。各上游项目的原始许可与版权声明归其原作者所有;使用前请遵守各上游项目的许可条款。

> 声明:本插件是文风优化工具,帮助改善 AI 生成文本的自然度并辅助合法改写,不鼓励学术不端或抄袭规避。
