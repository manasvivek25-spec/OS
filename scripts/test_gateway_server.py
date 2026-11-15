import json
import time
import urllib.request
from pathlib import Path
from lazy.gateway.server import GatewayServer

server = GatewayServer(host="127.0.0.1", port=9876, hud_dir=Path("hud"))
server.start()
try:
    time.sleep(0.5)
    for ep in ["identity", "build-info", "metrics", "services", "tasks", "approvals", "capabilities", "briefing", "settings"]:
        data = urllib.request.urlopen(f"http://127.0.0.1:9876/api/{ep}").read()
        parsed = json.loads(data)
        print(f"/api/{ep}: OK ({len(parsed)} keys/items)")
finally:
    server.stop()
