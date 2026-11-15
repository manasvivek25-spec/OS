#!/usr/bin/env bash
for ep in identity build-info metrics services tasks approvals audit capabilities briefing settings; do
    code=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:8766/api/${ep}")
    echo "/api/${ep} -> HTTP ${code}"
done
code_fs=$(curl -s -o /dev/null -w "%{http_code}" "http://127.0.0.1:8766/api/fs?path=/data")
echo "/api/fs?path=/data -> HTTP ${code_fs}"
