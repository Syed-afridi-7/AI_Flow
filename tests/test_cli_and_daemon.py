import unittest
import subprocess
import sys
import json
from pathlib import Path


class TestCliAndDaemon(unittest.TestCase):
    def test_cli_list_command(self):
        cmd = [sys.executable, "-m", "engine.cli", "--list"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("Registered Skills (30 Skills, 60 Agents)", res.stdout)
        self.assertIn("prd-generator", res.stdout)
        self.assertIn("executive-time-ledger", res.stdout)

    def test_cli_run_skill_dual_mode(self):
        cmd = [
            sys.executable,
            "-m",
            "engine.cli",
            "--skill",
            "backend-schema",
            "--input",
            "Orders and Customers database",
            "--mode",
            "dual"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("Generator", res.stdout)
        self.assertIn("Validator", res.stdout)
        self.assertIn("Scorecard", res.stdout)
        self.assertIn("PASSED", res.stdout)

    def test_cli_run_skill_single_mode(self):
        cmd = [
            sys.executable,
            "-m",
            "engine.cli",
            "--skill",
            "prd-generator",
            "--input",
            "Simple Todo App",
            "--mode",
            "single"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(res.returncode, 0)
        self.assertIn("Single mode", res.stdout)


if __name__ == "__main__":
    unittest.main()
