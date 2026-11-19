#!/usr/bin/env python3
import glob

services_data = [
    'lazy-gateway', 'lazy-broker-comms', 'lazy-secrets', 'lazy-tasks',
    'lazy-routines', 'lazy-fetcher', 'lazy-outbox', 'lazy-audit',
    'lazy-broker-fs', 'lazy-broker-web'
]

for p in glob.glob('/mnt/c/Users/len/OS/systemd/lazy-*.service'):
    with open(p, 'r') as f:
        content = f.read()
    
    # Remove any existing ReadWritePaths lines
    lines = [l for l in content.splitlines() if not l.startswith('ReadWritePaths=')]
    
    new_lines = []
    base = p.split('/')[-1].replace('.service', '')
    
    rw_paths = ['/run/lazy']
    if any(s == base for s in services_data):
        rw_paths.append('/data')
    if base in ('lazy-gateway', 'lazy-audit'):
        rw_paths.append('/var/log')
    if base in ('lazy-secrets', 'lazy-tasks'):
        rw_paths.append('/var/lib/lazy')
    if base == 'lazy-broker-hw':
        rw_paths.extend(['/sys/class/backlight', '/sys/class/rfkill', '/sys/devices/system/cpu'])
        
    rw_line = f"ReadWritePaths={' '.join(rw_paths)}"
    
    for l in lines:
        new_lines.append(l)
        if l.strip() == 'ProtectSystem=strict' or (base == 'lazy-broker-hw' and l.strip() == '[Service]'):
            new_lines.append(rw_line)
            
    with open(p, 'w') as f:
        f.write('\n'.join(new_lines) + '\n')
    print(f'Updated {base}: {rw_line}')
