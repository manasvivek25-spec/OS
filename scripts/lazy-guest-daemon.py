#!/usr/bin/python3
import os
import sys
import time
from pathlib import Path
from lazy.gateway.server import GatewayServer

def main():
    hud_dir = Path("/usr/share/lazy/hud")
    repo_root = Path("/")
    server = GatewayServer(host="0.0.0.0", port=8765, hud_dir=hud_dir)
    server.api_handler.repo_root = repo_root
    server.api_handler.data_dir = Path("/data")
    server.start()
    print("Lazy OS Gateway Daemon online on 0.0.0.0:8765")
    while True:
        try:
            time.sleep(3600)
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
