#!/usr/bin/env python3
"""send_guest_command.py - Sends keystrokes to QEMU guest console via monitor socket.
"""
import socket
import time
import sys

MONITOR_SOCK = "/tmp/qemu-monitor.sock"

KEY_MAP = {
    ' ': 'spc',
    '\n': 'ret',
    '-': 'minus',
    '_': 'shift-minus',
    '/': 'slash',
    '.': 'dot',
    '>': 'shift-dot',
    '<': 'shift-comma',
    ':': 'shift-semicolon',
    ';': 'semicolon',
    '"': 'shift-apostrophe',
    "'": 'apostrophe',
    '=': 'equal',
    '+': 'shift-equal',
    '*': 'shift-8',
    '&': 'shift-7',
    '%': 'shift-5',
    '$': 'shift-4',
    '#': 'shift-3',
    '@': 'shift-2',
    '!': 'shift-1',
}

def send_command(cmd_text):
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(MONITOR_SOCK)
    s.settimeout(2.0)
    try:
        s.recv(1024)
    except Exception:
        pass

    for char in cmd_text:
        k = KEY_MAP.get(char, char)
        s.sendall(f"sendkey {k}\n".encode())
        time.sleep(0.04)
        try:
            s.recv(1024)
        except Exception:
            pass
    s.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1] + "\n"
    else:
        cmd = "echo live-test\n"
    send_command(cmd)
