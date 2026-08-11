#!/usr/bin/env python3
"""
PE / Binary Analysis Probe for Red-Team Hook Target Reconnaissance.
Extracts PE exports, imports, sensitive string patterns, and candidate Hook targets.
"""

import sys
import os
import re
import struct

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

SENSITIVE_API_KEYWORDS = [
    "Verify", "License", "Check", "Volume", "RegQuery", "Crypto", "RSA", 
    "Protect", "Debug", "Trust", "Hash", "Signature", "Key", "Auth", "Trial"
]

INTERESTING_STRINGS = [
    "license", "serial", "crack", "register", "success", "invalid", "expired", 
    "trial", "key", "password", "auth", "token", "activate"
]

def analyze_pe_basic(filepath):
    if not os.path.exists(filepath):
        print(f"[!] File not found: {filepath}")
        return

    print(f"==================================================")
    print(f"[*] Analyzing Binary Target: {os.path.basename(filepath)}")
    print(f"[*] File Size: {os.path.getsize(filepath)} bytes")
    print(f"==================================================")

    with open(filepath, "rb") as f:
        data = f.read()

    if len(data) < 0x40 or data[:2] != b"MZ":
        print("[!] Not a standard MS-DOS / PE Executable")
        extract_strings(data)
        return

    pe_offset = struct.unpack("<I", data[0x3C:0x40])[0]
    if len(data) < pe_offset + 4 or data[pe_offset:pe_offset+2] != b"PE":
        print("[!] Invalid PE Header signature")
        extract_strings(data)
        return

    print("[+] Valid PE Header detected.")

    found_apis = set()
    for kw in SENSITIVE_API_KEYWORDS:
        matches = re.findall(rb'[A-Za-z0-9_]*' + kw.encode('ascii') + rb'[A-Za-z0-9_]*', data, re.IGNORECASE)
        for m in matches:
            if len(m) > 4:
                found_apis.add(m.decode('ascii', errors='ignore'))

    if found_apis:
        print("\n[+] Candidate Sensitive APIs / Symbols Found in Memory:")
        for api in sorted(found_apis)[:30]:
            print(f"   - {api}")
    else:
        print("\n[-] No obvious sensitive API strings found directly.")

    extract_strings(data)

def extract_strings(data):
    print("\n[*] Interesting Strings (License/Verify Keywords):")
    ascii_strings = re.findall(b'[\x20-\x7E]{5,}', data)
    unicode_strings = re.findall(b'(?:[\x20-\x7E]\x00){5,}', data)
    
    candidates = []
    for s in ascii_strings:
        st = s.decode('ascii', errors='ignore')
        if any(k in st.lower() for k in INTERESTING_STRINGS):
            candidates.append(st)

    for s in unicode_strings:
        st = s.decode('utf-16le', errors='ignore')
        if any(k in st.lower() for k in INTERESTING_STRINGS):
            candidates.append(st)

    for c in list(set(candidates))[:25]:
        print(f"   * '{c}'")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_binary.py <path_to_binary>")
        sys.exit(1)
    analyze_pe_basic(sys.argv[1])
