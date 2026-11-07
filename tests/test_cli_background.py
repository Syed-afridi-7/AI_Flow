"""Integration and Unit Tests for Background Agent CLI and run.py Commands.

Tests cover:
1. engine.cli --background / -bg (human-readable and JSON)
2. engine.cli --list-tasks (human-readable and JSON)
3. engine.cli --status (human-readable, JSON, and nonexistent task handling)
4. engine.cli --logs (human-readable, JSON, tail truncation)
5. engine.cli --cancel (human-readable, JSON, and nonexistent task handling)
6. engine.cli --prune-tasks (human-readable and JSON)
7. scripts/run.py background dispatch, provider propagation, and task management
8. Non-blocking verification (< 3.0s command execution)
9. File input reading for background tasks
"""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest


class TestCliBackground(unittest.TestCase):
    """Test background dispatch and management CLI commands in engine.cli and scripts/run.py."""

    def test_cli_background_dispatch_human(self):
        cmd = [
            sys.executable,
            "-m",
            "engine.cli",
            "--skill",
            "prd-generator",
            "--input",
            "Test human background dispatch",
            "--background",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        self.assertEqual(res.returncode, 0, f"Error: {res.stderr}")
        self.assertIn("AI_FLOW BACKGROUND AGENT DISPATCHED", res.stdout)
        self.assertIn("Task ID:", res.stdout)
        self.assertIn("Worker PID:", res.stdout)
        self.assertIn("Skill:", res.stdout)
        self.assertIn("prd-generator", res.stdout)
        self.assertIn("Mode:", res.stdout)

    def test_cli_background_dispatch_json(self):
        cmd = [
            sys.executable,
            "-m",
            "engine.cli",
            "--skill",
            "prd-generator",
            "--input",
            "Test JSON background dispatch",
            "--background",
            "--json",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        self.assertEqual(res.returncode, 0, f"Error: {res.stderr}")
        data = json.loads(res.stdout)
        self.assertEqual(data.get("status"), "dispatched")
        self.assertEqual(data.get("skill"), "prd-generator")
        self.assertTrue(data.get("task_id", "").startswith("task_"))
        self.assertIsNotNone(data.get("pid"))
        self.assertEqual(data.get("provider"), "local")
        self.assertEqual(data.get("mode"), "dual")

    def test_cli_background_short_flag(self):
        cmd = [
            sys.executable,
            "-m",
            "engine.cli",
            "--skill",
            "backend-schema",
            "--input",
            "Short flag dispatch",
            "-bg",
            "--json",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        self.assertEqual(res.returncode, 0, f"Error: {res.stderr}")
        data = json.loads(res.stdout)
        self.assertEqual(data.get("status"), "dispatched")
        self.assertEqual(data.get("skill"), "backend-schema")

    def test_cli_background_missing_skill(self):
        # Missing --skill should fail
        cmd = [
            sys.executable,
            "-m",
            "engine.cli",
            "--background",
            "--json",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        self.assertNotEqual(res.returncode, 0)
        data = json.loads(res.stdout)
        self.assertIn("error", data)

        # Human-readable format
        cmd_human = [
            sys.executable,
            "-m",
            "engine.cli",
            "--background",
        ]
        res_human = subprocess.run(cmd_human, capture_output=True, text=True, timeout=10)
        self.assertNotEqual(res_human.returncode, 0)
        self.assertIn("Error: --skill is required", res_human.stdout)

    def test_cli_background_invalid_skill(self):
        cmd = [
            sys.executable,
            "-m",
            "engine.cli",
            "--skill",
            "mythical-nonexistent-skill-xyz",
            "--background",
            "--json",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        self.assertNotEqual(res.returncode, 0)
        data = json.loads(res.stdout)
        self.assertIn("error", data)

    def test_cli_list_tasks_human_and_json(self):
        # Human-readable table
        cmd = [sys.executable, "-m", "engine.cli", "--list-tasks"]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        self.assertEqual(res.returncode, 0, f"Error: {res.stderr}")
        self.assertIn("Background Tasks", res.stdout)
        self.assertIn("TASK ID", res.stdout)

        # JSON format
        cmd_json = [sys.executable, "-m", "engine.cli", "--list-tasks", "--json"]
        res_json = subprocess.run(cmd_json, capture_output=True, text=True, timeout=10)
        self.assertEqual(res_json.returncode, 0, f"Error: {res_json.stderr}")
        tasks = json.loads(res_json.stdout)
        self.assertIsInstance(tasks, list)

    def test_cli_status_human_and_json(self):
        # First dispatch a task
        cmd_dispatch = [
            sys.executable,
            "-m",
            "engine.cli",
            "--skill",
            "prd-generator",
            "--input",
            "Status testing prompt",
            "--background",
            "--json",
        ]
        res_dispatch = subprocess.run(cmd_dispatch, capture_output=True, text=True, timeout=10)
        self.assertEqual(res_dispatch.returncode, 0)
        task_id = json.loads(res_dispatch.stdout)["task_id"]

        # Check status human-readable
        cmd_status = [sys.executable, "-m", "engine.cli", "--status", task_id]
        res_status = subprocess.run(cmd_status, capture_output=True, text=True, timeout=10)
        self.assertEqual(res_status.returncode, 0, f"Error: {res_status.stderr}")
        self.assertIn("Background Task Status", res_status.stdout)
        self.assertIn(task_id, res_status.stdout)

        # Check status JSON
        cmd_status_json = [sys.executable, "-m", "engine.cli", "--status", task_id, "--json"]
        res_status_json = subprocess.run(cmd_status_json, capture_output=True, text=True, timeout=10)
        self.assertEqual(res_status_json.returncode, 0, f"Error: {res_status_json.stderr}")
        status_data = json.loads(res_status_json.stdout)
        self.assertEqual(status_data["task_id"], task_id)
        self.assertEqual(status_data["skill_name"], "prd-generator")
        self.assertIn(status_data["status"], ("running", "completed", "failed", "cancelled"))

    def test_cli_status_nonexistent(self):
        cmd = [sys.executable, "-m", "engine.cli", "--status", "task_nonexistent_88888888"]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        self.assertEqual(res.returncode, 1)
        self.assertIn("Error: Task 'task_nonexistent_88888888' not found", res.stdout)

        cmd_json = [sys.executable, "-m", "engine.cli", "--status", "task_nonexistent_88888888", "--json"]
        res_json = subprocess.run(cmd_json, capture_output=True, text=True, timeout=10)
        self.assertEqual(res_json.returncode, 1)
        data = json.loads(res_json.stdout)
        self.assertIn("error", data)

    def test_cli_logs_human_and_json(self):
        # Dispatch a task
        cmd_dispatch = [
            sys.executable,
            "-m",
            "engine.cli",
            "--skill",
            "prd-generator",
            "--input",
            "Logs testing prompt",
            "--background",
            "--json",
        ]
        res_dispatch = subprocess.run(cmd_dispatch, capture_output=True, text=True, timeout=10)
        task_id = json.loads(res_dispatch.stdout)["task_id"]

        # Human-readable logs
        cmd_logs = [sys.executable, "-m", "engine.cli", "--logs", task_id, "--tail", "10"]
        res_logs = subprocess.run(cmd_logs, capture_output=True, text=True, timeout=10)
        self.assertEqual(res_logs.returncode, 0)

        # JSON logs
        cmd_logs_json = [sys.executable, "-m", "engine.cli", "--logs", task_id, "--tail", "10", "--json"]
        res_logs_json = subprocess.run(cmd_logs_json, capture_output=True, text=True, timeout=10)
        self.assertEqual(res_logs_json.returncode, 0)
        data = json.loads(res_logs_json.stdout)
        self.assertEqual(data["task_id"], task_id)
        self.assertEqual(data["tail"], 10)
        self.assertIn("logs", data)

    def test_cli_cancel_human_and_json(self):
        # Dispatch a task
        cmd_dispatch = [
            sys.executable,
            "-m",
            "engine.cli",
            "--skill",
            "prd-generator",
            "--input",
            "Cancel testing prompt 1",
            "--background",
            "--json",
        ]
        res_dispatch = subprocess.run(cmd_dispatch, capture_output=True, text=True, timeout=10)
        task_id = json.loads(res_dispatch.stdout)["task_id"]

        # Human-readable cancel
        cmd_cancel = [sys.executable, "-m", "engine.cli", "--cancel", task_id]
        res_cancel = subprocess.run(cmd_cancel, capture_output=True, text=True, timeout=10)
        self.assertEqual(res_cancel.returncode, 0)
        self.assertIn(task_id, res_cancel.stdout)

        # Dispatch another task for JSON cancel
        res_dispatch2 = subprocess.run(cmd_dispatch, capture_output=True, text=True, timeout=10)
        task_id2 = json.loads(res_dispatch2.stdout)["task_id"]

        cmd_cancel_json = [sys.executable, "-m", "engine.cli", "--cancel", task_id2, "--json"]
        res_cancel_json = subprocess.run(cmd_cancel_json, capture_output=True, text=True, timeout=10)
        self.assertEqual(res_cancel_json.returncode, 0)
        data = json.loads(res_cancel_json.stdout)
        self.assertEqual(data["task_id"], task_id2)
        self.assertIn("cancelled", data)

    def test_cli_cancel_nonexistent(self):
        cmd = [sys.executable, "-m", "engine.cli", "--cancel", "task_nonexistent_cancel_999"]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        self.assertEqual(res.returncode, 1)

        cmd_json = [sys.executable, "-m", "engine.cli", "--cancel", "task_nonexistent_cancel_999", "--json"]
        res_json = subprocess.run(cmd_json, capture_output=True, text=True, timeout=10)
        self.assertEqual(res_json.returncode, 1)
        data = json.loads(res_json.stdout)
        self.assertFalse(data["cancelled"])
        self.assertIn("error", data)

    def test_cli_prune_tasks_human_and_json(self):
        cmd = [sys.executable, "-m", "engine.cli", "--prune-tasks", "--days", "30"]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        self.assertEqual(res.returncode, 0)
        self.assertIn("Pruned", res.stdout)

        cmd_json = [sys.executable, "-m", "engine.cli", "--prune-tasks", "--days", "30", "--json"]
        res_json = subprocess.run(cmd_json, capture_output=True, text=True, timeout=10)
        self.assertEqual(res_json.returncode, 0)
        data = json.loads(res_json.stdout)
        self.assertIn("pruned_count", data)
        self.assertEqual(data["older_than_days"], 30)

    def test_run_py_background_dispatch(self):
        cmd = [
            sys.executable,
            "scripts/run.py",
            "--skill",
            "prd-generator",
            "--input",
            "Testing run.py background dispatch",
            "--background",
            "--json",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        self.assertEqual(res.returncode, 0, f"Error: {res.stderr}")
        data = json.loads(res.stdout)
        self.assertEqual(data.get("status"), "dispatched")
        self.assertEqual(data.get("skill"), "prd-generator")
        self.assertEqual(data.get("provider"), "local")
        task_id = data.get("task_id")
        self.assertIsNotNone(task_id)

        # Status via run.py
        cmd_status = [sys.executable, "scripts/run.py", "--status", task_id]
        res_status = subprocess.run(cmd_status, capture_output=True, text=True, timeout=10)
        self.assertEqual(res_status.returncode, 0)
        self.assertIn(task_id, res_status.stdout)

        # List via run.py
        cmd_list = [sys.executable, "scripts/run.py", "--list-tasks"]
        res_list = subprocess.run(cmd_list, capture_output=True, text=True, timeout=10)
        self.assertEqual(res_list.returncode, 0)
        self.assertIn("Background Tasks", res_list.stdout)

    def test_run_py_background_with_provider_and_short_flag(self):
        cmd = [
            sys.executable,
            "scripts/run.py",
            "--skill",
            "prd-generator",
            "--input",
            "Testing provider metadata propagation",
            "--provider",
            "ollama",
            "-bg",
            "--json",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        self.assertEqual(res.returncode, 0, f"Error: {res.stderr}")
        data = json.loads(res.stdout)
        self.assertEqual(data.get("status"), "dispatched")
        self.assertEqual(data.get("provider"), "ollama")

    def test_run_py_background_human_output(self):
        cmd = [
            sys.executable,
            "scripts/run.py",
            "--skill",
            "prd-generator",
            "--input",
            "Testing human output from run.py",
            "-bg",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        self.assertEqual(res.returncode, 0, f"Error: {res.stderr}")
        self.assertIn("AI_FLOW BACKGROUND AGENT DISPATCHED", res.stdout)
        self.assertIn("Task ID:", res.stdout)
        self.assertIn("Worker PID:", res.stdout)

    def test_background_non_blocking_performance(self):
        """Verify that CLI background dispatch returns almost immediately (< 3.0s)."""
        start = time.time()
        cmd = [
            sys.executable,
            "-m",
            "engine.cli",
            "--skill",
            "prd-generator",
            "--input",
            "Quick latency check",
            "--background",
            "--json",
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        duration = time.time() - start
        self.assertEqual(res.returncode, 0)
        self.assertLess(duration, 3.0, f"Background dispatch took too long: {duration:.2f}s")

    def test_background_dispatch_file_input(self):
        """Verify prompt is loaded when a valid file path is given to --input."""
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, suffix=".txt") as tf:
            tf.write("Custom instructions inside a file for background task execution.")
            temp_path = tf.name

        try:
            cmd = [
                sys.executable,
                "-m",
                "engine.cli",
                "--skill",
                "backend-schema",
                "--input",
                temp_path,
                "--background",
                "--json",
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            self.assertEqual(res.returncode, 0)
            data = json.loads(res.stdout)
            self.assertEqual(data.get("status"), "dispatched")
        finally:
            Path(temp_path).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
