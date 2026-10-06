#!/usr/bin/env python3
"""One-shot extraction: pull FILE blocks out of jakeschincariol-replica-skill.txt,
rename replica-* skill folders to .agents/skills/clonekit-*, and rewrite the word
'replica' to 'clonekit' throughout. Skips README/LICENSE/plugin manifests (rewritten
from scratch for clonekit)."""
import os
import re

SRC = "jakeschincariol-replica-skill.txt"
SKIP = {"README.md", "LICENSE"}

text = open(SRC, encoding="utf-8", newline="").read()
text = text.replace("\r\n", "\n").replace("\r", "\n")
parts = re.split(r"={20,}\nFILE: (.*?)\n={20,}\n", text)
written = []
for i in range(1, len(parts), 2):
    name = parts[i].strip()
    body = parts[i + 1]
    if name in SKIP or name.startswith(".claude-plugin/"):
        continue
    if name.startswith("replica-"):
        name = ".agents/skills/clonekit-" + name[len("replica-"):]
    body = body.replace("replica_", "clonekit_")
    body = re.sub(r"\breplica\b", "clonekit", body)
    body = re.sub(r"\bReplica\b", "clonekit", body)
    body = body.rstrip() + "\n"
    path = name
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(body)
    written.append(path)

print("wrote %d files" % len(written))
for p in written:
    print("  " + p)
