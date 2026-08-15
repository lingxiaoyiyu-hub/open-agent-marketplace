---
name: media-studio
description: "Media Studio 多模态媒体创作套件 (TTS、音色克隆、ASR、字幕、媒体剪辑、生图、视频理解) | 供应商无关的媒体创作能力插件。"
---

# Media Studio 插件技能指南

本技能为 AI 助手及用户提供媒体创作能力：语音合成 (TTS)、音色克隆、语音转写 (ASR)、字幕、视频混剪/粗剪/转码、文生图、图像编辑与视频理解。

## 环境变量配置

- `STUDIO_API_KEY`：语音/图像/视频服务的 API Key（必填）。
- `STUDIO_BASE_URL`：默认 `https://api.stepfun.com/v1`（当前默认后端为阶跃星辰）。
- `FFMPEG_PATH` / `FFPROBE_PATH`：可选，指定 ffmpeg/ffprobe 完整路径；默认使用 PATH 中的 `ffmpeg` / `ffprobe`。

> 说明：插件命名与工具前缀已与供应商解耦，后续更换其它供应商只需替换后端实现与 key。

---

## 能力总览

| 类别 | 能力 | MCP 工具 |
| :--- | :--- | :--- |
| 语音合成 | 文字转配音（长文本自动切片+合并） | `voice_tts` |
| 音色 | 官方音色列表 / 克隆试听 / 复刻音色 | `voice_list` / `voice_clone_preview` / `voice_clone_voice` |
| 语音识别 | 音频/视频转文字（ASR） | `voice_transcribe` |
| 字幕 | 文字转 SRT / 一键自动加字幕 / 烧录字幕 | `subtitle_make` / `subtitle_auto` / `media_add_subtitle` |
| 剪辑 | 视频混剪 / 视频粗剪 / 转码 / 合并 / 裁剪 | `media_mixcut` / `media_roughcut` / `media_convert` / `media_merge` / `media_trim` |
| 音频 | 提取音频 / 配音合成到视频 | `media_extract_audio` / `media_mux_audio` |
| 画面 | 提取画面/截图 / 媒体信息 | `media_extract_frames` / `media_info` |
| 图像 | 文生图 / 图像编辑 | `image_generate` / `image_edit` |
| 视频 | 视频内容理解 | `video_understand` |

---

## 典型工作流

### 1. 文案配音
```
media-studio tts --input "需要合成的文案" --output voice.mp3 --voice cixingnansheng --instruction "语气温柔，语速偏慢"
```
MCP 工具：`voice_tts(text, output_path, voice, instruction, ...)`。

### 2. 音频/视频转文字
```
media-studio asr --input video.mp4
```
MCP 工具：`voice_transcribe(file_path, model="stepaudio-2.5-asr")`（视频输入会自动先提音频）。

### 3. 一键自动加字幕
```
media-studio auto-subtitle --video input.mp4 --output output.mp4
```
MCP 工具：`subtitle_auto(video_path, output_path)` —— 内部自动完成「转写 → 生成 SRT → 烧录」。

### 4. 视频混剪
```
media-studio mixcut --inputs a.mp4 b.mp4 c.mp4 --output mix.mp4 --duration 30 --transition --bgm music.mp3
```
MCP 工具：`media_mixcut(inputs, output_path, duration, segment, transition, voiceover, bgm, subtitle, ...)`。

### 5. 视频粗剪（去停顿）
```
media-studio roughcut --input talk.mp4 --output clean.mp4 --threshold -35dB --min-silence 0.4
```

### 6. 配音 + 合成到视频
```
media-studio tts --input "口播文案" --output voice.mp3
media-studio mux-audio --video footage.mp4 --audio voice.mp3 --output final.mp4
```

---

## MCP Server 服务

MCP 服务端通过 `python -m media_studio.mcp_server` 启动，暴露以下工具：

语音：`voice_tts` · `voice_list` · `voice_clone_preview` · `voice_clone_voice`
转写/字幕：`voice_transcribe` · `subtitle_make` · `subtitle_auto`
媒体剪辑：`media_info` · `media_add_subtitle` · `media_mixcut` · `media_roughcut` · `media_convert` · `media_merge` · `media_trim` · `media_extract_audio` · `media_extract_frames` · `media_mux_audio`
图像：`image_generate` · `image_edit`
视频：`video_understand`

---

## 前置依赖说明

- 语音/图像/视频能力需要 `STUDIO_API_KEY`（联网）。
- 本地媒体剪辑需要系统安装 `ffmpeg`（及 `ffprobe`），或通过 `FFMPEG_PATH` / `FFPROBE_PATH` 指向二进制。
- 烧录中文字幕建议使用 `Microsoft YaHei`（微软雅黑）或 `SimHei`（黑体）字体。
