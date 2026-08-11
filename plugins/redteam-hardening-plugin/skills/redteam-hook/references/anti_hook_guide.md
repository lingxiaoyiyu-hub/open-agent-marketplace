# 🛡️ 蓝队反 Hook 与软件二进制加固代码库 (Anti-Hook Reference)

本指南汇总了对抗 Inline Hook、API 劫持、Frida 插桩的核心防范技术与 C++ 源码实现。

---

## 1. 代码段内存完整性校验 (Anti-Inline Hook / CRC32 Check)

Inline Hook 通常会在目标函数开头写入 `E9 (JMP)` 指令。通过在初始化时计算 `.text` 段或关键函数的 CRC32/Hash 值，运行期间动态校验，可检测指令是否被篡改。

```cpp
#include <windows.h>
#include <iostream>

// 计算内存区块 CRC32 校验码
DWORD CalculateMemoryCRC32(BYTE* address, DWORD size) {
    DWORD crc = 0xFFFFFFFF;
    for (DWORD i = 0; i < size; ++i) {
        crc ^= address[i];
        for (int j = 0; j < 8; ++j) {
            if (crc & 1) crc = (crc >> 1) ^ 0xEDB88320;
            else crc >>= 1;
        }
    }
    return ~crc;
}

// 检测目标函数开头是否被改动 (比如包含了 JMP 0xE9 或 INT 3 0xCC)
bool CheckFunctionIntegrity(void* funcPtr, BYTE originalFirstByte) {
    BYTE* ptr = (BYTE*)funcPtr;
    if (ptr[0] == 0xE9 || ptr[0] == 0xEB || ptr[0] == 0xCC) {
        return false; // 被 Hook！
    }
    if (originalFirstByte != 0x00 && ptr[0] != originalFirstByte) {
        return false; // 字节不一致！
    }
    return true; // 正常
}
```

---

## 2. Direct Syscall 直接系统调用 (绕过 Ring3 API Hook)

攻击者常常 Hook `kernel32.dll` 或 `ntdll.dll` 中的 API。使用直接系统调用（Syscall）可以跳过 Ring3 DLL，直接请求内核。

```cpp
extern "C" NTSTATUS DirectSyscall_NtQueryInformationProcess(
    HANDLE ProcessHandle,
    ULONG ProcessInformationClass,
    PVOID ProcessInformation,
    ULONG ProcessInformationLength,
    PULONG ReturnLength
);
```

---

## 3. Anti-Frida 动态插桩检测

Frida 在运行时会引入特定名称的命名管道 (Named Pipe) 和默认端口 (27042)。

```cpp
#include <windows.h>

bool DetectFridaNamedPipe() {
    WIN32_FIND_DATAA findData;
    HANDLE hFind = FindFirstFileA("\\\\.\\pipe\\*", &findData);
    if (hFind != INVALID_HANDLE_VALUE) {
        do {
            if (strstr(findData.cFileName, "frida") != NULL || 
                strstr(findData.cFileName, "gum-js") != NULL) {
                CloseHandle(hFind);
                return true;
            }
        } while (FindNextFileA(hFind, &findData));
        CloseHandle(hFind);
    }
    return false;
}
```
