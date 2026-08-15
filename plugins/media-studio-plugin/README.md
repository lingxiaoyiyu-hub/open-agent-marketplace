# Media Studio — 多模态媒体创作套件 & MCP Server

供应商无关的多模态媒体创作套件，支持 **TTS 语音合成（长文本自动分段拼接）**、**音色克隆（试听 & 正式）**、**语音转写 (ASR)**、**字幕生成/烧录/一键自动加字幕**、**视频混剪/粗剪/转码/合并/裁剪/提音轨/提画面**、**文生图**、**图像编辑** 与 **视频理解**。

支持 **CLI 命令行**、**Python SDK** 及 **MCP 服务 (Model Context Protocol)** 3 种使用形态。

> 当前语音/图像/视频后端默认指向阶跃星辰 (StepFun)。插件命名与工具前缀已与供应商解耦；后续换供应商时改 `STUDIO_BASE_URL` 与 `STUDIO_API_KEY` 即可（不同供应商接口格式可能不同，需同步替换后端实现）。

---

## 1. 安装与环境变量配置

### 安装
```bash
pip install -e .
```

### 环境变量
```powershell
# Windows PowerShell
$env:STUDIO_API_KEY="你的Key"
setx STUDIO_API_KEY "你的Key"          # 永久生效
$env:FFMPEG_PATH="C:/path/to/ffmpeg.exe"  # 可选，媒体剪辑用
```

---

## 2. CLI 使用

```bash
media-studio tts -i "需要合成的文案" -o speech.mp3 -v cixingnansheng --instruction "语气温柔"
media-studio asr -i video.mp4
media-studio auto-subtitle --video input.mp4 --output output.mp4
media-studio mixcut --inputs a.mp4 b.mp4 --output mix.mp4 --duration 30 --transition
media-studio roughcut --input talk.mp4 --output clean.mp4
media-studio image -p "赛博朋克都市夜景" -o cyberpunk.png --size 1024x1024
media-studio video -v "https://example.com/demo.mp4" -p "请概括视频内容"
```

---

## 3. Python SDK 调用

```python
from media_studio import synthesize_speech, transcribe_audio, generate_image

synthesize_speech(text="你好，这是语音合成测试", output_path="sdk_tts.mp3")
generate_image(prompt="一幅江南水乡水墨画", output_path="jiangnan.png", size="1024x1024")
```

---

## 4. MCP 服务端配置

```json
{
  "mcpServers": {
    "media-studio": {
      "command": "python",
      "args": ["-m", "media_studio.mcp_server"],
      "env": {
        "STUDIO_API_KEY": "你的Key",
        "STUDIO_BASE_URL": "https://api.stepfun.com/v1"
      }
    }
  }
}
```

### MCP 工具列表
- 语音：`voice_tts` · `voice_list` · `voice_clone_preview` · `voice_clone_voice` · `voice_transcribe`
- 字幕：`subtitle_make` · `subtitle_auto` · `media_add_subtitle`
- 剪辑：`media_mixcut` · `media_roughcut` · `media_convert` · `media_merge` · `media_trim` · `media_extract_audio` · `media_extract_frames` · `media_mux_audio` · `media_info`
- 图像：`image_generate` · `image_edit`
- 视频：`video_understand`
