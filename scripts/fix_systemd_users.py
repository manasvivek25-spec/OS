import glob
import re

mapping = {
    r"\blazy-pol\b": "lazy-policy",
    r"\blazy-plan\b": "lazy-planner",
    r"\blazy-task\b": "lazy-tasks",
    r"\blazy-rout\b": "lazy-routines",
    r"\blazy-fetch\b": "lazy-fetcher",
    r"\blazy-brk-comms\b": "lazy-broker-comms",
    r"\blazy-brk-fs\b": "lazy-broker-fs",
    r"\blazy-brk-hw\b": "lazy-broker-hw",
    r"\blazy-brk-sys\b": "lazy-broker-sys",
    r"\blazy-brk-web\b": "lazy-broker-web",
}

for path in glob.glob("/mnt/c/Users/len/OS/systemd/lazy-*.service"):
    with open(path, "r") as f:
        content = f.read()
    orig = content
    for pattern, repl in mapping.items():
        content = re.sub(pattern, repl, content)
    if content != orig:
        with open(path, "w") as f:
            f.write(content)
        print(f"Updated {path}")
