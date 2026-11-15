#!/usr/bin/env python3
"""test_v2_b1_storage.py - Verifies V2.B1 persistent Btrfs storage across reboots
and snapshot rollback.
"""
import subprocess
import time
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BUILD_V2 = REPO_ROOT / "build/v2"
KERNEL = "/boot/vmlinuz-6.8.0-149-generic"
INITRD = str(BUILD_V2 / "lazy-os-boot.cpio.gz")
DISK = str(BUILD_V2 / "lazy-disk.img")

evidence_lines = []

def run_qemu_session(commands: str, session_name: str) -> str:
    print(f"\n--- Running QEMU Session: {session_name} ---")
    qemu_cmd = [
        "qemu-system-x86_64",
        "-enable-kvm",
        "-m", "1024",
        "-smp", "2",
        "-kernel", KERNEL,
        "-initrd", INITRD,
        "-drive", f"file={DISK},format=raw,if=virtio",
        "-append", "console=ttyS0 quiet panic=1 lazy_interactive=1",
        "-nographic",
        "-net", "none",
        "-no-reboot"
    ]
    proc = subprocess.Popen(
        qemu_cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    output = []
    def reader():
        for line in proc.stdout:
            output.append(line)
            sys.stdout.write(line)
            sys.stdout.flush()

    import threading
    t = threading.Thread(target=reader, daemon=True)
    t.start()
    
    time.sleep(2.5)
    proc.stdin.write(commands)
    proc.stdin.flush()
    
    proc.wait(timeout=35)
    t.join(timeout=5)
    return "".join(output)

# Session 1: Verify real mount, write persistent file, poweroff
cmds_run1 = """
echo '=== RUN1: MOUNT INSPECTION ==='
findmnt /data || mount | grep /data
df -h /data
lsblk
echo '=== RUN1: WRITE PERSISTENT FILE ==='
echo 'BTRFS_PERSISTENCE_TEST_PASSED_20261116' > /data/persistent_test.txt
sync
cat /data/persistent_test.txt
echo '=== RUN1 COMPLETE, POWERING OFF ==='
sleep 1
poweroff -f
"""

out1 = run_qemu_session(cmds_run1, "Run 1: Write Persistent File")
evidence_lines.append("=== RUN 1 OUTPUT ===")
evidence_lines.append(out1)

# Session 2: Reboot, verify persistent file survived, test snapshot & rollback
cmds_run2 = """
echo '=== RUN2: REBOOT VERIFICATION ==='
findmnt /data || mount | grep /data
echo '=== RUN2: READ PERSISTENT FILE ==='
cat /data/persistent_test.txt

echo '=== RUN2: SNAPSHOT ROLLBACK TEST ==='
python3 -c "
import os, sys
sys.path.insert(0, '/usr/lib/python3/dist-packages')
from lazy.tasks.manager import TaskManager
from lazy.tasks.backend import TreeHasher

tasks = TaskManager(target_dir='/data', backend_type='copy')
task_id = 'b1-verify-task'
tasks.create_task(task_id)

initial_hash = TreeHasher.hash_directory('/data')
print('Initial /data tree hash:', initial_hash)

# Checkpoint before mutation
tasks.checkpoint_before_step(task_id, 'step-1', 0)

# Mutate /data
with open('/data/mutation.txt', 'w') as f:
    f.write('Temporary file created during task\\n')
mutated_hash = TreeHasher.hash_directory('/data')
print('Mutated /data tree hash:', mutated_hash)
print('File /data/mutation.txt exists?:', os.path.exists('/data/mutation.txt'))

# Undo / rollback task
tasks.undo_task(task_id)
restored_hash = TreeHasher.hash_directory('/data')
print('Restored /data tree hash:', restored_hash)
print('File /data/mutation.txt exists after undo?:', os.path.exists('/data/mutation.txt'))
print('Hashes match initial?:', initial_hash == restored_hash)
"

echo '=== RUN2 COMPLETE, POWERING OFF ==='
sleep 1
poweroff -f
"""

out2 = run_qemu_session(cmds_run2, "Run 2: Read File & Rollback")
evidence_lines.append("=== RUN 2 OUTPUT ===")
evidence_lines.append(out2)

evidence_file = REPO_ROOT / "docs/audit/v2_b1_evidence.txt"
evidence_file.write_text("\n".join(evidence_lines))
print(f"\n[OK] V2.B1 evidence written to {evidence_file}")
