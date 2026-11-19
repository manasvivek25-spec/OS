"""Hardware control broker service for lazy-broker-hw."""
from __future__ import annotations

import os
from pathlib import Path
from lazy.brokers.hw_broker import HWBroker
from lazy.common.socket_server import UnixSocketServer, parse_socket_arg


def main():
    sock = parse_socket_arg("broker-hw")
    sysfs = os.environ.get("LAZY_SYSFS_PATH", "/sys")
    broker = HWBroker(sysfs_root=sysfs)
    srv = UnixSocketServer(sock, service_name="lazy-broker-hw")
    srv.register_broker(broker)
    srv.serve_forever()


if __name__ == "__main__":
    main()
