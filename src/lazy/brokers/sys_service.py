"""System administration broker service for lazy-broker-sys."""
from __future__ import annotations

import os
from pathlib import Path
from lazy.brokers.sys_broker import SysBroker
from lazy.common.socket_server import UnixSocketServer, parse_socket_arg


def main():
    sock = parse_socket_arg("broker-sys")
    broker = SysBroker()
    srv = UnixSocketServer(sock, service_name="lazy-broker-sys")
    srv.register_broker(broker)
    srv.serve_forever()


if __name__ == "__main__":
    main()
