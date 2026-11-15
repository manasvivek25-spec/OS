import json

path = "/mnt/c/Users/len/.gemini/antigravity/brain/9e8c7043-33d9-4a95-b40b-11e2da524dc0/.system_generated/logs/transcript_full.jsonl"
with open(path, "r", encoding="utf-8") as f:
    for line in f:
        try:
            data = json.loads(line)
            content = data.get("content", "")
            if "LAZY OS V2 PROMPT" in content:
                print("FOUND PROMPT at step", data.get("step_index"))
                with open("/mnt/c/Users/len/OS/docs/V2_PROMPT.txt", "w", encoding="utf-8") as out:
                    out.write(content)
                print("Saved to docs/V2_PROMPT.txt, length:", len(content))
                break
        except Exception as e:
            pass
