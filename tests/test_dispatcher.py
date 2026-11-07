"""Comprehensive Unit Tests for Universal Detached Agent Dispatcher (engine.core.dispatcher).

Tests:
1. Dispatcher initialization and directory scaffolding.
2. Background process spawning (Windows flags, Unix session flags, command arguments).
3. Non-blocking dispatch performance (< 50ms).
4. Spooling of large input prompts (> 200 characters).
5. Dead PID detection and automatic task reconciliation.
6. Task status inspection.
7. Task cancellation for running and terminal tasks.
8. Log retrieval with tail truncation.
9. Task listing, filtering, and pruning.
"""

from datetime import datetime, timezone, timedelta
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import MagicMock, patch
import warnings

from engine.core.dispatcher import (
    AgentDispatcher,
    DETACHED_PROCESS,
    CREATE_NEW_PROCESS_GROUP,
)
from engine.core.task_manager import TaskManager, TaskRecord


class TestAgentDispatcher(unittest.TestCase):
    def setUp(self) -> None:
        warnings.simplefilter("ignore", ResourceWarning)
        self.test_dir = Path(tempfile.mkdtemp())
        self.db_path = self.test_dir / "tasks.db"
        self.log_dir = self.test_dir / "logs"
        self.spool_dir = self.test_dir / "spool"
        self.output_dir = self.test_dir / "output"

        self.dispatcher = AgentDispatcher(
            db_path=self.db_path,
            log_dir=self.log_dir,
            spool_dir=self.spool_dir,
            output_dir=self.output_dir,
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_initialization_creates_directories(self) -> None:
        """Verify initialization scaffolded all necessary storage directories."""
        self.assertTrue(self.db_path.parent.exists())
        self.assertTrue(self.log_dir.is_dir())
        self.assertTrue(self.spool_dir.is_dir())
        self.assertTrue(self.output_dir.is_dir())
        self.assertEqual(self.dispatcher.db_path, self.db_path)

    @patch("subprocess.Popen")
    def test_dispatch_spawns_process_with_correct_args(self, mock_popen: MagicMock) -> None:
        """Verify command arguments, initial DB task state, and PID assignment."""
        mock_proc = MagicMock()
        mock_proc.pid = 98765
        mock_popen.return_value = mock_proc

        short_input = "Build an automated CRM system"
        record = self.dispatcher.dispatch(
            skill_name="prd-generator",
            input_text=short_input,
            mode="dual",
            provider="local",
        )

        self.assertTrue(record.task_id.startswith("task_"))
        self.assertEqual(record.skill_name, "prd-generator")
        self.assertEqual(record.status, "running")
        self.assertEqual(record.mode, "dual")
        self.assertEqual(record.provider, "local")
        self.assertEqual(record.pid, 98765)
        self.assertEqual(record.input_preview, short_input)
        self.assertTrue(record.log_file.endswith(f"{record.task_id}.log"))

        # Verify subprocess.Popen call args
        mock_popen.assert_called_once()
        cmd, kwargs = mock_popen.call_args[0][0], mock_popen.call_args[1]

        self.assertEqual(cmd[0], sys.executable)
        self.assertEqual(cmd[1:3], ["-m", "engine.core.worker"])
        self.assertIn("--task-id", cmd)
        self.assertEqual(cmd[cmd.index("--task-id") + 1], record.task_id)
        self.assertIn("--db-path", cmd)
        self.assertEqual(cmd[cmd.index("--db-path") + 1], str(self.db_path))

        # Because input <= 200 chars, --input-file should NOT be in command
        self.assertNotIn("--input-file", cmd)

        # Standard descriptors redirected and log file used for stdout
        self.assertEqual(kwargs["stdin"], subprocess.DEVNULL)
        self.assertEqual(kwargs["stderr"], subprocess.STDOUT)
        self.assertTrue(kwargs["stdout"].name.endswith(f"{record.task_id}.log"))

    @patch("subprocess.Popen")
    def test_dispatch_large_input_spooling(self, mock_popen: MagicMock) -> None:
        """Verify inputs > 200 chars are safely written to spool file and passed via --input-file."""
        mock_proc = MagicMock()
        mock_proc.pid = 44332
        mock_popen.return_value = mock_proc

        long_input = "Architecture Specification: " + ("X" * 300)
        record = self.dispatcher.dispatch(
            skill_name="system-architecture",
            input_text=long_input,
            mode="single",
            provider="gemini",
        )

        expected_spool_file = self.spool_dir / f"{record.task_id}.input"
        self.assertTrue(expected_spool_file.is_file())
        self.assertEqual(expected_spool_file.read_text(encoding="utf-8"), long_input)

        # Truncated preview in task record
        self.assertEqual(len(record.input_preview), 200)

        # Verify command line includes --input-file pointing to spool
        cmd = mock_popen.call_args[0][0]
        self.assertIn("--input-file", cmd)
        self.assertEqual(cmd[cmd.index("--input-file") + 1], str(expected_spool_file))

    @patch("subprocess.Popen")
    def test_dispatch_custom_output_dir(self, mock_popen: MagicMock) -> None:
        """Verify custom output_dir override is passed to worker command."""
        mock_proc = MagicMock()
        mock_proc.pid = 11223
        mock_popen.return_value = mock_proc

        custom_output = self.test_dir / "custom_artifacts"
        record = self.dispatcher.dispatch(
            skill_name="backend-schema",
            input_text="User auth tables",
            output_dir=str(custom_output),
        )

        cmd = mock_popen.call_args[0][0]
        self.assertIn("--output-dir", cmd)
        self.assertEqual(cmd[cmd.index("--output-dir") + 1], str(custom_output))

    @patch("subprocess.Popen")
    def test_dispatch_windows_process_creation_flags(self, mock_popen: MagicMock) -> None:
        """Verify Windows DETACHED_PROCESS and CREATE_NEW_PROCESS_GROUP flags are set."""
        mock_proc = MagicMock()
        mock_proc.pid = 55667
        mock_popen.return_value = mock_proc

        with patch("os.name", "nt"):
            self.dispatcher.dispatch(skill_name="prd-generator")

        kwargs = mock_popen.call_args[1]
        expected_flags = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
        self.assertEqual(kwargs.get("creationflags"), expected_flags)
        self.assertTrue(kwargs.get("close_fds"))
        self.assertNotIn("start_new_session", kwargs)

    @patch("subprocess.Popen")
    def test_dispatch_unix_start_new_session(self, mock_popen: MagicMock) -> None:
        """Verify Unix platform sets start_new_session=True for process detachment."""
        mock_proc = MagicMock()
        mock_proc.pid = 66778
        mock_popen.return_value = mock_proc

        with patch("os.name", "posix"):
            self.dispatcher.dispatch(skill_name="clean-git-commits")

        kwargs = mock_popen.call_args[1]
        self.assertTrue(kwargs.get("start_new_session"))
        self.assertNotIn("creationflags", kwargs)

    @patch("subprocess.Popen")
    def test_dispatch_performance_under_50ms(self, mock_popen: MagicMock) -> None:
        """Verify dispatch call returns immediately (< 50ms)."""
        mock_proc = MagicMock()
        mock_proc.pid = 77889
        mock_popen.return_value = mock_proc

        start_time = time.perf_counter()
        record = self.dispatcher.dispatch(
            skill_name="trd-generator",
            input_text="High frequency order matching engine",
        )
        elapsed_ms = (time.perf_counter() - start_time) * 1000

        self.assertLess(elapsed_ms, 50.0, f"Dispatch took {elapsed_ms:.2f}ms, expected < 50ms")
        self.assertIsNotNone(record)

    @patch("subprocess.Popen")
    def test_dispatch_exception_marks_task_failed(self, mock_popen: MagicMock) -> None:
        """Verify that if Popen throws an exception, task in DB is updated to failed."""
        mock_popen.side_effect = OSError("Executable permission denied")

        with self.assertRaises(OSError):
            self.dispatcher.dispatch(skill_name="prd-generator")

        tasks = self.dispatcher.task_manager.list_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].status, "failed")
        self.assertIn("Executable permission denied", tasks[0].error_message)

    def test_is_pid_alive(self) -> None:
        """Verify live PID check works for current process and rejects invalid/dead PIDs."""
        # Current running process is guaranteed alive
        self.assertTrue(self.dispatcher.is_pid_alive(os.getpid()))

        # None, 0, or negative PIDs are never alive
        self.assertFalse(self.dispatcher.is_pid_alive(None))
        self.assertFalse(self.dispatcher.is_pid_alive(0))
        self.assertFalse(self.dispatcher.is_pid_alive(-1))

        # Arbitrary out-of-range PID is dead
        self.assertFalse(self.dispatcher.is_pid_alive(99999999))

    def test_get_status_reconciles_dead_pid(self) -> None:
        """Verify get_status detects dead PIDs on running tasks and transitions them to failed."""
        # Create a task marked running with a dead PID
        dead_pid = 99999998
        record = self.dispatcher.task_manager.create_task(
            skill_name="playwright-e2e-testing",
            status="running",
            pid=dead_pid,
        )
        self.assertEqual(record.status, "running")

        # Query status via dispatcher
        status_record = self.dispatcher.get_status(record.task_id)
        self.assertIsNotNone(status_record)
        self.assertEqual(status_record.status, "failed")
        self.assertEqual(status_record.error_message, "Process terminated unexpectedly")
        self.assertEqual(status_record.exit_code, -1)

        # Database state should also be updated
        db_record = self.dispatcher.task_manager.get_task(record.task_id)
        self.assertEqual(db_record.status, "failed")

    def test_get_status_keeps_alive_pid_running(self) -> None:
        """Verify get_status leaves running tasks with alive PIDs in running status."""
        record = self.dispatcher.task_manager.create_task(
            skill_name="systematic-debugging",
            status="running",
            pid=os.getpid(),
        )

        status_record = self.dispatcher.get_status(record.task_id)
        self.assertIsNotNone(status_record)
        self.assertEqual(status_record.status, "running")
        self.assertIsNone(status_record.error_message)

    def test_get_status_nonexistent(self) -> None:
        """Verify get_status returns None for nonexistent task IDs."""
        self.assertIsNone(self.dispatcher.get_status("task_nonexistent_12345"))

    def test_reconcile_tasks_batch(self) -> None:
        """Verify reconcile_tasks scans and reconciles all tasks with dead PIDs."""
        # 1. Running with dead PID
        t1 = self.dispatcher.task_manager.create_task(
            skill_name="backend-schema", status="running", pid=99999991
        )
        # 2. Running with another dead PID
        t2 = self.dispatcher.task_manager.create_task(
            skill_name="api-contract-generator", status="running", pid=99999992
        )
        # 3. Running with current live PID
        t3 = self.dispatcher.task_manager.create_task(
            skill_name="clean-git-commits", status="running", pid=os.getpid()
        )
        # 4. Already completed task
        t4 = self.dispatcher.task_manager.create_task(
            skill_name="prd-generator", status="completed", pid=99999993, score=90
        )

        reconciled = self.dispatcher.reconcile_tasks()
        reconciled_ids = [t.task_id for t in reconciled]

        self.assertIn(t1.task_id, reconciled_ids)
        self.assertIn(t2.task_id, reconciled_ids)
        self.assertNotIn(t3.task_id, reconciled_ids)
        self.assertNotIn(t4.task_id, reconciled_ids)

        self.assertEqual(self.dispatcher.task_manager.get_task(t1.task_id).status, "failed")
        self.assertEqual(self.dispatcher.task_manager.get_task(t2.task_id).status, "failed")
        self.assertEqual(self.dispatcher.task_manager.get_task(t3.task_id).status, "running")
        self.assertEqual(self.dispatcher.task_manager.get_task(t4.task_id).status, "completed")

    def test_cancel_task_running(self) -> None:
        """Verify cancelling a running task terminates the process and updates status to cancelled."""
        # Start a real dummy sleep process to test cancellation
        proc = subprocess.Popen(
            [sys.executable, "-c", "import time; time.sleep(30)"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            record = self.dispatcher.task_manager.create_task(
                skill_name="devops-docker-deploy",
                status="running",
                pid=proc.pid,
            )

            result = self.dispatcher.cancel_task(record.task_id)
            self.assertTrue(result)

            # Give OS a moment to finish termination
            proc.wait(timeout=5)

            updated = self.dispatcher.task_manager.get_task(record.task_id)
            self.assertEqual(updated.status, "cancelled")
            self.assertEqual(updated.error_message, "Task cancelled by user")
            self.assertFalse(self.dispatcher.is_pid_alive(proc.pid))
        finally:
            try:
                proc.wait(timeout=2)
            except Exception:
                proc.kill()
                proc.wait(timeout=2)

    def test_cancel_task_terminal_returns_false(self) -> None:
        """Verify cancelling completed, failed, or already cancelled tasks returns False."""
        t_completed = self.dispatcher.task_manager.create_task(
            skill_name="prd-generator", status="completed"
        )
        self.assertFalse(self.dispatcher.cancel_task(t_completed.task_id))

        t_failed = self.dispatcher.task_manager.create_task(
            skill_name="trd-generator", status="failed"
        )
        self.assertFalse(self.dispatcher.cancel_task(t_failed.task_id))

        t_cancelled = self.dispatcher.task_manager.create_task(
            skill_name="app-flow", status="cancelled"
        )
        self.assertFalse(self.dispatcher.cancel_task(t_cancelled.task_id))

        # Nonexistent task
        self.assertFalse(self.dispatcher.cancel_task("task_nonexistent_0000"))

    def test_get_logs(self) -> None:
        """Verify log retrieval with tail truncation and handling of missing files."""
        task_id = self.dispatcher.task_manager.generate_task_id()
        log_file = self.log_dir / f"{task_id}.log"
        lines = [f"Log entry line {i:03d}\n" for i in range(1, 101)]
        log_file.write_text("".join(lines), encoding="utf-8")

        self.dispatcher.task_manager.create_task(
            task_id=task_id,
            skill_name="seo-content-strategist",
            log_file=str(log_file),
        )

        # Tail 10
        tail10 = self.dispatcher.get_logs(task_id, tail=10)
        expected_tail10 = "".join(lines[-10:])
        self.assertEqual(tail10, expected_tail10)

        # Tail 0 or negative returns all lines
        all_logs = self.dispatcher.get_logs(task_id, tail=0)
        self.assertEqual(all_logs, "".join(lines))

        # Tail greater than total lines returns all
        tail200 = self.dispatcher.get_logs(task_id, tail=200)
        self.assertEqual(tail200, "".join(lines))

        # Nonexistent task returns empty string
        self.assertEqual(self.dispatcher.get_logs("task_nonexistent_8888"), "")

    def test_list_tasks(self) -> None:
        """Verify listing tasks with status/skill filtering and limits."""
        for i in range(5):
            self.dispatcher.task_manager.create_task(
                skill_name="prd-generator",
                status="completed",
                started_at=f"2026-11-07T10:0{i}:00+00:00",
            )
        for i in range(3):
            self.dispatcher.task_manager.create_task(
                skill_name="backend-schema",
                status="failed",
                started_at=f"2026-11-07T11:0{i}:00+00:00",
            )

        # Total count
        all_tasks = self.dispatcher.list_tasks(limit=20, reconcile=False)
        self.assertEqual(len(all_tasks), 8)

        # Filter by status
        completed = self.dispatcher.list_tasks(status="completed", reconcile=False)
        self.assertEqual(len(completed), 5)
        self.assertTrue(all(t.status == "completed" for t in completed))

        # Filter by skill
        backend = self.dispatcher.list_tasks(skill_name="backend-schema", reconcile=False)
        self.assertEqual(len(backend), 3)

        # Limit
        limited = self.dispatcher.list_tasks(limit=2, reconcile=False)
        self.assertEqual(len(limited), 2)

    def test_prune_tasks(self) -> None:
        """Verify prune_tasks deletes records older than given days."""
        now = datetime.now(timezone.utc)
        old_time = (now - timedelta(days=10)).isoformat()
        recent_time = (now - timedelta(days=2)).isoformat()

        t_old = self.dispatcher.task_manager.create_task(
            skill_name="prd-generator", started_at=old_time
        )
        t_recent = self.dispatcher.task_manager.create_task(
            skill_name="trd-generator", started_at=recent_time
        )

        pruned = self.dispatcher.prune_tasks(older_than_days=7)
        self.assertEqual(pruned, 1)

        self.assertIsNone(self.dispatcher.task_manager.get_task(t_old.task_id))
        self.assertIsNotNone(self.dispatcher.task_manager.get_task(t_recent.task_id))


    def test_live_detached_dispatch_and_worker_completion(self) -> None:
        """Integration test: Spawns a real detached worker process and verifies completion."""
        start_time = time.perf_counter()
        record = self.dispatcher.dispatch(
            skill_name="prd-generator",
            input_text="Online multiplayer chess platform",
            mode="dual",
            provider="local",
        )
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        self.assertLess(elapsed_ms, 150.0, "Dispatch should be non-blocking")

        task_id = record.task_id
        # Poll for completion with a timeout
        deadline = time.time() + 10.0
        final_record = None
        while time.time() < deadline:
            task = self.dispatcher.get_status(task_id)
            if task and task.status in ("completed", "failed"):
                final_record = task
                break
            time.sleep(0.2)

        self.assertIsNotNone(final_record, "Worker did not complete within deadline")
        self.assertEqual(final_record.status, "completed")
        self.assertEqual(final_record.verdict, "PASS")
        self.assertGreaterEqual(final_record.score, 80)
        self.assertTrue(Path(final_record.output_file).is_file())

        logs = self.dispatcher.get_logs(task_id, tail=20)
        self.assertIn("Task state transitioned to RUNNING", logs)
        self.assertIn("marked COMPLETED", logs)


if __name__ == "__main__":
    unittest.main()
