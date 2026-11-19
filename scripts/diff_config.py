with open('/mnt/c/Users/len/OS/lazy-br2/configs/lazy_x86_64_defconfig') as f:
    f1 = [l.strip() for l in f if l.strip() and not l.startswith('#')]
with open('/home/manas/lazy-build/output/.config') as f:
    f2 = set(l.strip() for l in f if l.strip() and not l.startswith('#'))

missing = [l for l in f1 if l not in f2]
print("Missing configs in /home/manas/lazy-build/output/.config:")
for m in missing:
    print("  ", m)
