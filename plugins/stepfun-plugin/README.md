# 阶跃星辰 (StepFun) 工具套件 & MCP Server

基于阶跃星辰 `Step Plan` 专属路径 (`https://api.stepfun.com/step_plan/v1`) 构建的完整工具套件，支持 **TTS 语音合成 (含长文本自动分段拼接)**、**音色克隆 (试听 & 正式)**、**文生图**、**图像编辑** 以及 **视频理解**。

支持 **CLI 命令行**、**Python SDK** 及 **MCP 服务 (Model Context Protocol)** 3 种使用形态。

---

## 1. 安装与环境变量配置

### 安装
在工具目录安装（开发模式）：
```bash
pip install -e .
```

### 环境变量设置
在终端或系统环境变量中配置 `STEPFUN_API_KEY`：
```powershell
# Windows PowerShell
$env:STEPFUN_API_KEY="你的Key"
# 或永久生效：
setx STEPFUN_API_KEY "你的Key"
```

---

## 2. CLI 命令行使用

### 2.1 语音合成 (TTS)
支持长文本自动切片拼接：
```bash
stepfun tts -i "阶跃星辰拥有强劲的多模态能力。今天的天气非常好，我们一起来体验语音合成与图像生成功能吧！" -o speech.mp3 -v cixingnansheng --instruction "语气温柔，语速偏慢"
```

### 2.2 音色克隆试听 (preview)
无需注册 `voice_id`，直接用 5~10 秒参考音频进行效果试听（保存为 wav）：
```bash
stepfun clone-preview -a "D:/voice/reference.mp3" -r "参考音频里说的原文" -s "试听新合成的这句话" -o preview.wav
```

### 2.3 音色克隆正式注册 (clone-voice)
注册专属音色并获取 `voice_id`：
```bash
stepfun clone-voice -a "D:/voice/reference.mp3" -r "参考音频里说的原文"
```

### 2.4 文生图 (image)
```bash
stepfun image -p "赛博朋克风格的都市夜景，霓虹灯光映照在湿漉漉的街道上" -o cyberpunk.png --size 1024x1024
```

### 2.5 图像编辑 (image-edit)
```bash
stepfun image-edit -i input.png -p "让图中的角色骑上一辆红色的自行车" -o output.png
```

### 2.6 视频理解 (video)
支持网络视频 URL 或本地 MP4 文件：
```bash
stepfun video -v "https://example.com/demo.mp4" -p "请详细概括视频中发生的事件"
```

---

## 3. Python SDK 调用

```python
from stepfun import synthesize_speech, generate_image, understand_video

# 1. TTS 语音合成
synthesize_speech(
    text="你好，这是通过 Python SDK 调用阶跃星辰 TTS 生成的语音。",
    output_path="sdk_tts.mp3",
    instruction="语气热情，语速适中"
)

# 2. 文生图
generate_image(
    prompt="一幅精美的江南水乡水墨画",
    output_path="jiangnan.png",
    size="1024x1024"
)

# 3. 视频理解
result = understand_video(
    video_input="D:/videos/test.mp4",
    prompt="说明视频的主题"
)
print(result)
```

---

## 4. MCP 服务端配置 (Cursor / Claude Code / Cline / Cherry Studio)

工具内内置了 FastMCP 服务端 `stepfun-mcp`。

### MCP JSON 配置文件

在 MCP 客户端配置文件 (如 `claude_desktop_config.json` 或 Cursor MCP 配置) 中添加：

```json
{
  "mcpServers": {
    "stepfun": {
      "command": "python",
      "args": ["-m", "stepfun.mcp_server"],
      "env": {
        "STEPFUN_API_KEY": "你的Key",
        "STEPFUN_BASE_URL": "https://api.stepfun.com/step_plan/v1"
      }
    }
  }
}
```

### 暴漏的 MCP 工具列表：
- `stepfun_tts`: 语音合成 (支持长文本分段)
- `stepfun_clone_preview`: 音色克隆试听
- `stepfun_clone_voice`: 音色正式克隆
- `stepfun_image_generate`: 文生图
- `stepfun_image_edit`: 图像编辑
- `stepfun_video_understand`: 视频理解
