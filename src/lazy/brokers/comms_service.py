"""Communications broker service for lazy-broker-comms."""
from __future__ import annotations

import os
from pathlib import Path
from lazy.brokers.comms_broker import CommsBroker
from lazy.common.socket_server import UnixSocketServer, parse_socket_arg


def main():
    sock = parse_socket_arg("broker-comms")
    storage = os.environ.get("LAZY_COMMS_STORAGE", "/data")
    maildir = os.path.join(storage, "mail")
    broker = CommsBroker(maildir_root=maildir)
    srv = UnixSocketServer(sock, service_name="lazy-broker-comms")
    srv.register_broker(broker)
    srv.serve_forever()


if __name__ == "__main__":
    main()
