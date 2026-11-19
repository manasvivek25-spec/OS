"""Secrets vault server entry point for lazy-secrets."""
from __future__ import annotations

import os
import signal
import sys
import time
from pathlib import Path
from lazy.common.socket_server import parse_socket_arg
from lazy.secrets.service import SecretsService
from lazy.secrets.vault import SecretVault


def main():
    sock = parse_socket_arg("secrets")
    vault_dir = os.environ.get("LAZY_SECRETS_DIR", "/var/lib/lazy/secrets")
    vault = SecretVault(vault_dir=vault_dir)
    service = SecretsService(socket_path=sock, vault=vault)
    service.start()

    def handle_signal(sig, frame):
        service.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    while True:
        time.sleep(3600)


if __name__ == "__main__":
    main()
