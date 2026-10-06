"""install.sh: real run into a temp project, file-style rules targets, idempotency."""

import os
import shutil
import subprocess
import tempfile
import unittest

from _load import ROOT

BASH = shutil.which("bash")
INSTALL = os.path.join(ROOT, "install.sh")
MARK = "<!-- clonekit:begin -->"


@unittest.skipUnless(BASH, "bash is required to run install.sh")
class Install(unittest.TestCase):
    def run_install(self, dest, *args):
        return subprocess.run([BASH, INSTALL] + list(args), cwd=dest,
                              capture_output=True, text=True)

    def markers(self, path):
        with open(path, encoding="utf-8") as fh:
            return fh.read().count(MARK)

    def test_real_run_file_rules_targets_and_idempotency(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, ".claude"))
            os.makedirs(os.path.join(d, ".windsurf"))
            # rules paths as plain files, the documented convention
            for rel, content in ((".roorules", "roo rules\n"),
                                 (".clinerules", "# cline rules\nkeep me too\n"),
                                 ("AGENTS.md", "# my rules\nkeep me\n")):
                with open(os.path.join(d, rel), "w", encoding="utf-8") as fh:
                    fh.write(content)

            r = self.run_install(d)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertTrue(os.path.isfile(
                os.path.join(d, ".claude", "skills", "clonekit", "SKILL.md")))

            windsurf = os.path.join(d, ".windsurfrules")
            for f in (windsurf, os.path.join(d, ".roorules"),
                      os.path.join(d, ".clinerules"),
                      os.path.join(d, "AGENTS.md")):
                with open(f, encoding="utf-8") as fh:
                    self.assertIn(MARK, fh.read(), f)

            # existing file content preserved, with a backup of AGENTS.md
            with open(os.path.join(d, ".clinerules"), encoding="utf-8") as fh:
                self.assertIn("keep me too", fh.read())
            with open(os.path.join(d, "AGENTS.md"), encoding="utf-8") as fh:
                self.assertIn("keep me", fh.read())
            self.assertTrue(os.path.isfile(os.path.join(d, "AGENTS.md.bak")))

            # a second run must not duplicate blocks or backups
            r2 = self.run_install(d)
            self.assertEqual(r2.returncode, 0, r2.stdout + r2.stderr)
            for f in (windsurf, os.path.join(d, ".roorules"),
                      os.path.join(d, ".clinerules"),
                      os.path.join(d, "AGENTS.md")):
                self.assertEqual(self.markers(f), 1, f)
            backups = [n for n in os.listdir(d) if n.startswith("AGENTS.md.bak")]
            self.assertEqual(len(backups), 1)

    def test_dry_run_changes_nothing(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, ".claude"))
            r = self.run_install(d, "--dry-run")
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertFalse(os.path.exists(os.path.join(d, ".claude", "skills")))
            self.assertFalse(os.path.exists(os.path.join(d, "AGENTS.md")))

    def test_unknown_option_exits_2(self):
        with tempfile.TemporaryDirectory() as d:
            r = self.run_install(d, "--frobnicate")
            self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
