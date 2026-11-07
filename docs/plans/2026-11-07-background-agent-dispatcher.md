# Background Agent Dispatcher & Asynchronous Task System Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a zero-dependency background agent dispatcher and asynchronous task management system for AI_Flow, allowing any of the 30 skills and 60 dual-agent personas to execute detached in the background with full CLI controls (`--background`, `--status`, `--list-tasks`, `--logs`, `--cancel`).

**Architecture:** Pure Python 3 standard library architecture centered on an ACID SQLite task ledger (`data/tasks.db`), cross-platform detached process spawning (`DETACHED_PROCESS` on Windows, `setsid` on Unix), and a dedicated background worker entrypoint (`engine/core/worker.py`) that executes the Generator & Validator loop and reports back.

**Tech Stack:** Python 3.10+ standard library (`sqlite3`, `subprocess`, `os`, `signal`, `pathlib`, `json`, `datetime`, `unittest`). Zero external pip dependencies.

---

### Task 1: SQLite Task Ledger & Manager (`engine/core/task_manager.py`)

**Files:**
- Create: `engine/core/task_manager.py`
- Test: `tests/test_task_manager.py`

**Step 1: Write the failing test**
Create `tests/test_task_manager.py` testing:
- Creation of SQLite database and `agent_tasks` table with indexes.
- Generating unique task IDs: `task_YYYYMMDD_XXXXXX`.
- `create_task()` inserting initial record with status `queued` or `running`.
- `update_task()` updating status, score, output_file, error_message, completed_at.
- `get_task()` returning task dictionary or None.
- `list_tasks()` returning sorted tasks with optional status filter.

```python
import unittest
import tempfile
import shutil
from pathlib import Path
from engine.core.task_manager import TaskManager, TaskRecord

class TestTaskManager(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.db_path = self.test_dir / "tasks.db"
        self.manager = TaskManager(db_path=self.db_path)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_create_and_get_task(self):
        task_id = self.manager.generate_task_id()
        self.assertTrue(task_id.startswith("task_"))
        
        record = self.manager.create_task(
            task_id=task_id,
            skill_name="prd-generator",
            mode="dual",
            provider="local",
            pid=1234,
            input_preview="Crypto portfolio tracker"
        )
        self.assertEqual(record.task_id, task_id)
        self.assertEqual(record.status, "running")
        
        fetched = self.manager.get_task(task_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.skill_name, "prd-generator")
        self.assertEqual(fetched.pid, 1234)

    def test_update_task_completion(self):
        task_id = self.manager.generate_task_id()
        self.manager.create_task(task_id=task_id, skill_name="backend-schema")
        
        self.manager.update_task(
            task_id=task_id,
            status="completed",
            score=95,
            verdict="PASS",
            output_file="output/test.md"
        )
        fetched = self.manager.get_task(task_id)
        self.assertEqual(fetched.status, "completed")
        self.assertEqual(fetched.score, 95)
        self.assertIsNotNone(fetched.completed_at)
```

**Step 2: Run test to verify it fails**
Run: `python -m unittest tests/test_task_manager.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'engine.core.task_manager'`

**Step 3: Write minimal implementation**
Create `engine/core/task_manager.py` implementing `TaskManager`, `TaskRecord` dataclass, SQLite schema creation, and query methods.

**Step 4: Run test to verify it passes**
Run: `python -m unittest tests/test_task_manager.py`
Expected: PASS

**Step 5: Commit**
```bash
git add engine/core/task_manager.py tests/test_task_manager.py
git commit -m "feat(tasks): implement SQLite task ledger and manager"
```

---

### Task 2: Background Worker Execution Engine (`engine/core/worker.py`)

**Files:**
- Create: `engine/core/worker.py`
- Test: `tests/test_worker.py`

**Step 1: Write the failing test**
Create `tests/test_worker.py` testing:
- Worker initialization from Task ID and SQLite database.
- Executing skill via `DualAgentRunner` in a separate process/thread.
- Capturing stdout and stderr logs to `data/logs/{task_id}.log`.
- Writing output artifact to `output/{skill_name}_{task_id}.md`.
- Updating task status to `completed` with score and verdict.
- Exception handling and updating task status to `failed` with error message.

**Step 2: Run test to verify it fails**
Run: `python -m unittest tests/test_worker.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'engine.core.worker'`

**Step 3: Write minimal implementation**
Implement `engine/core/worker.py` with standalone entrypoint callable as `python -m engine.core.worker --task-id <task_id> --db-path <db_path>`.

**Step 4: Run test to verify it passes**
Run: `python -m unittest tests/test_worker.py`
Expected: PASS

**Step 5: Commit**
```bash
git add engine/core/worker.py tests/test_worker.py
git commit -m "feat(worker): implement standalone background worker process runner"
```

---

### Task 3: Universal Agent Dispatcher (`engine/core/dispatcher.py`)

**Files:**
- Create: `engine/core/dispatcher.py`
- Test: `tests/test_dispatcher.py`

**Step 1: Write the failing test**
Create `tests/test_dispatcher.py` testing:
- `AgentDispatcher.dispatch()` spawns detached background process.
- Windows `creationflags` (`DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP`).
- Unix `start_new_session=True`.
- Non-blocking execution (&lt; 50ms).
- Dead PID detection in `reconcile_tasks()`.
- Cancelling running task via `AgentDispatcher.cancel_task(task_id)`.

**Step 2: Run test to verify it fails**
Run: `python -m unittest tests/test_dispatcher.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'engine.core.dispatcher'`

**Step 3: Write minimal implementation**
Implement `AgentDispatcher` in `engine/core/dispatcher.py` integrating `TaskManager`, process spawning, dead process reconciliation, and cancellation.

**Step 4: Run test to verify it passes**
Run: `python -m unittest tests/test_dispatcher.py`
Expected: PASS

**Step 5: Commit**
```bash
git add engine/core/dispatcher.py tests/test_dispatcher.py
git commit -m "feat(dispatcher): implement detached process agent dispatcher"
```

---

### Task 4: CLI Interface Integration (`engine/cli.py` & `scripts/run.py`)

**Files:**
- Modify: `engine/cli.py`
- Modify: `scripts/run.py`
- Test: `tests/test_cli_background.py`

**Step 1: Write the failing test**
Create `tests/test_cli_background.py` testing:
- `--background` (`-bg`) argument in `engine.cli` and `scripts/run.py`.
- `--list-tasks` prints tabular view of active/completed tasks.
- `--status <task_id>` outputs detailed task state, score, and output file.
- `--logs <task_id>` outputs log content.
- `--cancel <task_id>` halts running task.

**Step 2: Run test to verify it fails**
Run: `python -m unittest tests/test_cli_background.py`
Expected: FAIL with unrecognized arguments

**Step 3: Write minimal implementation**
Add `--background`, `--list-tasks`, `--status`, `--logs`, `--cancel` argument parsing and handlers in `engine/cli.py` and `scripts/run.py`.

**Step 4: Run test to verify it passes**
Run: `python -m unittest tests/test_cli_background.py`
Expected: PASS

**Step 5: Commit**
```bash
git add engine/cli.py scripts/run.py tests/test_cli_background.py
git commit -m "feat(cli): add background dispatch and task management commands"
```

---

### Task 5: End-to-End Live Verification & Documentation

**Files:**
- Modify: `docs/MULTI_CLI_INSTALLATION_GUIDE.md`
- Modify: `README.md`
- Update: `scripts/install.ps1` to deploy `worker.py` and `dispatcher.py` into installed plugin locations.

**Step 1: Execute live background dispatch**
Run: `python -m engine.cli --skill prd-generator --input "Decentralized video platform" --background`
Verify: Command returns in &lt; 100ms with Task ID and PID.
Run: `python -m engine.cli --status <task_id>` until completed.
Verify: Output artifact exists, score &ge; 85, log file populated.

**Step 2: Execute Ollama background dispatch**
Run: `python scripts/run.py --provider ollama --skill backend-schema --input "SaaS Auth Schema" --background`

**Step 3: Run full regression test suite**
Run: `python -m unittest discover -s tests -p "test_*.py"`
Run: `node scripts/validate.js`
Run: `python scripts/verify_install.py`

**Step 4: Update documentation**
Document background commands in `docs/MULTI_CLI_INSTALLATION_GUIDE.md` and `README.md`.

**Step 5: Commit**
```bash
git add docs/ README.md scripts/
git commit -m "docs(background): document background agent execution across CLI tools"
```
