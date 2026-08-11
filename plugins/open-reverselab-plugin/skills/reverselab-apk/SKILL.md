---
name: reverselab-apk
description: "Android APK Reverse Engineering & Frida Hook Protocol | Android APK 逆向与 Frida 插桩技能。"
---

# Android APK / DEX / Native Reverse Engineering Protocol (APK 逆向工作流)

基于 open-reverselab 的 Android 逆向分析标准流程。

---

## 🎯 核心原则

1. **多维分析**：结合 Java 层（JADX/DEX）与 Native 层（`.so` C++ 导出函数/RegisterNatives）共同分析。
2. **知识库优先**：遇到壳、抓包防护、加密算法时，查阅插件 `kb/apk-reverse/` 对应的技术文档与 Frida 脚本模板。

---

## 🔄 4 步分析工作流

### Phase 1: 静态解包与清单分析 (APK Unpack & Manifest)
- 反编译 `AndroidManifest.xml`，提取包名、主 Activity、Service、BroadcastReceiver 以及敏感权限。
- 识别加固壳类型（如 360加固、腾讯乐固、百度加固、爱加密等）。

### Phase 2: DEX / Java 逻辑逆向 (Java Analysis)
- 使用 JADX 提取 Java 源码，定位敏感 API（如 `Cipher.getInstance`, `SecretKeySpec`, `MessageDigest`）。
- 定位 JNI 接口声明（如 `private native String signParams(...)`）。

### Phase 3: Native .so 逆向 (Native Analysis)
- 分析 `lib/*.so` 共享库，查找 `JNI_OnLoad` 与动态注册函数 `RegisterNatives`。
- 使用 Ghidra 逆向分析 Native 层算法。

### Phase 4: Frida 动态监控与 Hook (Dynamic Instrumentation)
- 运行 Frida Hook Java 层函数与 Native 函数。
- 提取网络请求秘钥、签名参数或进行 SSL Unpinning 抓包。
