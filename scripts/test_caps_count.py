import urllib.request
import json

data = json.loads(urllib.request.urlopen('http://127.0.0.1:8766/api/capabilities').read())
print("Total capabilities in live guest:", len(data))
print("hw.backlight_set present:", any(c.get("name") == "hw.backlight_set" for c in data))
