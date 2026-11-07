"""SQLite Task Ledger and Manager for asynchronous background agent execution.

Provides an ACID SQLite-backed task ledger tracking execution status, PIDs,
scores, verdicts, and logs across all 30 AI_Flow skills and 60 dual personas.
"""

from contextlib import contextmanager
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
import os
from pathlib import Path
import sqlite3
from typing import Any, Generator, Optional, Union
import uuid

# Project root: ../../../
REPO_ROOT = Path(__file__).resolve().parent.parent.parent


@dataclass
class TaskRecord:
    task_id: str
    skill_name: str
    mode: str = "dual"
    provider: str = "local"
    status: str = "running"
    pid: Optional[int] = None
    input_preview: str = ""
    started_at: str = ""
    completed_at: Optional[str] = None
    exit_code: Optional[int] = None
    score: Optional[int] = None
    verdict: Optional[str] = None
    output_file: Optional[str] = None
    log_file: Optional[str] = None
    error_message: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_row(cls, row: Union[sqlite3.Row, dict[str, Any]]) -> "TaskRecord":
        if isinstance(row, sqlite3.Row):
            data = dict(row)
        else:
            data = dict(row)
        return cls(**data)


class TaskManager:
    """Manages background task state in an ACID SQLite database."""

    VALID_COLUMNS = {
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

    def __init__(self, db_path: Optional[Union[Path, str]] = None) -> None:
        if db_path is None:
            self.db_path = REPO_ROOT / "data" / "tasks.db"
        else:
            self.db_path = Path(db_path)

        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @contextmanager
    def _connect(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout = 5000;")
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_tasks (
                    task_id TEXT PRIMARY KEY,
                    skill_name TEXT NOT NULL,
                    mode TEXT NOT NULL DEFAULT 'dual',
                    provider TEXT NOT NULL DEFAULT 'local',
                    status TEXT NOT NULL DEFAULT 'running',
                    pid INTEGER,
                    input_preview TEXT DEFAULT '',
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    exit_code INTEGER,
                    score INTEGER,
                    verdict TEXT,
                    output_file TEXT,
                    log_file TEXT,
                    error_message TEXT
                );
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_tasks_status ON agent_tasks(status);"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_tasks_skill ON agent_tasks(skill_name);"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_tasks_started ON agent_tasks(started_at);"
            )

    @staticmethod
    def generate_task_id() -> str:
        """Generate a unique task ID in format: task_YYYYMMDD_HHMMSS_<8 hex chars>."""
        now = datetime.now(timezone.utc)
        hex_suffix = uuid.uuid4().hex[:8]
        return f"task_{now.strftime('%Y%m%d_%H%M%S')}_{hex_suffix}"

    def create_task(
        self,
        skill_name: str,
        input_text: str = "",
        mode: str = "dual",
        provider: str = "local",
        pid: Optional[int] = None,
        log_file: Optional[str] = None,
        task_id: Optional[str] = None,
        status: str = "running",
        input_preview: Optional[str] = None,
        output_file: Optional[str] = None,
        **kwargs: Any,
    ) -> TaskRecord:
        """Create and persist a new task record."""
        if task_id is None:
            task_id = self.generate_task_id()

        if input_preview is None:
            input_preview = (input_text[:200] if input_text else "").strip()

        started_at = kwargs.get("started_at") or datetime.now(timezone.utc).isoformat()

        record = TaskRecord(
            task_id=task_id,
            skill_name=skill_name,
            mode=mode,
            provider=provider,
            status=status,
            pid=pid,
            input_preview=input_preview,
            started_at=started_at,
            completed_at=kwargs.get("completed_at"),
            exit_code=kwargs.get("exit_code"),
            score=kwargs.get("score"),
            verdict=kwargs.get("verdict"),
            output_file=output_file or kwargs.get("output_file"),
            log_file=log_file or kwargs.get("log_file"),
            error_message=kwargs.get("error_message"),
        )

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO agent_tasks (
                    task_id, skill_name, mode, provider, status, pid,
                    input_preview, started_at, completed_at, exit_code,
                    score, verdict, output_file, log_file, error_message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    record.task_id,
                    record.skill_name,
                    record.mode,
                    record.provider,
                    record.status,
                    record.pid,
                    record.input_preview,
                    record.started_at,
                    record.completed_at,
                    record.exit_code,
                    record.score,
                    record.verdict,
                    record.output_file,
                    record.log_file,
                    record.error_message,
                ),
            )

        return record

    def update_task(self, task_id: str, **fields: Any) -> Optional[TaskRecord]:
        """Update fields on an existing task. Auto-sets completed_at on terminal status."""
        if not fields:
            return self.get_task(task_id)

        clean_fields = {k: v for k, v in fields.items() if k in self.VALID_COLUMNS}
        if not clean_fields:
            return self.get_task(task_id)

        status = clean_fields.get("status")
        if (
            status in ("completed", "failed", "cancelled")
            and "completed_at" not in clean_fields
        ):
            clean_fields["completed_at"] = datetime.now(timezone.utc).isoformat()

        set_clause = ", ".join(f"{col} = ?" for col in clean_fields.keys())
        params = list(clean_fields.values())
        params.append(task_id)

        with self._connect() as conn:
            cursor = conn.execute(
                f"UPDATE agent_tasks SET {set_clause} WHERE task_id = ?;",
                params,
            )
            if cursor.rowcount == 0:
                return None

        return self.get_task(task_id)

    def get_task(self, task_id: str) -> Optional[TaskRecord]:
        """Retrieve a task record by ID."""
        with self._connect() as conn:
            cursor = conn.execute(
                "SELECT * FROM agent_tasks WHERE task_id = ?;",
                (task_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return TaskRecord.from_row(row)

    def list_tasks(
        self,
        status: Optional[str] = None,
        skill_name: Optional[str] = None,
        limit: int = 50,
    ) -> list[TaskRecord]:
        """List tasks with optional filtering, ordered by newest first."""
        query = "SELECT * FROM agent_tasks"
        conditions: list[str] = []
        params: list[Any] = []

        if status:
            conditions.append("status = ?")
            params.append(status)

        if skill_name:
            conditions.append("skill_name = ?")
            params.append(skill_name)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY started_at DESC LIMIT ?;"
        params.append(limit)

        with self._connect() as conn:
            cursor = conn.execute(query, params)
            return [TaskRecord.from_row(row) for row in cursor.fetchall()]

    def delete_task(self, task_id: str) -> bool:
        """Delete a task record by ID. Returns True if deleted."""
        with self._connect() as conn:
            cursor = conn.execute(
                "DELETE FROM agent_tasks WHERE task_id = ?;",
                (task_id,),
            )
            return cursor.rowcount > 0

    def prune_tasks(self, older_than_days: int = 7) -> int:
        """Delete task records older than older_than_days. Returns count of pruned tasks."""
        cutoff = (datetime.now(timezone.utc) - timedelta(days=older_than_days)).isoformat()
        with self._connect() as conn:
            cursor = conn.execute(
                "DELETE FROM agent_tasks WHERE started_at < ?;",
                (cutoff,),
            )
            return cursor.rowcount
