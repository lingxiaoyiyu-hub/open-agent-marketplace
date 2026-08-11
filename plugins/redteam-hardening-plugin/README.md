# RedTeam Hook 加固插件 (redteam-hardening-plugin)

红蓝 Hook 攻防对抗协议: 红队生成可运行的 Hook PoC, 蓝队加固防御, 多轮迭代。

## 包含
- `skills/redteam-hook/SKILL.md` — 四阶段攻防协议 (侦察→攻击→加固→Bypass)
- `skills/redteam-hook/scripts/analyze_binary.py` — PE/ELF 二进制探针 (真实解析)
- `skills/redteam-hook/references/anti_hook_guide.md` — 反 Hook 加固代码库 (C++)
- `skills/redteam-hook/references/hardening_report_template.md` — 加固报告模板

## 使用
在新任务中描述攻防需求即可自动激活, 或手动运行探针:
```
python scripts/analyze_binary.py <目标文件>
python scripts/analyze_binary.py <目标文件> --json
```

## 依赖
```
pip install pefile pyelftools
```

## ⚠️ 合法性
仅用于自己拥有或已获授权的软件。破解他人软件违法。
