#!/usr/bin/env python3
"""Injects the 512MB Btrfs partition containing the SmolLM2 model into lazy-disk.img."""
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
disk_img = REPO_ROOT / "build/v2/lazy-disk.img"
btrfs_part = Path("/tmp/btrfs-data-part.img")

assert btrfs_part.exists(), f"Source partition {btrfs_part} does not exist"

if disk_img.exists():
    disk_img.unlink()

print("Creating 1024M raw disk image...")
subprocess.run(["truncate", "-s", "1024M", str(disk_img)], check=True)

sfdisk_input = """label: gpt
label-id: 01234567-89AB-CDEF-0123-456789ABCDEF
unit: sectors

1 : start=2048, size=32768, type=C12A7328-F81F-11D2-BA4B-00A0C93EC93B, name="boot"
2 : start=34816, size=204800, type=0FC63DAF-8483-4772-8E79-3D69D8477DE4, name="root"
3 : start=239616, size=1048576, type=0FC63DAF-8483-4772-8E79-3D69D8477DE4, name="data"
"""
print("Applying GPT partition table...")
subprocess.run(["sfdisk", str(disk_img)], input=sfdisk_input, text=True, check=True)

print("Injecting Btrfs data partition into partition 3 (seek=239616)...")
subprocess.run(
    f"dd if={btrfs_part} of={disk_img} seek=239616 bs=512 conv=notrunc",
    shell=True,
    check=True
)
print("Injection complete.")
