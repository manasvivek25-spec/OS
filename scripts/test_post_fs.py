import urllib.request, json
req = urllib.request.Request("http://127.0.0.1:8766/api/fs", data=b'{"path": "/data/test.txt", "content": "hello"}', headers={"Content-Type": "application/json"}, method="POST")
try:
    resp = urllib.request.urlopen(req)
    print("STATUS:", resp.status, resp.read().decode())
except urllib.error.HTTPError as e:
    print("HTTP ERROR:", e.code, e.read().decode())
