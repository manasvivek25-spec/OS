import sys
sys.path.insert(0, '/mnt/c/Users/len/OS/src')
from lazy.gateway.api import GatewayAPIHandler
import json

handler = GatewayAPIHandler(repo_root='/mnt/c/Users/len/OS')
status, headers, body = handler._get_capabilities()
data = json.loads(body.decode('utf-8'))
print(f"Status: {status}, Count: {len(data)}")
if len(data) > 0:
    print("First item:", data[0])
