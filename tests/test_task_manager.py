import unittest
import tempfile
import shutil
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

from engine.core.task_manager import TaskManager, TaskRecord


class TestTaskManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.db_path = self.test_dir / "tasks.db"
        self.manager = TaskManager(db_path=self.db_path)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_db_initialization_and_wal(self):
        self.assertTrue(self.db_path.exists())
        with self.manager._connect() as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='agent_tasks';")
            self.assertIsNotNone(cursor.fetchone())
            
            indexes = [row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='index';").fetchall()]
            self.assertTrue(any("idx_tasks_status" in idx for idx in indexes))
            self.assertTrue(any("idx_tasks_skill" in idx for idx in indexes))

    def test_generate_task_id(self):
        task_id = self.manager.generate_task_id()
        self.assertTrue(task_id.startswith("task_"))
        parts = task_id.split("_")
        self.assertGreaterEqual(len(parts), 4)
        
        # Test uniqueness
        id1 = self.manager.generate_task_id()
        id2 = self.manager.generate_task_id()
        self.assertNotEqual(id1, id2)

    def test_create_and_get_task(self):
        task_id = self.manager.generate_task_id()
        self.assertTrue(task_id.startswith("task_"))

        record = self.manager.create_task(
            task_id=task_id,
            skill_name="prd-generator",
            mode="dual",
            provider="local",
            pid=1234,
            input_preview="Crypto portfolio tracker",
            log_file="data/logs/test.log"
        )
        self.assertEqual(record.task_id, task_id)
        self.assertEqual(record.status, "running")
        self.assertEqual(record.skill_name, "prd-generator")
        self.assertEqual(record.mode, "dual")
        self.assertEqual(record.provider, "local")
        self.assertEqual(record.pid, 1234)
        self.assertEqual(record.input_preview, "Crypto portfolio tracker")
        self.assertEqual(record.log_file, "data/logs/test.log")
        self.assertIsNotNone(record.started_at)
        self.assertIsNone(record.completed_at)

        fetched = self.manager.get_task(task_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.task_id, task_id)
        self.assertEqual(fetched.skill_name, "prd-generator")
        self.assertEqual(fetched.pid, 1234)
        self.assertEqual(fetched.input_preview, "Crypto portfolio tracker")

    def test_create_task_minimal_args(self):
        record = self.manager.create_task(skill_name="backend-schema")
        self.assertTrue(record.task_id.startswith("task_"))
        self.assertEqual(record.skill_name, "backend-schema")
        self.assertEqual(record.status, "running")
        self.assertEqual(record.mode, "dual")
        self.assertEqual(record.provider, "local")
        self.assertIsNone(record.pid)

    def test_create_task_with_input_text_truncation(self):
        long_input = "A" * 300
        record = self.manager.create_task(skill_name="trd-generator", input_text=long_input)
        self.assertLessEqual(len(record.input_preview), 200)

    def test_get_nonexistent_task(self):
        result = self.manager.get_task("task_nonexistent_12345")
        self.assertIsNone(result)

    def test_update_task_completion(self):
        task_id = self.manager.generate_task_id()
        self.manager.create_task(task_id=task_id, skill_name="backend-schema")

        updated = self.manager.update_task(
            task_id=task_id,
            status="completed",
            score=95,
            verdict="PASS",
            output_file="output/test.md"
        )
        self.assertIsNotNone(updated)
        self.assertEqual(updated.status, "completed")
        self.assertEqual(updated.score, 95)
        self.assertEqual(updated.verdict, "PASS")
        self.assertEqual(updated.output_file, "output/test.md")
        self.assertIsNotNone(updated.completed_at)

        fetched = self.manager.get_task(task_id)
        self.assertEqual(fetched.status, "completed")
        self.assertEqual(fetched.score, 95)
        self.assertEqual(fetched.completed_at, updated.completed_at)

    def test_update_task_failure(self):
        task_id = self.manager.generate_task_id()
        self.manager.create_task(task_id=task_id, skill_name="app-flow")

        updated = self.manager.update_task(
            task_id=task_id,
            status="failed",
            exit_code=1,
            error_message="Runtime connection error"
        )
        self.assertIsNotNone(updated)
        self.assertEqual(updated.status, "failed")
        self.assertEqual(updated.exit_code, 1)
        self.assertEqual(updated.error_message, "Runtime connection error")
        self.assertIsNotNone(updated.completed_at)

    def test_update_nonexistent_task(self):
        result = self.manager.update_task("task_nonexistent_00000", status="completed")
        self.assertIsNone(result)

    def test_list_tasks_and_filtering(self):
        t1 = self.manager.create_task(skill_name="prd-generator", input_text="Task 1")
        time.sleep(0.01)
        t2 = self.manager.create_task(skill_name="backend-schema", input_text="Task 2")
        time.sleep(0.01)
        t3 = self.manager.create_task(skill_name="prd-generator", input_text="Task 3")

        self.manager.update_task(t1.task_id, status="completed", score=90)
        self.manager.update_task(t2.task_id, status="failed", error_message="fail")

        all_tasks = self.manager.list_tasks()
        self.assertEqual(len(all_tasks), 3)

        # Filtering by status
        completed = self.manager.list_tasks(status="completed")
        self.assertEqual(len(completed), 1)
        self.assertEqual(completed[0].task_id, t1.task_id)

        running = self.manager.list_tasks(status="running")
        self.assertEqual(len(running), 1)
        self.assertEqual(running[0].task_id, t3.task_id)

        # Filtering by skill_name
        prd_tasks = self.manager.list_tasks(skill_name="prd-generator")
        self.assertEqual(len(prd_tasks), 2)

        # Filtering by both
        prd_running = self.manager.list_tasks(skill_name="prd-generator", status="running")
        self.assertEqual(len(prd_running), 1)
        self.assertEqual(prd_running[0].task_id, t3.task_id)

        # Limit
        limited = self.manager.list_tasks(limit=2)
        self.assertEqual(len(limited), 2)

    def test_delete_task(self):
        record = self.manager.create_task(skill_name="system-architecture")
        task_id = record.task_id

        deleted = self.manager.delete_task(task_id)
        self.assertTrue(deleted)
        self.assertIsNone(self.manager.get_task(task_id))

        deleted_again = self.manager.delete_task(task_id)
        self.assertFalse(deleted_again)

    def test_prune_tasks(self):
        now = datetime.now(timezone.utc)
        old_time = (now - timedelta(days=10)).isoformat()
        recent_time = (now - timedelta(days=2)).isoformat()

        t_old = self.manager.create_task(skill_name="old-task")
        t_recent = self.manager.create_task(skill_name="recent-task")

        # Manually backdate started_at for t_old and t_recent
        with self.manager._connect() as conn:
            conn.execute("UPDATE agent_tasks SET started_at = ? WHERE task_id = ?", (old_time, t_old.task_id))
            conn.execute("UPDATE agent_tasks SET started_at = ? WHERE task_id = ?", (recent_time, t_recent.task_id))

        pruned_count = self.manager.prune_tasks(older_than_days=7)
        self.assertEqual(pruned_count, 1)

        self.assertIsNone(self.manager.get_task(t_old.task_id))
        self.assertIsNotNone(self.manager.get_task(t_recent.task_id))

    def test_task_record_to_dict(self):
        record = self.manager.create_task(skill_name="prd-generator", input_text="Sample input")
        d = record.to_dict()
        self.assertIsInstance(d, dict)
        self.assertEqual(d["task_id"], record.task_id)
        self.assertEqual(d["skill_name"], "prd-generator")
        self.assertEqual(d["status"], "running")


if __name__ == "__main__":
    unittest.main()
