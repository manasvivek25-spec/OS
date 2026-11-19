"""Web broker service for lazy-broker-web."""
from __future__ import annotations

import os
from pathlib import Path
from lazy.brokers.web_broker import WebBroker
from lazy.common.socket_server import UnixSocketServer, parse_socket_arg


def main():
    sock = parse_socket_arg("broker-web")
    quarantine = os.environ.get("LAZY_QUARANTINE_DIR", "/data/quarantine")
    broker = WebBroker(quarantine_dir=quarantine)
    srv = UnixSocketServer(sock, service_name="lazy-broker-web")
    srv.register_broker(broker)
    srv.serve_forever()


if __name__ == "__main__":
    main()
