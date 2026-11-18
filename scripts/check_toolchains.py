import urllib.request
import re

try:
    url = 'https://toolchains.bootlin.com/downloads/releases/toolchains/x86-64/tarballs/'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
    matches = sorted(list(set(re.findall(r'x86-64--glibc--[^\"]*tar\.xz', html))))
    print("Found toolchains:")
    for m in matches[-10:]:
        print(" -", m)
except Exception as e:
    print("Error:", e)
