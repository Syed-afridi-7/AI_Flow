import datetime
import os
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional


class TopicMemory:
    """Tracks generated and posted content topics using a local SQLite database to prevent repetition."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # Default to data/memory.db under AI_Flow root
            repo_root = Path(__file__).resolve().parent.parent.parent.parent
            data_dir = repo_root / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            db_path = str(data_dir / "memory.db")
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Create tables if they do not exist."""
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS posted_topics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    theme TEXT NOT NULL,
                    hook TEXT NOT NULL,
                    format_type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()

    def record_topic(
        self,
        theme: str,
        hook: str,
        format_type: str = "reel",
        date_str: Optional[str] = None,
    ):
        """Record a generated topic into memory."""
        if date_str is None:
            date_str = datetime.date.today().isoformat()

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO posted_topics (date, theme, hook, format_type)
                VALUES (?, ?, ?, ?)
                """,
                (date_str, theme.strip(), hook.strip(), format_type.strip()),
            )
            conn.commit()

    def get_recent_topics(self, days: int = 14) -> List[Dict]:
        """Fetch all topics generated in the last N days."""
        cutoff = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
        with self._get_connection() as conn:
            cur = conn.execute(
                """
                SELECT id, date, theme, hook, format_type, created_at
                FROM posted_topics
                WHERE date >= ?
                ORDER BY id DESC
                """,
                (cutoff,),
            )
            rows = cur.fetchall()
            return [dict(row) for row in rows]

    def is_topic_recent(self, theme: str, days: int = 14) -> bool:
        """Check if a similar topic or theme was generated recently."""
        recent = self.get_recent_topics(days=days)
        theme_clean = theme.lower().strip()
        for item in recent:
            if theme_clean in item["theme"].lower() or item["theme"].lower() in theme_clean:
                return True
        return False

    def get_topic_count(self) -> int:
        """Get total count of recorded topics."""
        with self._get_connection() as conn:
            cur = conn.execute("SELECT COUNT(*) FROM posted_topics")
            return cur.fetchone()[0]
