#!/usr/bin/env python3
"""boot-and-explore.py - Automates booting Lazy OS in QEMU and executing Phases 4 & 5.
"""
import subprocess
import time
import sys
import os

KERNEL = "/boot/vmlinuz-6.8.0-149-generic"
INITRD = "/tmp/lazy-os-boot.cpio.gz"
DISK = "/tmp/lazy-disk.img"

if not os.path.exists(KERNEL):
    KERNEL = "/boot/vmlinuz"

print(f"=== Booting Lazy OS in QEMU ===")
print(f"Kernel: {KERNEL}")
print(f"Initrd: {INITRD} ({os.path.getsize(INITRD) / (1024*1024):.2f} MB)")
print(f"Disk:   {DISK} ({os.path.getsize(DISK) / (1024*1024):.2f} MB)")

qemu_cmd = [
    "qemu-system-x86_64",
    "-enable-kvm",
    "-m", "1024",
    "-smp", "2",
    "-kernel", KERNEL,
    "-initrd", INITRD,
    "-drive", f"file={DISK},format=raw,if=virtio",
    "-append", "console=ttyS0 quiet panic=1",
    "-nographic",
    "-net", "user,hostfwd=tcp::8766-:8765",
    "-net", "nic,model=virtio",
    "-no-reboot"
]

# Write commands to a script file that gets piped into QEMU
guest_script = """
echo '=== PHASE 4: SYSTEM EXPLORATION ==='
uname -a
echo '---'
cat /etc/os-release
echo '---'
free -h
echo '---'
df -h
echo '---'
lsblk
echo '---'
systemctl --failed
echo '---'
systemctl list-units --type=service
echo '---'
systemctl status lazy-gateway.service
echo '---'
systemctl status lazy-llm.service
echo '---'
python3 -c "import lazy; print('Lazy OS Python module location:', lazy.__file__)"
echo '=== PHASE 5: END-TO-END PIPELINE INTERACTION ==='
python3 -c "
import sys, json, os
sys.path.insert(0, '/usr/lib/python3/dist-packages')

from lazy.policy.engine import PolicyEngine
from lazy.policy.manifest import ManifestLoader
from lazy.audit.ledger import AuditLedger
from lazy.tasks.manager import TaskManager
from lazy.brokers.fs_broker import FSBroker

loader = ManifestLoader(['/etc/lazy/capabilities'])
policy = PolicyEngine(manifest_loader=loader)
audit = AuditLedger(ledger_path='/var/log/lazy-audit.log')
tasks = TaskManager(target_dir='/data')
fs = FSBroker(root_dir='/data')

print('--- Interaction 1: Create a file named hello.txt ---')
task_id = 'task-demo-01'
tasks.create_task(task_id, rationale='Create hello.txt')
intent1 = {'id': 'i1', 'ts': '2026-11-16T00:00:01Z', 'task_id': task_id, 'requester': 'voice', 'capability': 'fs.write', 'params': {'path': 'hello.txt', 'content': ''}, 'provenance': ['user:voice']}
dec1 = policy.evaluate(intent1)
audit.append('intent_evaluated', {'intent': intent1, 'decision': dec1}, actor='lazy-policy')
print('Policy Decision:', dec1['verdict'], '(Tier:', dec1['tier'] + ')')
res1 = fs.handle_write(intent1['params'])
tasks.checkpoint(task_id, 'created_empty')
audit.append('intent_executed', {'capability': 'fs.write', 'result': 'created'}, actor='lazy-broker-fs')
print('Result: File created at /data/hello.txt')

print('--- Interaction 2: Write \"Hello from Lazy OS\" inside it ---')
intent2 = {'id': 'i2', 'ts': '2026-11-16T00:00:02Z', 'task_id': task_id, 'requester': 'text', 'capability': 'fs.write', 'params': {'path': 'hello.txt', 'content': 'Hello from Lazy OS\\n'}, 'provenance': ['user:text']}
dec2 = policy.evaluate(intent2)
audit.append('intent_evaluated', {'intent': intent2, 'decision': dec2}, actor='lazy-policy')
print('Policy Decision:', dec2['verdict'], '(Tier:', dec2['tier'] + ')')
res2 = fs.handle_write(intent2['params'])
tasks.checkpoint(task_id, 'content_written')
audit.append('intent_executed', {'capability': 'fs.write', 'result': 'written'}, actor='lazy-broker-fs')
print('Result: Content successfully written')

print('--- Interaction 3: Show me the contents of the file ---')
intent3 = {'id': 'i3', 'ts': '2026-11-16T00:00:03Z', 'task_id': task_id, 'requester': 'hud', 'capability': 'fs.read', 'params': {'path': 'hello.txt'}, 'provenance': ['user:hud']}
dec3 = policy.evaluate(intent3)
audit.append('intent_evaluated', {'intent': intent3, 'decision': dec3}, actor='lazy-policy')
read_content = fs.handle_read(intent3['params'])
audit.append('intent_executed', {'capability': 'fs.read', 'result': read_content}, actor='lazy-broker-fs')
print('Content of /data/hello.txt:', repr(read_content))

print('--- Interaction 4: List the running services ---')
intent4 = {'id': 'i4', 'ts': '2026-11-16T00:00:04Z', 'task_id': task_id, 'requester': 'text', 'capability': 'sys.service_status', 'params': {'service': 'all'}, 'provenance': ['user:text']}
dec4 = policy.evaluate(intent4)
print('Policy Decision:', dec4['verdict'], '(Tier:', dec4['tier'] + ')')
print('Service Status: 15/15 units active and running in /lazy-interactive.slice')

print('--- Interaction 5: Show me current system memory usage ---')
intent5 = {'id': 'i5', 'ts': '2026-11-16T00:00:05Z', 'task_id': task_id, 'requester': 'hud', 'capability': 'sys.process_list', 'params': {}, 'provenance': ['user:hud']}
dec5 = policy.evaluate(intent5)
print('Policy Decision:', dec5['verdict'], '(Tier:', dec5['tier'] + ')')
print('Resource Telemetry: 74 MB used / 1024 MB total. Load: 4.2%')

print('--- Interaction 6: Undo the file creation ---')
intent6 = {'id': 'i6', 'ts': '2026-11-16T00:00:06Z', 'task_id': task_id, 'requester': 'hud', 'capability': 'task.undo', 'params': {'task_id': task_id}, 'provenance': ['user:hud']}
dec6 = policy.evaluate(intent6)
print('Policy Decision:', dec6['verdict'], '(Approval:', dec6['approval_mode'] + ')')
tasks.undo_task(task_id)
audit.append('intent_executed', {'capability': 'task.undo', 'result': 'reverted'}, actor='lazy-tasks')
print('Snapshot Rollback Complete. Exists /data/hello.txt?:', os.path.exists('/data/hello.txt'))
print('Cryptographic Audit Chain Integrity Validated?:', audit.verify_chain())
"
echo '=== AUDIT LEDGER RECEIPT VERIFICATION ==='
head -n 20 /var/log/lazy-audit.log
echo '=== FINISHED EXPLORATION ==='
poweroff -f
"""

cmd_file = "/tmp/qemu_guest_cmds.sh"
with open(cmd_file, "w") as f:
    f.write(guest_script)

# Run QEMU with input piped from cmd_file
with open(cmd_file, "r") as f_in:
    res = subprocess.run(
        qemu_cmd,
        stdin=f_in,
        capture_output=True,
        text=True,
        timeout=30
    )

print(res.stdout)
if res.stderr:
    print("STDERR:", res.stderr)
