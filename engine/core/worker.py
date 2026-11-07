"""Background Worker Process Runner for detached asynchronous agent execution.

Executes AI_Flow skills (via DualAgentRunner) in an isolated process,
persisting execution progress, logs, artifacts, and scorecards to the SQLite
task ledger.
"""

import argparse
from datetime import datetime, timezone
import json
import logging
import os
from pathlib import Path
import sqlite3
import sys
import traceback
from typing import Any, Optional, Union

# Auto-register all 30 skills and 60 agents
import engine.agents
from engine.core.registry import AgentRegistry
from engine.core.runner import DualAgentRunner
from engine.core.types import GenerationResult, ValidationScorecard

# Try importing TaskManager and TaskRecord from engine.core.task_manager
try:
    from engine.core.task_manager import TaskManager, TaskRecord
except ImportError:
    TaskManager = None
    TaskRecord = None

# Project paths
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_DB_PATH = REPO_ROOT / "data" / "tasks.db"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output"
DEFAULT_LOG_DIR = REPO_ROOT / "data" / "logs"


def ensure_skills_registered() -> None:
    """Ensure all 30 skills are loaded in AgentRegistry."""
    if len(AgentRegistry.list_skills()) < 30:
        import importlib
        import engine.agents as ea
        for mod in (
            ea.phase1_architecture,
            ea.phase2_execution,
            ea.phase3_release,
            ea.phase4_design_frontend,
            ea.phase5_api_data_perf,
            ea.phase6_devops_finops,
            ea.phase7_freelance_ops,
            ea.phase8_growth_founder,
        ):
            importlib.reload(mod)


def _get_val(obj: Any, key: str, default: Any = None) -> Any:
    """Helper to extract attribute or dictionary key safely."""
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _sqlite_get_task(db_path: Path, task_id: str) -> Optional[dict[str, Any]]:
    """Direct SQLite fallback to fetch a task record."""
    if not db_path.exists():
        return None
    conn = sqlite3.connect(str(db_path), timeout=10.0)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.execute("SELECT * FROM agent_tasks WHERE task_id = ?;", (task_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def _sqlite_update_task(db_path: Path, task_id: str, **fields: Any) -> Optional[dict[str, Any]]:
    """Direct SQLite fallback to update a task record."""
    if not db_path.exists():
        return None

    status = fields.get("status")
    if (
        status in ("completed", "failed", "cancelled")
        and "completed_at" not in fields
    ):
        fields["completed_at"] = datetime.now(timezone.utc).isoformat()

    valid_columns = {
        "task_id",
        "skill_name",
        "mode",
        "provider",
        "status",
        "pid",
        "input_preview",
        "started_at",
        "completed_at",
        "exit_code",
        "score",
        "verdict",
        "output_file",
        "log_file",
        "error_message",
    }
    clean_fields = {k: v for k, v in fields.items() if k in valid_columns}
    if not clean_fields:
        return _sqlite_get_task(db_path, task_id)

    set_clause = ", ".join(f"{k} = ?" for k in clean_fields.keys())
    params = list(clean_fields.values()) + [task_id]

    conn = sqlite3.connect(str(db_path), timeout=10.0)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.execute(f"UPDATE agent_tasks SET {set_clause} WHERE task_id = ?;", params)
        conn.commit()
        if cur.rowcount == 0:
            return None
        cur = conn.execute("SELECT * FROM agent_tasks WHERE task_id = ?;", (task_id,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def fetch_task_record(task_id: str, db_path: Path) -> Optional[Any]:
    """Fetch task record via TaskManager or SQLite fallback."""
    if TaskManager is not None:
        try:
            manager = TaskManager(db_path=db_path)
            record = manager.get_task(task_id)
            if record is not None:
                return record
        except Exception:
            pass
    return _sqlite_get_task(db_path, task_id)


def update_task_record(task_id: str, db_path: Path, **fields: Any) -> Optional[Any]:
    """Update task record via TaskManager or SQLite fallback."""
    if TaskManager is not None:
        try:
            manager = TaskManager(db_path=db_path)
            updated = manager.update_task(task_id, **fields)
            if updated is not None:
                return updated
        except Exception:
            pass
    return _sqlite_update_task(db_path, task_id, **fields)


def setup_worker_logging(
    task_id: str,
    log_file_path: Optional[Union[Path, str]] = None,
) -> tuple[logging.Logger, Optional[logging.FileHandler]]:
    """Configure isolated logger for this worker process writing to log file and stdout."""
    logger = logging.getLogger(f"engine.worker.{task_id}")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    logger.propagate = False

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] [worker:%(process)d] %(message)s"
    )

    # Console stream handler
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    # File handler
    file_handler = None
    if log_file_path is not None:
        lp = Path(log_file_path)
        lp.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(str(lp), mode="a", encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger, file_handler


def run_worker(
    task_id: str,
    db_path: Optional[Union[Path, str]] = None,
    input_file: Optional[Union[Path, str]] = None,
    output_dir: Optional[Union[Path, str]] = None,
    runner: Optional[DualAgentRunner] = None,
) -> int:
    """Execute a task in the background worker protocol.

    Args:
        task_id: Unique task identifier to execute.
        db_path: Path to SQLite task ledger database.
        input_file: Optional path to file containing prompt text.
        output_dir: Optional directory to store generated artifact markdown.
        runner: Optional custom DualAgentRunner instance (useful for mocking in tests).

    Returns:
        0 on success, 1 on error.
    """
    resolved_db_path = Path(db_path).resolve() if db_path else DEFAULT_DB_PATH
    resolved_output_dir = Path(output_dir).resolve() if output_dir else DEFAULT_OUTPUT_DIR
    resolved_output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Fetch initial task record
    task = fetch_task_record(task_id, resolved_db_path)
    if task is None:
        sys.stderr.write(
            f"Error: Task '{task_id}' not found in database '{resolved_db_path}'.\n"
        )
        return 1

    # Check if task was already cancelled
    current_status = _get_val(task, "status")
    if current_status == "cancelled":
        sys.stdout.write(f"Task '{task_id}' is marked as cancelled. Exiting.\n")
        return 0

    # 2. Determine log file path
    log_file_val = _get_val(task, "log_file")
    if log_file_val:
        log_file_path = Path(log_file_val)
    else:
        DEFAULT_LOG_DIR.mkdir(parents=True, exist_ok=True)
        log_file_path = DEFAULT_LOG_DIR / f"{task_id}.log"

    logger, file_handler = setup_worker_logging(task_id, log_file_path)
    logger.info("Initializing worker for task: %s (PID: %d)", task_id, os.getpid())

    try:
        # 3. Update task status to 'running'
        started_at = datetime.now(timezone.utc).isoformat()
        pid = os.getpid()
        update_task_record(
            task_id,
            resolved_db_path,
            status="running",
            pid=pid,
            started_at=started_at,
            log_file=str(log_file_path),
        )
        logger.info("Task state transitioned to RUNNING at %s", started_at)

        # 4. Resolve input prompt
        prompt = ""
        if input_file:
            inp_path = Path(input_file)
            if inp_path.is_file():
                prompt = inp_path.read_text(encoding="utf-8")
                logger.info(
                    "Loaded prompt from input file: %s (%d chars)",
                    input_file,
                    len(prompt),
                )
            else:
                logger.warning(
                    "Input file %s does not exist; checking task record.", input_file
                )

        if not prompt:
            prompt_preview = _get_val(task, "input_preview", "")
            if prompt_preview and Path(prompt_preview).is_file():
                try:
                    prompt = Path(prompt_preview).read_text(encoding="utf-8")
                    logger.info("Loaded prompt from file path in input_preview.")
                except Exception:
                    prompt = prompt_preview
            else:
                prompt = prompt_preview or ""

        # 5. Extract skill and execution mode
        skill_name = _get_val(task, "skill_name")
        if not skill_name:
            raise ValueError(f"Task record {task_id} has no skill_name specified.")

        ensure_skills_registered()
        available_skills = AgentRegistry.list_skills()
        if skill_name not in available_skills:
            raise ValueError(
                f"Skill '{skill_name}' not found in AgentRegistry. "
                f"Available skills ({len(available_skills)}): {', '.join(available_skills)}"
            )

        mode = _get_val(task, "mode", "dual") or "dual"
        logger.info(
            "Executing skill '%s' in '%s' mode (Prompt length: %d chars)...",
            skill_name,
            mode,
            len(prompt),
        )

        # 6. Execute skill via DualAgentRunner
        if runner is None:
            runner = DualAgentRunner(max_refinements=2)

        result, scorecard = runner.run_skill(
            skill_name=skill_name,
            prompt=prompt,
            mode=mode,
        )

        logger.info(
            "Execution complete. Score: %d, Passed: %s, Iterations: %d",
            scorecard.score,
            scorecard.passed,
            scorecard.iteration,
        )

        # 7. Save generated artifact markdown
        artifact_path = resolved_output_dir / f"{skill_name}_{task_id}.md"
        artifact_path.write_text(result.content, encoding="utf-8")
        logger.info(
            "Saved artifact to %s (%d bytes)",
            artifact_path,
            len(result.content),
        )

        # 8. Update task record in DB to completed
        completed_at = datetime.now(timezone.utc).isoformat()
        verdict = "PASS" if scorecard.passed else "FAIL"

        update_task_record(
            task_id,
            resolved_db_path,
            status="completed",
            score=scorecard.score,
            verdict=verdict,
            output_file=str(artifact_path),
            completed_at=completed_at,
            exit_code=0,
            error_message=None,
        )
        logger.info(
            "Task %s marked COMPLETED (verdict=%s, score=%d)",
            task_id,
            verdict,
            scorecard.score,
        )
        return 0

    except Exception as exc:
        err_msg = str(exc)
        logger.error(
            "Fatal error executing task %s: %s\n%s",
            task_id,
            err_msg,
            traceback.format_exc(),
        )

        # Update task status to failed in DB
        try:
            completed_at = datetime.now(timezone.utc).isoformat()
            update_task_record(
                task_id,
                resolved_db_path,
                status="failed",
                error_message=err_msg,
                completed_at=completed_at,
                exit_code=1,
            )
            logger.info("Task %s marked FAILED in ledger.", task_id)
        except Exception as db_exc:
            logger.error("Failed to update task state in DB: %s", db_exc)

        return 1

    finally:
        # Close and clean up file handler to prevent file lock leaks on Windows
        if file_handler is not None:
            file_handler.close()
            logger.removeHandler(file_handler)
        for h in list(logger.handlers):
            h.close()
            logger.removeHandler(h)


def main(argv: Optional[list[str]] = None) -> int:
    """CLI entrypoint parser for standalone background worker process."""
    parser = argparse.ArgumentParser(
        description="AI_Flow Standalone Background Agent Worker Process"
    )
    parser.add_argument(
        "--task-id",
        type=str,
        required=True,
        help="Unique task ID to process from ledger",
    )
    parser.add_argument(
        "--db-path",
        type=str,
        default=None,
        help="Path to SQLite tasks database (default: data/tasks.db)",
    )
    parser.add_argument(
        "--input-file",
        type=str,
        default=None,
        help="Path to file containing full prompt input",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Directory to save generated artifacts (default: output/)",
    )

    args = parser.parse_args(argv)
    exit_code = run_worker(
        task_id=args.task_id,
        db_path=args.db_path,
        input_file=args.input_file,
        output_dir=args.output_dir,
    )
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
