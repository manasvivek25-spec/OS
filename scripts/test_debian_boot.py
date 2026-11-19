import subprocess
import time

cmd = [
    "qemu-system-x86_64",
    "-m", "1024",
    "-smp", "2",
    "-kernel", "/home/manas/debian-12/vmlinuz",
    "-initrd", "/home/manas/debian-12/initrd.img",
    "-drive", "file=/home/manas/debian-12/disk.raw,format=raw,if=virtio",
    "-append", "root=/dev/vda1 ro console=ttyS0 panic=1 quiet systemd.default_timeout_start_sec=10",
    "-display", "none",
    "-serial", "stdio"
]
t0 = time.time()
p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

time.sleep(6)
script = "\nroot\nexport PATH=/usr/bin:/bin:/usr/sbin:/sbin\nfree -m\ncat /proc/meminfo | head -n 10\nsystemctl list-units --state=running | head -n 10\npoweroff\n"
try:
    stdout, stderr = p.communicate(input=script, timeout=12)
except Exception:
    p.kill()
    stdout, stderr = p.communicate()
elapsed = time.time() - t0

print(f"Elapsed: {elapsed:.2f} s")
print("STDOUT:")
print(stdout)
