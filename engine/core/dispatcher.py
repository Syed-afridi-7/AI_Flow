"""Universal Detached Background Agent Dispatcher for AI_Flow.

Provides zero-dependency detached process spawning across Windows and Unix platforms,
PID lifecycle management, dead process reconciliation, log retrieval, and task cancellation
using 100% Python standard library.
"""

from datetime import datetime, timezone
import logging
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from typing import Any, Optional, Union

from engine.core.task_manager import TaskManager, TaskRecord

# Set up logger
logger = logging.getLogger("engine.core.dispatcher")

# Repository root: ../../../
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_DB_PATH = REPO_ROOT / "data" / "tasks.db"
DEFAULT_LOG_DIR = REPO_ROOT / "data" / "logs"
DEFAULT_SPOOL_DIR = REPO_ROOT / "data" / "spool"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output"

# Cross-platform detached process constants
DETACHED_PROCESS = getattr(subprocess, "DETACHED_PROCESS", 0x00000008)
CREATE_NEW_PROCESS_GROUP = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200)


class AgentDispatcher:
    """Dispatches and manages asynchronous background agent execution processes."""

    def __init__(
        self,
        db_path: Optional[Union[Path, str]] = None,
        log_dir: Optional[Union[Path, str]] = None,
        spool_dir: Optional[Union[Path, str]] = None,
        output_dir: Optional[Union[Path, str]] = None,
    ) -> None:
        """Initialize AgentDispatcher with database and storage directories."""
        self.task_manager = TaskManager(db_path=db_path)

        if log_dir is None:
            self.log_dir = DEFAULT_LOG_DIR
        else:
            self.log_dir = Path(log_dir)

        if spool_dir is None:
            self.spool_dir = DEFAULT_SPOOL_DIR
        else:
            self.spool_dir = Path(spool_dir)

        if output_dir is None:
            self.output_dir = DEFAULT_OUTPUT_DIR
        else:
            self.output_dir = Path(output_dir)

        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.spool_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @property
    def db_path(self) -> Path:
        """Return the database path used by TaskManager."""
        return self.task_manager.db_path

    def dispatch(
        self,
        skill_name: str,
        input_text: str = "",
        mode: str = "dual",
        provider: str = "local",
        output_dir: Optional[str] = None,
    ) -> TaskRecord:
        """Spawn a detached background worker process executing the requested skill.

        Returns immediately (< 50ms) with a TaskRecord containing task_id and worker pid.

        Args:
            skill_name: Name of registered skill to execute.
            input_text: Input prompt text or instructions for the agent.
            mode: Execution mode ('dual' or 'single').
            provider: LLM inference provider ('local', 'gemini', 'ollama', etc.).
            output_dir: Optional directory override for artifact outputs.

        Returns:
            TaskRecord: The created and running task record with PID assigned.
        """
        # 1. Generate unique task ID
        task_id = self.task_manager.generate_task_id()

        # 2. Configure log file and spooling for long input prompts
        log_path = self.log_dir / f"{task_id}.log"
        input_file: Optional[Path] = None
        input_preview = (input_text[:200] if input_text else "").strip()

        if len(input_text) > 200:
            self.spool_dir.mkdir(parents=True, exist_ok=True)
            input_file = self.spool_dir / f"{task_id}.input"
            input_file.write_text(input_text, encoding="utf-8")

        # 3. Create initial record in database
        record = self.task_manager.create_task(
            task_id=task_id,
            skill_name=skill_name,
            mode=mode,
            provider=provider,
            log_file=str(log_path),
            input_preview=input_preview,
            status="running",
        )

        # 4. Build detached worker command line
        cmd = [
            sys.executable,
            "-m",
            "engine.core.worker",
            "--task-id",
            task_id,
            "--db-path",
            str(self.task_manager.db_path),
        ]
        if input_file is not None:
            cmd.extend(["--input-file", str(input_file)])
        if output_dir is not None:
            cmd.extend(["--output-dir", str(output_dir)])
        elif self.output_dir != DEFAULT_OUTPUT_DIR:
            cmd.extend(["--output-dir", str(self.output_dir)])

        # 5. Open log file and configure detached process parameters
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_fp = open(log_path, "a", encoding="utf-8")

        popen_kwargs: dict[str, Any] = {
            "stdin": subprocess.DEVNULL,
            "stdout": log_fp,
            "stderr": subprocess.STDOUT,
        }

        if os.name == "nt":
            popen_kwargs["creationflags"] = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
            popen_kwargs["close_fds"] = True
        else:
            popen_kwargs["start_new_session"] = True

        try:
            proc = subprocess.Popen(cmd, cwd=str(REPO_ROOT), **popen_kwargs)
        except Exception as exc:
            self.task_manager.update_task(
                task_id,
                status="failed",
                error_message=f"Failed to spawn background worker: {exc}",
                exit_code=1,
            )
            raise
        finally:
            log_fp.close()

        # 6. Update task record with worker PID
        updated_record = self.task_manager.update_task(task_id, pid=proc.pid)
        return updated_record or record

    def is_pid_alive(self, pid: Optional[int]) -> bool:
        """Check if a process with given PID is actively running.

        Works reliably on Windows (via OpenProcess and WaitForSingleObject or tasklist)
        and Unix (via os.kill(pid, 0)).

        Args:
            pid: Process ID to check.

        Returns:
            bool: True if process is alive, False otherwise.
        """
        if pid is None or pid <= 0:
            return False

        if os.name == "nt":
            try:
                import ctypes

                PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
                SYNCHRONIZE = 0x00100000
                WAIT_TIMEOUT = 258

                kernel32 = ctypes.windll.kernel32
                handle = kernel32.OpenProcess(
                    PROCESS_QUERY_LIMITED_INFORMATION | SYNCHRONIZE, False, int(pid)
                )
                if not handle:
                    return False
                try:
                    wait_res = kernel32.WaitForSingleObject(handle, 0)
                    return wait_res == WAIT_TIMEOUT
                finally:
                    kernel32.CloseHandle(handle)
            except Exception:
                pass

            try:
                res = subprocess.run(
                    ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
                return str(pid) in res.stdout
            except Exception:
                return False
        else:
            try:
                os.kill(pid, 0)
                return True
            except OSError as err:
                import errno

                return err.errno == errno.EPERM

    def _terminate_pid(self, pid: int) -> bool:
        """Terminate a process by PID across platforms."""
        if pid <= 0:
            return False

        if os.name == "nt":
            # 1. Try taskkill /F /T to terminate child process tree
            try:
                res = subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(pid)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=5,
                )
                if res.returncode == 0:
                    return True
            except Exception:
                pass

            # 2. Try TerminateProcess via ctypes
            try:
                import ctypes

                PROCESS_TERMINATE = 0x0001
                kernel32 = ctypes.windll.kernel32
                handle = kernel32.OpenProcess(PROCESS_TERMINATE, False, int(pid))
                if handle:
                    try:
                        if kernel32.TerminateProcess(handle, 1):
                            return True
                    finally:
                        kernel32.CloseHandle(handle)
            except Exception:
                pass

            # 3. Fallback to os.kill
            try:
                os.kill(pid, signal.SIGTERM)
                return True
            except OSError:
                return False
        else:
            try:
                os.kill(pid, signal.SIGTERM)
                return True
            except OSError:
                return False

    def get_status(self, task_id: str) -> Optional[TaskRecord]:
        """Retrieve task record with automatic dead PID reconciliation.

        If a task is marked 'running' but its process is no longer alive,
        the task status is updated to 'failed' with error_message='Process terminated unexpectedly'.

        Args:
            task_id: Unique task identifier.

        Returns:
            Optional[TaskRecord]: Current task record or None if not found.
        """
        record = self.task_manager.get_task(task_id)
        if record is None:
            return None

        if record.status == "running":
            if not record.pid or not self.is_pid_alive(record.pid):
                record = self.task_manager.update_task(
                    task_id,
                    status="failed",
                    error_message="Process terminated unexpectedly",
                    exit_code=-1,
                )
        return record

    def reconcile_tasks(self) -> list[TaskRecord]:
        """Scan running tasks and reconcile any with dead PIDs.

        Returns:
            List of TaskRecord instances that were transitioned to failed.
        """
        running_tasks = self.task_manager.list_tasks(status="running", limit=500)
        reconciled: list[TaskRecord] = []
        for task in running_tasks:
            if not task.pid or not self.is_pid_alive(task.pid):
                updated = self.task_manager.update_task(
                    task.task_id,
                    status="failed",
                    error_message="Process terminated unexpectedly",
                    exit_code=-1,
                )
                if updated:
                    reconciled.append(updated)
        return reconciled

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task and terminate its process.

        Args:
            task_id: Unique task identifier to cancel.

        Returns:
            bool: True if task was running and cancelled, False if not found or already terminal.
        """
        record = self.task_manager.get_task(task_id)
        if record is None:
            return False

        if record.status in ("completed", "failed", "cancelled"):
            return False

        if record.pid and self.is_pid_alive(record.pid):
            self._terminate_pid(record.pid)

        self.task_manager.update_task(
            task_id,
            status="cancelled",
            error_message="Task cancelled by user",
        )
        return True

    def list_tasks(
        self,
        status: Optional[str] = None,
        skill_name: Optional[str] = None,
        limit: int = 50,
        reconcile: bool = True,
    ) -> list[TaskRecord]:
        """List tasks with optional status and skill filtering, ordered newest first.

        Args:
            status: Optional filter by status ('running', 'completed', 'failed', 'cancelled').
            skill_name: Optional filter by skill name.
            limit: Maximum number of records to return (default: 50).
            reconcile: If True, reconciles dead PIDs before returning results.

        Returns:
            list[TaskRecord]: Task records matching filters.
        """
        if reconcile:
            self.reconcile_tasks()
        return self.task_manager.list_tasks(
            status=status,
            skill_name=skill_name,
            limit=limit,
        )

    def get_logs(self, task_id: str, tail: int = 50) -> str:
        """Retrieve execution log contents for a given task ID.

        Args:
            task_id: Unique task identifier.
            tail: Number of trailing lines to return (0 or negative returns all lines).

        Returns:
            str: Log content, or empty string if no log file exists.
        """
        record = self.task_manager.get_task(task_id)
        log_path: Optional[Path] = None
        if record and record.log_file:
            log_path = Path(record.log_file)
        else:
            log_path = self.log_dir / f"{task_id}.log"

        if not log_path.is_file():
            return ""

        try:
            with open(log_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
                if tail > 0:
                    lines = lines[-tail:]
                return "".join(lines)
        except Exception as exc:
            logger.warning("Failed to read log file %s: %s", log_path, exc)
            return ""

    def prune_tasks(self, older_than_days: int = 7) -> int:
        """Delete task records older than specified days.

        Args:
            older_than_days: Cutoff threshold in days.

        Returns:
            int: Number of pruned tasks.
        """
        return self.task_manager.prune_tasks(older_than_days=older_than_days)
