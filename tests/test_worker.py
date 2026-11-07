"""Unit tests for engine.core.worker (Background Worker Process Runner)."""

import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import MagicMock, patch

from engine.core.registry import AgentRegistry
from engine.core.runner import DualAgentRunner
from engine.core.task_manager import TaskManager, TaskRecord
from engine.core.types import GenerationResult, ValidationScorecard
import engine.core.worker as worker_module
from engine.core.worker import main, run_worker


class TestBackgroundWorker(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.db_path = self.test_dir / "tasks.db"
        self.output_dir = self.test_dir / "output"
        self.log_dir = self.test_dir / "logs"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.manager = TaskManager(db_path=self.db_path)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_worker_successful_execution_real_skill(self):
        """Worker successfully runs a registered skill, produces artifact and marks completed."""
        task_id = self.manager.generate_task_id()
        self.manager.create_task(
            task_id=task_id,
            skill_name="prd-generator",
            mode="dual",
            input_text="Decentralized identity protocol",
            log_file=str(self.log_dir / f"{task_id}.log"),
        )

        exit_code = run_worker(
            task_id=task_id,
            db_path=self.db_path,
            output_dir=self.output_dir,
        )
        self.assertEqual(exit_code, 0)

        # Check DB update
        record = self.manager.get_task(task_id)
        self.assertIsNotNone(record)
        self.assertEqual(record.status, "completed")
        self.assertEqual(record.exit_code, 0)
        self.assertEqual(record.verdict, "PASS")
        self.assertGreaterEqual(record.score, 85)
        self.assertEqual(record.pid, os.getpid())
        self.assertIsNotNone(record.started_at)
        self.assertIsNotNone(record.completed_at)

        # Check artifact
        expected_artifact = self.output_dir / f"prd-generator_{task_id}.md"
        self.assertTrue(expected_artifact.exists())
        self.assertEqual(record.output_file, str(expected_artifact))
        content = expected_artifact.read_text(encoding="utf-8")
        self.assertGreater(len(content), 50)

        # Check log file was populated
        log_file = self.log_dir / f"{task_id}.log"
        self.assertTrue(log_file.exists())
        log_text = log_file.read_text(encoding="utf-8")
        self.assertIn("Initializing worker for task", log_text)
        self.assertIn("Task state transitioned to RUNNING", log_text)
        self.assertIn("marked COMPLETED", log_text)

    def test_worker_with_input_file(self):
        """Worker loads prompt from an explicit input file."""
        input_file = self.test_dir / "custom_prompt.txt"
        input_file.write_text("Crypto asset treasury management specification", encoding="utf-8")

        task_id = self.manager.generate_task_id()
        self.manager.create_task(
            task_id=task_id,
            skill_name="backend-schema",
            mode="dual",
            input_text="Placeholder preview",
            log_file=str(self.log_dir / f"{task_id}.log"),
        )

        exit_code = run_worker(
            task_id=task_id,
            db_path=self.db_path,
            input_file=input_file,
            output_dir=self.output_dir,
        )
        self.assertEqual(exit_code, 0)

        record = self.manager.get_task(task_id)
        self.assertEqual(record.status, "completed")

        artifact = Path(record.output_file)
        self.assertTrue(artifact.exists())
        self.assertIn("backend-schema", artifact.name)

    def test_worker_with_mocked_runner_failing_verdict(self):
        """Worker records FAIL verdict when validator scorecard does not pass."""
        mock_runner = MagicMock(spec=DualAgentRunner)
        mock_runner.run_skill.return_value = (
            GenerationResult(skill_name="trd-generator", content="Mocked technical specification"),
            ValidationScorecard(
                skill_name="trd-generator",
                score=65,
                passed=False,
                audit_summary="Fails latency requirements",
                iteration=2,
            ),
        )

        task_id = self.manager.generate_task_id()
        self.manager.create_task(
            task_id=task_id,
            skill_name="trd-generator",
            mode="dual",
            input_text="High frequency order matching engine",
            log_file=str(self.log_dir / f"{task_id}.log"),
        )

        exit_code = run_worker(
            task_id=task_id,
            db_path=self.db_path,
            output_dir=self.output_dir,
            runner=mock_runner,
        )
        self.assertEqual(exit_code, 0)

        record = self.manager.get_task(task_id)
        self.assertEqual(record.status, "completed")
        self.assertEqual(record.verdict, "FAIL")
        self.assertEqual(record.score, 65)
        self.assertEqual(record.exit_code, 0)

    def test_worker_exception_handling_unknown_skill(self):
        """Worker handles unknown skill by recording failed status in ledger and exiting with 1."""
        task_id = self.manager.generate_task_id()
        self.manager.create_task(
            task_id=task_id,
            skill_name="unregistered-mythical-skill",
            mode="dual",
            input_text="Task input",
            log_file=str(self.log_dir / f"{task_id}.log"),
        )

        exit_code = run_worker(
            task_id=task_id,
            db_path=self.db_path,
            output_dir=self.output_dir,
        )
        self.assertEqual(exit_code, 1)

        record = self.manager.get_task(task_id)
        self.assertEqual(record.status, "failed")
        self.assertEqual(record.exit_code, 1)
        self.assertIn("not found in AgentRegistry", record.error_message)
        self.assertIsNotNone(record.completed_at)

    def test_worker_exception_handling_runner_exception(self):
        """Worker traps exceptions raised by runner, logs traceback, and sets status=failed."""
        mock_runner = MagicMock(spec=DualAgentRunner)
        mock_runner.run_skill.side_effect = RuntimeError("Fatal connection reset during LLM call")

        task_id = self.manager.generate_task_id()
        self.manager.create_task(
            task_id=task_id,
            skill_name="app-flow",
            mode="dual",
            input_text="Checkout journey",
            log_file=str(self.log_dir / f"{task_id}.log"),
        )

        exit_code = run_worker(
            task_id=task_id,
            db_path=self.db_path,
            output_dir=self.output_dir,
            runner=mock_runner,
        )
        self.assertEqual(exit_code, 1)

        record = self.manager.get_task(task_id)
        self.assertEqual(record.status, "failed")
        self.assertEqual(record.exit_code, 1)
        self.assertIn("Fatal connection reset", record.error_message)

        # Check that error is in the log file
        log_file = self.log_dir / f"{task_id}.log"
        self.assertTrue(log_file.exists())
        self.assertIn("Fatal error executing task", log_file.read_text(encoding="utf-8"))

    def test_worker_task_not_found(self):
        """Worker returns 1 when task_id does not exist in ledger."""
        exit_code = run_worker(
            task_id="task_nonexistent_9999",
            db_path=self.db_path,
            output_dir=self.output_dir,
        )
        self.assertEqual(exit_code, 1)

    def test_worker_cancelled_task_early_exit(self):
        """Worker does not execute task if it is already cancelled."""
        task_id = self.manager.generate_task_id()
        self.manager.create_task(
            task_id=task_id,
            skill_name="prd-generator",
            status="cancelled",
        )

        exit_code = run_worker(
            task_id=task_id,
            db_path=self.db_path,
            output_dir=self.output_dir,
        )
        self.assertEqual(exit_code, 0)

        record = self.manager.get_task(task_id)
        self.assertEqual(record.status, "cancelled")

    def test_worker_sqlite_fallback_when_task_manager_none(self):
        """Worker functions completely through direct SQLite queries when TaskManager is None."""
        task_id = self.manager.generate_task_id()
        self.manager.create_task(
            task_id=task_id,
            skill_name="prd-generator",
            input_text="Local sqlite test",
            log_file=str(self.log_dir / f"{task_id}.log"),
        )

        # Simulate TaskManager module not available
        with patch.object(worker_module, "TaskManager", None):
            exit_code = run_worker(
                task_id=task_id,
                db_path=self.db_path,
                output_dir=self.output_dir,
            )
            self.assertEqual(exit_code, 0)

        record = self.manager.get_task(task_id)
        self.assertEqual(record.status, "completed")
        self.assertEqual(record.verdict, "PASS")
        self.assertEqual(record.exit_code, 0)

    def test_worker_cli_entrypoint(self):
        """Worker main() correctly parses CLI arguments and runs task."""
        task_id = self.manager.generate_task_id()
        self.manager.create_task(
            task_id=task_id,
            skill_name="prd-generator",
            input_text="CLI entrypoint test",
            log_file=str(self.log_dir / f"{task_id}.log"),
        )

        argv = [
            "--task-id",
            task_id,
            "--db-path",
            str(self.db_path),
            "--output-dir",
            str(self.output_dir),
        ]
        exit_code = main(argv)
        self.assertEqual(exit_code, 0)

        record = self.manager.get_task(task_id)
        self.assertEqual(record.status, "completed")

    def test_worker_cli_entrypoint_with_input_file(self):
        """Worker main() handles --input-file CLI option."""
        input_file = self.test_dir / "cli_prompt.txt"
        input_file.write_text("CLI prompt test content", encoding="utf-8")

        task_id = self.manager.generate_task_id()
        self.manager.create_task(
            task_id=task_id,
            skill_name="prd-generator",
            log_file=str(self.log_dir / f"{task_id}.log"),
        )

        argv = [
            "--task-id",
            task_id,
            "--db-path",
            str(self.db_path),
            "--input-file",
            str(input_file),
            "--output-dir",
            str(self.output_dir),
        ]
        exit_code = main(argv)
        self.assertEqual(exit_code, 0)


if __name__ == "__main__":
    unittest.main()
