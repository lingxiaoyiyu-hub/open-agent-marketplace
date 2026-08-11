---
name: stepfun
description: 阶跃星辰 (StepFun) 多模态能力插件。提供语音合成 (TTS)、音色克隆、文生图、图像编辑以及视频理解的 CLI 指令、Python SDK 及 MCP 工具使用说明。
---

# 阶跃星辰 (StepFun) 插件技能指南

本技能为 AI 助手及用户提供阶跃星辰 (StepFun) 的语音、图像及视频处理能力支持。

## 环境变量配置

所有的接口请求走 Step Plan 专属路径 `https://api.stepfun.com/step_plan/v1`。
全局环境变量为 `STEPFUN_API_KEY`。

---

## 核心工具指令 (CLI)

套件已提供全局 `stepfun` 命令：

### 1. 语音合成 (TTS)
支持长文本自动切片与 `ffmpeg` 无缝合并：
```bash
stepfun tts --input "需要合成的文本内容" --output speech.mp3 --voice cixingnansheng --instruction "语气温柔，语速偏慢"
```

### 2. 音色克隆
- **试听 (preview)**（无需创建永久 `voice_id`）：
  ```bash
  stepfun clone-preview --audio "D:/voice/ref.mp3" --ref-text "参考音频文字" --sample-text "试听文本" --output preview.wav
  ```
- **正式注册 (clone-voice)**：
  ```bash
  stepfun clone-voice --audio "D:/voice/ref.mp3" --ref-text "参考音频文字"
  ```

### 3. 文生图与图像编辑
- **文生图**：
  ```bash
  stepfun image --prompt "赛博朋克风格都市夜景" --output generated.png --size 1024x1024
  ```
- **图像编辑**：
  ```bash
  stepfun image-edit --image input.png --prompt "将背景替换为星空" --output edited.png
  ```

### 4. 视频理解
```bash
stepfun video --video "https://example.com/video.mp4" --prompt "请概括视频主要内容"
```

---

## Python SDK 调用方式

```python
from stepfun import synthesize_speech, generate_image, edit_image, understand_video

# 1. TTS 语音合成
synthesize_speech("测试语音合成", output_path="speech.mp3")

# 2. 文生图
generate_image(prompt="水墨画风格江南水乡", output_path="jiangnan.png")
```

---

## MCP Server 服务

MCP 服务端可直接通过 `python -m stepfun.mcp_server` 启动，暴露以下 MCP 工具：
- `stepfun_tts`
- `stepfun_clone_preview`
- `stepfun_clone_voice`
- `stepfun_image_generate`
- `stepfun_image_edit`
- `stepfun_video_understand`
