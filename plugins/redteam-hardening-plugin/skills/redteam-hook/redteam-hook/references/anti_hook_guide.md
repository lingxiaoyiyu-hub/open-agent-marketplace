# 🛡️ 蓝队反 Hook 与软件二进制加固代码库 (Anti-Hook Reference v2)

本指南汇总对抗 Inline Hook、API 劫持、Frida 插桩、调试器的核心防范技术与可编译 C++ 源码。

---

## 0. 防御分层总览

| 层级 | 技术 | 检测/对抗目标 | 代价 |
|------|------|--------------|------|
| L1 代码完整性 | CRC32/Hash 自校验 | Inline Hook, Memory Patch | 低 |
| L2 系统调用层 | Direct Syscall | Ring3 API Hook (Frida/MinHook) | 中 |
| L3 环境检测 | Anti-Frida/Anti-Debug | 动态插桩, 调试器 | 低 |
| L4 虚表保护 | VTable 只读校验 | 虚函数劫持 | 中 |
| L5 控制流 | CFG / ROP 防护 | ROP, JOP | 编译器支持 |

> 建议 L1+L3 起步，关键函数叠加 L2，核心对象用 L4，全程序开 L5。

---

## 1. 代码段内存完整性校验 (Anti-Inline Hook / CRC32 Check)

Inline Hook 会在函数开头写入 `E9 (JMP)`。初始化时计算 `.text` 段 CRC32，运行期动态校验。

```cpp
#include <windows.h>
#include <iostream>

// 计算内存区块 CRC32 校验码
DWORD CalcCRC32(BYTE* addr, DWORD size) {
    DWORD crc = 0xFFFFFFFF;
    for (DWORD i = 0; i < size; ++i) {
        crc ^= addr[i];
        for (int j = 0; j < 8; ++j)
            crc = (crc & 1) ? (crc >> 1) ^ 0xEDB88320 : crc >> 1;
    }
    return ~crc;
}

// 启动时快照 .text 段
DWORD g_textCRC = 0;
void SnapshotText() {
    HMODULE hMod = GetModuleHandleW(NULL);
    PIMAGE_DOS_HEADER dos = (PIMAGE_DOS_HEADER)hMod;
    PIMAGE_NT_HEADERS nt = (PIMAGE_NT_HEADERS)((BYTE*)hMod + dos->e_lfanew);
    PIMAGE_SECTION_HEADER sec = IMAGE_FIRST_SECTION(nt);
    for (int i = 0; i < nt->FileHeader.NumberOfSections; ++i) {
        if (memcmp(sec[i].Name, ".text", 5) == 0) {
            g_textCRC = CalcCRC32((BYTE*)hMod + sec[i].VirtualAddress, sec[i].Misc.VirtualSize);
            break;
        }
    }
}

// 运行期校验 (放心跳线程)
bool VerifyText() {
    HMODULE hMod = GetModuleHandleW(NULL);
    PIMAGE_DOS_HEADER dos = (PIMAGE_DOS_HEADER)hMod;
    PIMAGE_NT_HEADERS nt = (PIMAGE_NT_HEADERS)((BYTE*)hMod + dos->e_lfanew);
    PIMAGE_SECTION_HEADER sec = IMAGE_FIRST_SECTION(nt);
    for (int i = 0; i < nt->FileHeader.NumberOfSections; ++i) {
        if (memcmp(sec[i].Name, ".text", 5) == 0) {
            DWORD now = CalcCRC32((BYTE*)hMod + sec[i].VirtualAddress, sec[i].Misc.VirtualSize);
            return now == g_textCRC;
        }
    }
    return false;
}

// 快速首字节检测: JMP(0xE9) / INT3(0xCC) / EB(短跳)
bool IsHooked(void* fn) {
    BYTE b = *(BYTE*)fn;
    return b == 0xE9 || b == 0xEB || b == 0xCC;
}
```

### 弱点与加固
- ❌ 攻击者可 Hook `VirtualProtect` 或在心跳线程的 CRC 计算函数本身打补丁绕过。
- ✅ 加固: 校验逻辑分散到多处、用随机延迟触发、对校验函数自身也做 CRC。

---

## 2. Direct Syscall 直接系统调用 (绕过 Ring3 API Hook)

攻击者常 Hook `ntdll.dll`。Direct Syscall 用内联汇编直接 `syscall` 指令，跳过 DLL。

```cpp
#include <windows.h>
#include <winternl.h>

// 方案 A: 从 ntdll 读取 syscall number, 自行调用 (兼容性好)
// ntdll!NtQueryInformationProcess 开头: mov r10,rcx; mov eax,<SSN>; syscall
WORD GetSyscallNumber(const char* funcName) {
    HMODULE ntdll = GetModuleHandleW(L"ntdll.dll");
    BYTE* fn = (BYTE*)GetProcAddress(ntdll, funcName);
    if (!fn || fn[0] != 0x4C || fn[1] != 0x8B) return 0;
    return *(WORD*)(fn + 4);  // mov eax, imm32 的低 16 位
}

// 方案 B: 纯汇编 stub (x64 MSVC 需要 .asm 文件)
// my_syscall.asm:
//   .code
//   MyNtQueryInformationProcess PROC
//       mov r10, rcx          ; win64 ABI: rcx -> r10
//       mov eax, <SSN>        ; 系统调用号 (运行时填)
//       syscall
//       ret
//   MyNtQueryInformationProcess ENDP
//   END

// 用 Direct Syscall 检测调试器 (绕过 Ring3 IsDebuggerPresent hook)
bool IsBeingDebugged_Direct() {
    DWORD debugPort = 0;
    // NtQueryInformationProcess(ProcessDebugPort=7)
    // 正常会调 ntdll, 这里直调绕过 hook
    // 简化: 检查 PEB->BeingDebuggered (不走 API)
    PPEB peb = (PPEB)__readgsqword(0x60);  // x64: gs:[0x60] = TEB->Peb
    return peb->BeingDebuggered != 0;
}
```

### 弱点
- ❌ 攻击者可在内核层 hook (ETW/EDR 才到这层), 或扫描 syscall stub 特征码。
- ❌ 固定 SSN 在不同 Windows 版本会变; 需运行时从 ntdll 动态读取。

---

## 3. Anti-Frida 与反调试检测

```cpp
#include <windows.h>
#include <tlhelp32.h>

// 3.1 检测 Frida 命名管道 (frida-agent 默认创建 \\.\pipe\frida-*)
bool DetectFridaPipe() {
    WIN32_FIND_DATAA fd;
    HANDLE h = FindFirstFileA("\\\\.\\pipe\\*", &fd);
    if (h == INVALID_HANDLE_VALUE) return false;
    bool found = false;
    do {
        if (strstr(fd.cFileName, "frida") || strstr(fd.cFileName, "gum-js") || strstr(fd.cFileName, "linjector"))
            found = true;
    } while (FindNextFileA(h, &fd));
    FindClose(h);
    return found;
}

// 3.2 检测 Frida 默认端口 27042
bool DetectFridaPort() {
    WSADATA wsa;
    WSAStartup(MAKEWORD(2,2), &wsa);
    SOCKET s = socket(AF_INET, SOCK_STREAM, 0);
    DWORD nonblk = 1;
    ioctlsocket(s, FIONBIO, &nonblk);
    sockaddr_in addr = {0};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(27042);
    addr.sin_addr.s_addr = htonl(0x7F000001); // 127.0.0.1
    connect(s, (sockaddr*)&addr, sizeof(addr));
    fd_set set; FD_ZERO(&set); FD_SET(s, &set);
    timeval tv = {0, 200000};
    bool open = select(0, NULL, &set, NULL, &tv) > 0;
    closesocket(s);
    WSACleanup();
    return open;
}

// 3.3 扫描进程内存中的 Frida 特征字符串
bool DetectFridaInMemory() {
    HANDLE h = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    PROCESSENTRY32W pe = {sizeof(pe)};
    if (Process32FirstW(h, &pe)) {
        do {
            if (wcsstr(pe.szExeFile, L"frida")) { CloseHandle(h); return true; }
        } while (Process32NextW(h, &pe));
    }
    CloseHandle(h);
    return false;
}

// 3.4 PEB 直接检测调试器 (不走 API, 绕过 IsDebuggerPresent hook)
bool DetectDebugger_PEB() {
    PPEB peb = (PPEB)__readgsqword(0x60);
    if (peb->BeingDebuggered) return true;
    // NtGlobalFlag (偏移 0xBC on x64): 调试器会设 FLG_HEAP_*
    DWORD flags = *(DWORD*)((BYTE*)peb + 0xBC);
    return (flags & 0x70) != 0;
}

// 3.5 硬件断点检测 (Frida/调试器常用 DR0-DR3)
bool DetectHwBreakpoints() {
    CONTEXT ctx = {0};
    ctx.ContextFlags = CONTEXT_DEBUG_REGISTERS;
    GetThreadContext(GetCurrentThread(), &ctx);
    return ctx.Dr0 || ctx.Dr1 || ctx.Dr2 || ctx.Dr3;
}
```

---

## 4. VTable 虚函数指针只读校验

攻击者可篡改 C++ 对象的 vtable 指针劫持虚函数调用。

```cpp
#include <windows.h>

// 启动时快照关键对象的 vtable 指针
void* g_originalVtable = nullptr;

void SnapshotVtable(void* obj) {
    g_originalVtable = *(void**)obj;
}

// 运行期校验 vtable 是否被篡改
bool VerifyVtable(void* obj) {
    void* current = *(void**)obj;
    if (current != g_originalVtable) return false; // 被改!
    // 进一步: 校验 vtable 所在页是否可写 (正常应只读)
    MEMORY_BASIC_INFORMATION mbi;
    VirtualQuery(current, &mbi, sizeof(mbi));
    return !(mbi.Protect & (PAGE_READWRITE | PAGE_EXECUTE_READWRITE));
}

// 主动将 vtable 页面设为只读
void LockVtable(void* obj) {
    void* vtbl = *(void**)obj;
    DWORD old;
    VirtualProtect(vtbl, 8, PAGE_READONLY, &old);
}
```

---

## 5. PyInstaller 打包程序的加固建议 (针对 Python 打包)

如果启动器是 PyInstaller 打包 (如本案例):

1. **混淆 Python 源码**: 用 `pyarmor` / `cython` 编译关键模块为 .pyd, 避免 pyc 被直接反编译。
2. **license 校验放 C 扩展**: 把 HMAC/RSA 校验逻辑用 Cython 编译成原生 .pyd, 而非纯 Python。
3. **反 pyinstxtractor**: 检测 `MEIPASS` 环境变量特征, 或在 bootstrap 阶段校验 archive 完整性。
4. **license 文件加密**: `.bakal-v2-license` 不要明文, 用机器绑定密钥 (MAC+CPUID 派生) AES 加密。
5. **服务器端二次验证**: 本地校验通过后, 再向服务器发心跳确认 (防本地伪造 license)。
6. **关键逻辑服务端化**: 翻牌概率等敏感配置放服务端, 客户端不存。
