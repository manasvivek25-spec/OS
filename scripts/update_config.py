import re

path = "/home/manas/lazy-build/output/.config"
with open(path, "r") as f:
    c = f.read()

line = 'BR2_ROOTFS_DEVICE_TABLE="system/device_table.txt /mnt/c/Users/len/OS/lazy-br2/board/lazy/device_table.txt"'
if "BR2_ROOTFS_DEVICE_TABLE" in c:
    c = re.sub(r'BR2_ROOTFS_DEVICE_TABLE=.*', line, c)
else:
    c += "\n" + line + "\n"

with open(path, "w") as f:
    f.write(c)

print("Successfully updated .config with BR2_ROOTFS_DEVICE_TABLE")
