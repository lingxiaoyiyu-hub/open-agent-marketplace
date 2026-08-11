---
name: reverselab-ctf
description: "CTF Competition & Crackme Automated Solving Protocol | CTF 竞赛与 Crackme 自动化解题技能。"
---

# CTF & Crackme Reverse Engineering Protocol (CTF 竞赛解题工作流)

基于 open-reverselab 的 CTF 自动化分析标准。

---

## 🎯 核心原则

1. **按信号查知识库**：发现特征（如 JWT、SQLi、SM4、Z3、PRNG、OLLVM 混淆）时，自动检索 `kb/ctf-website/` 和 `kb/general/`。
2. **算法重现优先**：用 Python 编写可直接运行的求解/解密脚本，计算目标 Flag。

---

## 🔄 3 步解题流程

### Phase 1: 题目特征识别 (Target Recon)
- 提取题目文件（二进制、Web 站点、加密密文、流量包）。
- 识别关键算法特征（例如：自定义 Base64 表、RC4、TEA、SM4、Z3 约束条件）。

### Phase 2: 逆向推演与求解脚本 (Solver Script)
- 使用 Python z3-solver、pycryptodome 或 C 语言实现逆向解密逻辑。
- 自动化演算输入与期望输出。

### Phase 3: Flag 验证与总结
- 运行 Solver 脚本提取最终 Flag 格式（如 `flag{...}` 或 `ctf{...}`）。
- 编写解题 WP (WriteUp)。
