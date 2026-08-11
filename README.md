# Antigravity Custom Plugins (自定义插件市场)

这是一个整理集成的 Antigravity / AGY 个人自定义插件仓库。您可以将此仓库添加到 Antigravity IDE 的“插件市场”中，一键导入和使用所有技能与 MCP 服务。

## 📦 包含插件列表

| 插件名称 | 包含技能 (Skills) | 说明 |
| :--- | :--- | :--- |
| **`stepfun-plugin`** | `stepfun` | 阶跃星辰 (StepFun) 多模态能力插件（语音合成 TTS、音色克隆、文生图、图像编辑、视频理解）。 |
| **`redteam-hardening-plugin`** | `redteam-hook` | 软件黑盒逆向、Hook 攻击还原与蓝队防破解加固插件。 |
| **`open-reverselab-plugin`** | `reverselab-apk`<br>`reverselab-ctf`<br>`reverselab-pe` | Agent-native 逆向工程实验室插件（包含 PE 逆向、APK 分析、CTF 答题与密码学分析）。 |

---

## 🚀 如何在 Antigravity 中添加此插件市场

1. 打开 **Antigravity IDE** 设置 / 插件界面。
2. 点击 **“添加插件市场”** 按钮。
3. 在弹出的输入框中填入本仓库地址：
   ```text
   https://github.com/lingxiaoyiyu-hub/antigravity-custom-plugins
   ```
4. 点击 **“+ 添加插件市场”** 按钮，即可自动下载并导入包含的所有自定义插件。

---

## ⚠️ 配置指南

### StepFun 插件 Key 配置
`stepfun-plugin` 已进行安全脱敏处理。在运行 StepFun 语音合成或图像生成前，请在系统环境变量中设置您的 API Key：

- **Windows PowerShell**:
  ```powershell
  $env:STEPFUN_API_KEY="your_actual_stepfun_api_key"
  ```
- **Linux / macOS**:
  ```bash
  export STEPFUN_API_KEY="your_actual_stepfun_api_key"
  ```
