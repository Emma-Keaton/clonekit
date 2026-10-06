#!/usr/bin/env python3
"""Supercharge frontmatter: add spec fields from agentskills.io to every
SKILL.md -- license (MIT), metadata (version 2.0.0, role), and compatibility
on the skills that ship Python tools. allowed-tools is deliberately omitted:
it is experimental in the spec and its tool vocabularies differ per agent."""
import os
import re

ROOT = ".agents/skills"

ROLES = {
    "clonekit": "workflow-orchestrator",
    "clonekit-recon": "clean-room-specifier",
    "clonekit-architect": "software-architect",
    "clonekit-design": "design-systems-engineer",
    "clonekit-build": "frontend-build-engineer",
    "clonekit-backend": "backend-systems-engineer",
    "clonekit-test": "qa-automation-engineer",
    "clonekit-diff": "verification-evaluator",
    "clonekit-entrepreneur": "product-strategist",
    "clonekit-brand": "brand-identity-director",
    "clonekit-launch": "growth-marketing-lead",
    "clonekit-deploy": "devops-release-engineer",
}

# skills whose SKILL.md tells the agent to run the bundled Python tools
TOOL_SKILLS = {
    "clonekit-design", "clonekit-diff", "clonekit-entrepreneur",
    "clonekit-brand", "clonekit-launch", "clonekit-deploy",
    "clonekit",
}

for name, role in ROLES.items():
    path = os.path.join(ROOT, name, "SKILL.md")
    with open(path, encoding="utf-8") as fh:
        text = fh.read().replace("\r\n", "\n")
    if "metadata:" in text:
        print("skip (already done): %s" % path)
        continue
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        raise SystemExit("%s: no frontmatter" % path)
    if "name: %s\n" % name not in m.group(1):
        raise SystemExit("%s: frontmatter name mismatch" % path)
    add = ["license: MIT"]
    if name in TOOL_SKILLS:
        add.append("compatibility: Requires Python 3.8+ and bash for the bundled "
                   "./bin/replica tools.")
    add += ["metadata:", '  version: "2.0.0"', "  role: %s" % role]
    insert_at = m.start(1) + len(m.group(1)) + 1  # position of closing ---
    text = text[:insert_at] + "\n".join(add) + "\n" + text[insert_at:]
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    print("frontmatter: %s (+%d lines)" % (path, len(add)))
