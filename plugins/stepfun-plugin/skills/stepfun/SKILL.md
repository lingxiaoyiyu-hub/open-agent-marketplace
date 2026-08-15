---
name: stepfun
description: "StepFun Multimodal AI Suite (TTS, Voice Clone, ASR, Subtitle, Media Editing, Image Gen, Video) | 阶跃星辰 (StepFun) 多模态能力插件。"
---

# 阶跃星辰 (StepFun) 插件技能指南

本技能为 AI 助手及用户提供阶跃星辰 (StepFun) 的语音、图像、视频能力，以及基于 ffmpeg 的本地媒体剪辑能力（加字幕 / 混剪 / 粗剪 / 转码等）。

## 环境变量配置

- `STEPFUN_API_KEY`：StepFun 平台 API Key（必填）。
- `STEPFUN_BASE_URL`：默认 `https://api.stepfun.com/v1`（一般无需修改）。
- `FFMPEG_PATH` / `FFPROBE_PATH`：可选，指定 ffmpeg/ffprobe 的完整路径；默认使用 PATH 中的 `ffmpeg` / `ffprobe`。

---

## 能力总览

| 类别 | 能力 | MCP 工具 |
| :--- | :--- | :--- |
| 语音合成 | 文字转配音（长文本自动切片+合并） | `stepfun_tts` |
| 音色 | 官方音色列表 / 克隆试听 / 复刻音色 | `stepfun_list_voices` / `stepfun_clone_preview` / `stepfun_clone_voice` |
| 语音识别 | 音频/视频转文字（ASR） | `stepfun_transcribe` |
| 字幕 | 文字转 SRT / 一键自动加字幕 / 烧录字幕 | `stepfun_make_srt` / `stepfun_auto_subtitle` / `media_add_subtitle` |
| 剪辑 | 视频混剪 / 视频粗剪 / 转码 / 合并 / 裁剪 | `media_mixcut` / `media_roughcut` / `media_convert` / `media_merge` / `media_trim` |
| 音频 | 提取音频 / 配音合成到视频 | `media_extract_audio` / `media_mux_audio` |
| 画面 | 提取画面/截图 / 媒体信息 | `media_extract_frames` / `media_info` |
| 图像 | 文生图 / 图像编辑 | `stepfun_image_generate` / `stepfun_image_edit` |
| 视频 | 视频内容理解 | `stepfun_video_understand` |

---

## 典型工作流（对齐"逆象"那套创作流程）

### 1. 文案配音
```
stepfun tts --input "需要合成的文案" --output voice.mp3 --voice cixingnansheng --instruction "语气温柔，语速偏慢"
```
MCP 工具：`stepfun_tts(text, output_path, voice, instruction, ...)`。

### 2. 音频/视频转文字
```
stepfun asr --input video.mp4
```
MCP 工具：`stepfun_transcribe(file_path, model="stepaudio-2.5-asr")`（视频输入会自动先提音频）。

### 3. 一键自动加字幕
```
stepfun auto-subtitle --video input.mp4 --output output.mp4
```
MCP 工具：`stepfun_auto_subtitle(video_path, output_path)` —— 内部自动完成「转写 → 生成 SRT → 烧录」。

手动分步：
1. `stepfun asr --input video.mp4` 拿到文本
2. `stepfun srt --text "..." --output sub.srt --duration 60`
3. `stepfun add-subtitle --video input.mp4 --srt sub.srt --output out.mp4`

### 4. 视频混剪
```
stepfun mixcut --inputs a.mp4 b.mp4 c.mp4 --output mix.mp4 --duration 30 --transition --bgm music.mp3
```
MCP 工具：`media_mixcut(inputs, output_path, duration, segment, transition, voiceover, bgm, subtitle, ...)`。

### 5. 视频粗剪（去停顿）
```
stepfun roughcut --input talk.mp4 --output clean.mp4 --threshold -35dB --min-silence 0.4
```
MCP 工具：`media_roughcut(input_path, output_path, threshold, min_silence)`。

### 6. 配音 + 合成到视频
```
stepfun tts --input "口播文案" --output voice.mp3
stepfun mux-audio --video footage.mp4 --audio voice.mp3 --output final.mp4
```

---

## MCP Server 服务

MCP 服务端通过 `python -m stepfun.mcp_server` 启动，暴露以下工具：

语音：`stepfun_tts` · `stepfun_list_voices` · `stepfun_clone_preview` · `stepfun_clone_voice`
转写/字幕：`stepfun_transcribe` · `stepfun_make_srt` · `stepfun_auto_subtitle`
媒体剪辑：`media_info` · `media_add_subtitle` · `media_mixcut` · `media_roughcut` · `media_convert` · `media_merge` · `media_trim` · `media_extract_audio` · `media_extract_frames` · `media_mux_audio`
图像：`stepfun_image_generate` · `stepfun_image_edit`
视频：`stepfun_video_understand`

---

## 前置依赖说明

- 语音/图像/视频能力需要 `STEPFUN_API_KEY`（联网）。
- 本地媒体剪辑需要系统安装 `ffmpeg`（及 `ffprobe`），或通过 `FFMPEG_PATH` / `FFPROBE_PATH` 指向二进制。
- 烧录中文字幕建议使用 `Microsoft YaHei`（微软雅黑）或 `SimHei`（黑体）字体。
