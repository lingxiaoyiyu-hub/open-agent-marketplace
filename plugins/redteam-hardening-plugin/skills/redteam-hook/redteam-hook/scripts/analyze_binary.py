#!/usr/bin/env python3
"""
RedTeam-Hook Binary Analysis Probe (v2)
真正的 PE/ELF 解析: 导入导出表、节区/熵、TLS 回调、缓解措施、加壳启发、
敏感 API 与 Hook 目标推荐, 支持 --json 结构化输出。
依赖: pefile (PE), pyelftools (ELF, 可选); 两者都缺时退化为字符串扫描。
"""
import sys, os, re, json, argparse, struct

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

SENSITIVE_KW = ["verify", "license", "check", "serial", "crypto", "rsa", "protect",
                "debug", "trust", "hash", "signature", "key", "auth", "trial",
                "regquery", "volume", "activate", "valid", "isdebugger", "ntquery"]
HOOK_WORTHY_KW = ["isdebuggerpresent", "getvolumeinformation", "winverifytrust",
                  "regqueryvalue", "messagebox", "checklicense", "activate",
                  "createfile", "readfile", "writefile", "virtualprotect", "connect"]
INTERESTING_STR = ["license", "serial", "crack", "register", "success", "invalid",
                   "expired", "trial", "key", "password", "auth", "token", "activate"]


def strings_in(data, limit=40):
    out = []
    for m in re.finditer(rb"[\x20-\x7e]{5,}", data):
        s = m.group().decode("ascii", "ignore")
        if any(k in s.lower() for k in INTERESTING_STR):
            out.append(s)
    for m in re.finditer(rb"(?:[\x20-\x7e]\x00){5,}", data):
        s = m.group().decode("utf-16le", "ignore")
        if any(k in s.lower() for k in INTERESTING_STR):
            out.append(s)
    return sorted(set(out))[:limit]


def scan_apis(names, extra_kw=None):
    kws = list(SENSITIVE_KW) + (extra_kw or [])
    hits, hooks = set(), set()
    for n in names:
        low = n.lower()
        if any(k in low for k in kws):
            hits.add(n)
        if any(k in low for k in HOOK_WORTHY_KW):
            hooks.add(n)
    return sorted(hits), sorted(hooks)


def analyze_pe(data, path):
    try:
        import pefile
    except ImportError:
        return {"error": "pefile not installed; run: pip install pefile"}
    pe = pefile.PE(data=data, fast_load=False)
    r = {"format": "PE", "machine": hex(pe.FILE_HEADER.Machine),
         "subsystem": pe.OPTIONAL_HEADER.Subsystem,
         "timestamp": hex(pe.FILE_HEADER.TimeDateStamp)}
    # sections + entropy
    r["sections"] = []
    for s in pe.sections:
        ent = round(s.get_entropy(), 2)
        r["sections"].append({
            "name": s.Name.rstrip(b"\x00").decode("latin1", "ignore"),
            "vsize": s.Misc_VirtualSize, "raw": s.SizeOfRawData,
            "entropy": ent, "chars": hex(s.Characteristics)})
    # mitigations
    dc = pe.OPTIONAL_HEADER.DllCharacteristics
    r["mitigations"] = {
        "ASLR": bool(dc & 0x0040), "DEP": bool(dc & 0x0100),
        "CFG": bool(dc & 0x4000), "ForceIntegrity": bool(dc & 0x0080)}
    # imports / exports
    imports, exports = [], []
    try:
        imports = [e.dll.decode("latin1", "ignore") for e in pe.DIRECTORY_ENTRY_IMPORT]
    except Exception:
        pass
    try:
        exports = [e.name.decode("latin1", "ignore") if e.name else f"ord{e.ordinal}"
                   for e in pe.DIRECTORY_ENTRY_EXPORT.symbols]
    except Exception:
        pass
    r["import_dlls"] = sorted(set(imports))
    r["exports_count"] = len(exports)
    # TLS callbacks
    tls = []
    try:
        if pe.DIRECTORY_ENTRY_TLS and pe.DIRECTORY_ENTRY_TLS.struct:
            tls = ["TLS callbacks present (early code exec point)"]
    except Exception:
        pass
    r["tls"] = tls
    # hook targets from import names + exports
    import_names = []
    try:
        for e in pe.DIRECTORY_ENTRY_IMPORT:
            import_names += [f.name.decode("latin1", "ignore") for f in e.imports if f.name]
    except Exception:
        pass
    sensitive, hooks = scan_apis(import_names + exports)
    r["sensitive_apis"] = sensitive[:40]
    r["candidate_hook_targets"] = hooks[:30]
    # packer heuristics
    packed = any(s["entropy"] > 7.2 for s in r["sections"])
    upx = b"UPX!" in data
    r["packed_hint"] = {"high_entropy_section": packed, "upx_marker": upx,
                        "overlay": (pe.get_overlay_data_start_offset() or 0) < len(data) if hasattr(pe, "get_overlay_data_start_offset") else False}
    r["strings"] = strings_in(data)
    return r


def analyze_elf(data, path):
    try:
        import elftools
    except ImportError:
        return {"error": "ELF support needs pyelftools: pip install pyelftools"}
    from elftools.elf.elffile import ELFFile
    import io
    f = ELFFile(io.BytesIO(data))
    r = {"format": "ELF", "machine": f.elfclass, "endian": f.little_endian}
    r["sections"] = []
    for s in f.iter_sections():
        r["sections"].append({"name": s.name, "size": s.data_size,
                              "flags": str(s.header.sh_flags)})
    imports, exports = [], []
    dynsym = f.get_section_by_name(".dynsym")
    if dynsym:
        for sym in dynsym.iter_symbols():
            if sym.name:
                if sym.entry.st_info.type == "STT_FUNC":
                    exports.append(sym.name)
                elif sym.entry.st_info.bind == "STB_GLOBAL":
                    exports.append(sym.name)
    r["symbols_count"] = len(exports)
    sensitive, hooks = scan_apis(exports)
    r["sensitive_apis"] = sensitive[:40]
    r["candidate_hook_targets"] = hooks[:30]
    r["strings"] = strings_in(data)
    return r


def main():
    ap = argparse.ArgumentParser(description="Binary probe: PE/ELF recon + hook target suggestions")
    ap.add_argument("file", help="path to binary (.exe/.dll/.so)")
    ap.add_argument("--json", action="store_true", help="JSON output")
    ap.add_argument("--limit", type=int, default=40)
    args = ap.parse_args()
    if not os.path.exists(args.file):
        print(json.dumps({"error": "file not found"})) if args.json else print(f"[!] not found: {args.file}")
        return 1
    data = open(args.file, "rb").read()
    head = {"file": os.path.basename(args.file), "size": len(data)}
    if data[:2] == b"MZ":
        res = analyze_pe(data, args.file)
    elif data[:4] == b"\x7fELF":
        res = analyze_elf(data, args.file)
    else:
        res = {"format": "unknown", "strings": strings_in(data)}
    head.update(res)
    if args.json:
        print(json.dumps(head, ensure_ascii=False, indent=2))
    else:
        print(f"== {head['file']} ({head['size']} bytes) ==")
        print("format:", head.get("format"), "| machine:", head.get("machine", "-"))
        print("mitigations:", head.get("mitigations", "-"))
        print("sections:")
        for s in head.get("sections", []):
            print(f"  {s['name']:12s} ent={s['entropy']:5.2f} chars={s['chars']}")
        print("packed_hint:", head.get("packed_hint", "-"))
        print("tls:", head.get("tls", "-"))
        print("import_dlls:", ", ".join(head.get("import_dlls", []))[:300] or "-")
        print("sensitive_apis:", ", ".join(head.get("sensitive_apis", []))[:300] or "-")
        print("candidate_hook_targets:", ", ".join(head.get("candidate_hook_targets", [])) or "-")
        print("interesting_strings:")
        for s in head.get("strings", [])[:15]:
            print("  *", s)
    return 0


if __name__ == "__main__":
    sys.exit(main())
