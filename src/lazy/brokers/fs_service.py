"""Filesystem & Document broker service for lazy-broker-fs."""
from __future__ import annotations

import os
from pathlib import Path
from lazy.brokers.fs_broker import FSBroker
from lazy.common.socket_server import UnixSocketServer, parse_socket_arg


def main():
    sock = parse_socket_arg("broker-fs")
    root = os.environ.get("LAZY_FS_ROOT", "/data/home/lazy")
    broker = FSBroker(root_dir=root)
    srv = UnixSocketServer(sock, service_name="lazy-broker-fs")
    srv.register_broker(broker)
    srv.serve_forever()


if __name__ == "__main__":
    main()
