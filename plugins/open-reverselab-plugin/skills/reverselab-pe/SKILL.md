---
name: reverselab-pe
description: "Windows PE/ELF Reverse Engineering & Binary Analysis Protocol | Windows PE/ELF 二进制逆向工程技能。"
---

# Windows PE / Binary Reverse Engineering Protocol (PE 逆向分析工作流)

基于 open-reverselab 的 PE 分析标准作业程序 (SOP)。

---

## 🎯 核心原则

1. **查知识库**：分析前先检索插件 `kb/pe-reverse/` 知识库。
2. **证据导向**：不要凭空猜测，基于字符串、导入表、控制流和解密结果给出结论。
3. **优先自动化**：优先使用 `scripts/` 中的分析脚本进行初筛 (triage)。

---

## 🔄 5 步分析工作流 (Phase 1-5)

### Phase 1: 目标初筛 (Triage)
- 运行初筛检查，识别 PE 格式、位数 (32/64位)、编译器、时间戳与保护类型（UPX, Themida, VMP, PyInstaller 等）。
- 提取敏感 API（如 `VirtualProtect`, `IsDebuggerPresent`, `RegQueryValueEx`, `WinVerifyTrust`）。

### Phase 2: 静态分析 (Static Analysis)
- 结合 Ghidra / IDA 分析导出函数与主逻辑。
- 检索字符串与算法特征（如 AES S-box, RSA 常数, Base64 表）。

### Phase 3: 动态调试与 Hook (Dynamic Debugging)
- 使用 Frida 或 x64dbg 挂载目标。
- 拦截关键函数返回值或寄存器状态，提取解密后的 Payload。

### Phase 4: 密码学与逻辑还原 (Crypto & Logic Extraction)
- 提取秘钥、解密算法与验证流程。
- 生成伪代码或 Python 算法还原脚本。

### Phase 5: 报告生成 (Reporting)
- 输出完整的分析结论、关键函数偏移地址、IOC 与加固建议。
