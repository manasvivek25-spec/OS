#!/usr/bin/env python3
"""Apply strong systemd sandboxing directives across lazy-* services."""

import glob
import re

directives_to_add = """
PrivateDevices=yes
ProtectKernelLogs=yes
ProtectClock=yes
ProtectHostname=yes
RestrictNamespaces=yes
CapabilityBoundingSet=
UMask=0077
RemoveIPC=yes
"""

for path in glob.glob("/mnt/c/Users/len/OS/systemd/lazy-*.service"):
    with open(path, "r") as f:
        content = f.read()
    
    # Don't add capability/device restrictions to hardware broker
    is_hw = "broker-hw" in path
    
    lines = content.splitlines()
    new_lines = []
    added = False
    for line in lines:
        new_lines.append(line)
        if line.strip() == "PrivateTmp=yes" and not added:
            new_lines.append("PrivateDevices=yes" if not is_hw else "# PrivateDevices omitted for hw broker")
            new_lines.append("ProtectKernelLogs=yes")
            new_lines.append("ProtectClock=yes")
            new_lines.append("ProtectHostname=yes")
            new_lines.append("RestrictNamespaces=yes")
            if not is_hw:
                new_lines.append("CapabilityBoundingSet=")
            new_lines.append("UMask=0077")
            new_lines.append("RemoveIPC=yes")
            if "lazy-gateway" not in path and "lazy-broker-web" not in path and "lazy-fetcher" not in path and "lazy-llm" not in path:
                new_lines.append("IPAddressDeny=any")
            added = True
            
    content = "\n".join(new_lines) + "\n"
    with open(path, "w") as f:
        f.write(content)
    print(f"Hardened {path}")
