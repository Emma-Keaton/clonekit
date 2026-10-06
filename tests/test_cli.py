"""The unified CLI wrapper: dispatch, help, doctor, and real tool runs."""

import os
import shutil
import subprocess
import unittest

from _load import ROOT

BASH = shutil.which("bash")
BIN = os.path.join(ROOT, "bin", "replica")


def run(*args):
    return subprocess.run([BASH, BIN] + list(args), cwd=ROOT,
                          capture_output=True, text=True)


@unittest.skipUnless(BASH, "bash is required to run bin/replica")
class Cli(unittest.TestCase):
    def test_help_lists_every_command(self):
        r = run("--help")
        self.assertEqual(r.returncode, 0, r.stderr)
        for cmd in ("parity", "imgdiff", "contrast", "reviews", "sweep",
                    "listing", "doctor"):
            self.assertIn(cmd, r.stdout)

    def test_unknown_command_exits_2(self):
        r = run("frobnicate")
        self.assertEqual(r.returncode, 2)
        self.assertIn("unknown command", r.stderr)

    def test_doctor_reports_healthy_environment(self):
        r = run("doctor")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("12 SKILL.md", r.stdout)
        self.assertEqual(r.stdout.count("tool ok"), 6, r.stdout)
        self.assertNotIn("FAIL", r.stdout)

    def test_parity_runs_on_the_shipped_template(self):
        r = run("parity", ".agents/skills/clonekit-recon/features.csv")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("Parity", r.stdout)

    def test_contrast_runs_on_the_shipped_tokens(self):
        r = run("contrast", ".agents/skills/clonekit-design/tokens.json")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_listing_runs_on_the_shipped_example(self):
        r = run("listing", ".agents/skills/clonekit-launch/listing.example.json")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_sweep_with_nothing_to_find_exits_2(self):
        r = run("sweep", ".")
        self.assertEqual(r.returncode, 2)
        self.assertIn("nothing to look for", r.stderr)


if __name__ == "__main__":
    unittest.main()
