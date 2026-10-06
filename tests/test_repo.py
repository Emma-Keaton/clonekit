"""Repository contract: the skill tree, its metadata, and the docs that index it."""

import os
import re
import unittest

from _load import ROOT, SKILLS

SKILLS_LIST = ["clonekit", "clonekit-recon", "clonekit-architect",
               "clonekit-design", "clonekit-build", "clonekit-backend",
               "clonekit-test", "clonekit-diff", "clonekit-entrepreneur",
               "clonekit-brand", "clonekit-launch", "clonekit-deploy"]

# Agent product names must not appear anywhere in the skill tree: the skills
# are agent-neutral. Word boundaries keep "declined" from matching "cline".
BANNED = [r"\bclaude\b", r"\bcursor\b", r"\bcopilot\b", r"\bcline\b",
          r"\bqwen\b", r"\bgemini\b", r"\bopencode\b", r"\bwindsurf\b",
          r"\baider\b"]

TOOLS = ["clonekit-diff/parity.py", "clonekit-diff/imgdiff.py",
         "clonekit-design/contrast.py", "clonekit-entrepreneur/reviews.py",
         "clonekit-brand/sweep.py", "clonekit-launch/listing.py"]

SKILL_MD = ".md", ".py", ".json", ".csv", ".ts"


def frontmatter(path):
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return (m.group(1) if m else ""), text


class SkillTree(unittest.TestCase):
    def test_twelve_skill_folders(self):
        found = sorted(d for d in os.listdir(SKILLS)
                       if os.path.isfile(os.path.join(SKILLS, d, "SKILL.md")))
        self.assertEqual(found, sorted(SKILLS_LIST))

    def test_frontmatter_name_and_description(self):
        for s in SKILLS_LIST:
            fm, _ = frontmatter(os.path.join(SKILLS, s, "SKILL.md"))
            self.assertIn("name: %s\n" % s, fm + "\n", s)
            m = re.search(r"^description: >-\n((?:  .*\n)+)", fm, re.M)
            self.assertTrue(m, "%s: no folded description" % s)
            desc = " ".join(line.strip() for line in m.group(1).splitlines())
            self.assertGreater(len(desc), 200, "%s description is too thin" % s)

    def test_contract_sections_present(self):
        for s in SKILLS_LIST:
            _, text = frontmatter(os.path.join(SKILLS, s, "SKILL.md"))
            for section in ("## Reads and writes", "## Done when", "## Handoff"):
                self.assertIn(section, text, "%s is missing '%s'" % (s, section))
            self.assertGreater(len(text.splitlines()), 60, s)
            self.assertLess(len(text.splitlines()), 220,
                            "%s is too long for progressive disclosure" % s)

    def test_no_agent_names_in_the_skill_tree(self):
        pats = [(p, re.compile(p, re.I)) for p in BANNED]
        hits = []
        for dirpath, dirnames, filenames in os.walk(SKILLS):
            dirnames[:] = [d for d in dirnames if d != "__pycache__"]
            for fn in sorted(filenames):
                if not fn.endswith(SKILL_MD):
                    continue
                path = os.path.join(dirpath, fn)
                with open(path, encoding="utf-8", errors="replace") as fh:
                    for i, line in enumerate(fh, 1):
                        for pat, rx in pats:
                            if rx.search(line):
                                hits.append("%s:%d [%s] %s" % (
                                    os.path.relpath(path, ROOT), i, pat,
                                    line.strip()[:70]))
        self.assertEqual(hits, [], "\n" + "\n".join(hits))

    def test_companion_files_referenced_by_skills_exist(self):
        ref = re.compile(r"(clonekit-[a-z0-9-]+/[\w.-]*\.(?:md|py|csv|json|ts))")
        missing = []
        for s in SKILLS_LIST:
            path = os.path.join(SKILLS, s, "SKILL.md")
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
            for m in ref.finditer(text):
                if not os.path.isfile(os.path.join(SKILLS, m.group(1))):
                    missing.append("%s references missing %s" % (s, m.group(1)))
        self.assertEqual(missing, [], "\n" + "\n".join(missing))

    def test_tools_present(self):
        for rel in TOOLS:
            self.assertTrue(os.path.isfile(os.path.join(SKILLS, rel)), rel)
        self.assertTrue(os.path.isfile(os.path.join(ROOT, "bin", "replica")))
        self.assertTrue(os.path.isfile(os.path.join(ROOT, "install.sh")))


class DocsIndexEverything(unittest.TestCase):
    def test_every_skill_indexed_in_agents_md_and_readme(self):
        for doc in ("AGENTS.md", "README.md"):
            with open(os.path.join(ROOT, doc), encoding="utf-8") as fh:
                text = fh.read()
            for s in SKILLS_LIST:
                self.assertIn(s, text, "%s does not index %s" % (doc, s))

    def test_readme_carries_credit_and_fine_print(self):
        with open(os.path.join(ROOT, "README.md"), encoding="utf-8") as fh:
            readme = fh.read()
        self.assertIn("Jake Schincariol", readme)
        self.assertIn("replica-skill", readme)
        for section in ("## Install", "## The twelve skills", "## Tools",
                        "## Ground rules", "## License"):
            self.assertIn(section, readme)

    def test_license_retains_original_copyright(self):
        with open(os.path.join(ROOT, "LICENSE"), encoding="utf-8") as fh:
            license_text = fh.read()
        self.assertIn("Jake Schincariol", license_text)
        self.assertIn("MIT License", license_text)

    def test_no_em_dashes_anywhere(self):
        bad = []
        for dirpath, dirnames, filenames in os.walk(ROOT):
            dirnames[:] = [d for d in dirnames
                           if d not in (".git", "__pycache__", ".agents")]
            for fn in filenames:
                if fn.endswith((".md", ".py", ".json", ".ts", ".csv")):
                    path = os.path.join(dirpath, fn)
                    with open(path, encoding="utf-8", errors="replace") as fh:
                        if chr(0x2014) in fh.read():
                            bad.append(os.path.relpath(path, ROOT))
        self.assertEqual(bad, [])
        # the skill tree is checked too
        bad = []
        for dirpath, dirnames, filenames in os.walk(SKILLS):
            dirnames[:] = [d for d in dirnames if d != "__pycache__"]
            for fn in filenames:
                if fn.endswith((".md", ".py", ".json", ".ts", ".csv")):
                    path = os.path.join(dirpath, fn)
                    with open(path, encoding="utf-8", errors="replace") as fh:
                        if chr(0x2014) in fh.read():
                            bad.append(os.path.relpath(path, ROOT))
        self.assertEqual(bad, [])


if __name__ == "__main__":
    unittest.main()
