import sqlite3
import time

import config


def _conn():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute(
        "CREATE TABLE IF NOT EXISTS messages ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT, content TEXT, created REAL)"
    )
    return conn


def add(role, content):
    with _conn() as conn:
        conn.execute(
            "INSERT INTO messages (role, content, created) VALUES (?, ?, ?)",
            (role, content, time.time()),
        )


def recent(limit=50):
    with _conn() as conn:
        rows = conn.execute(
            "SELECT id, role, content, created FROM messages ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(r) for r in reversed(rows)]


def delete_range(scope):
    """scope: 'hour', 'day' ya 'all'."""
    with _conn() as conn:
        if scope == "all":
            cur = conn.execute("DELETE FROM messages")
        else:
            seconds = {"hour": 3600, "day": 86400}.get(scope)
            if seconds is None:
                raise ValueError("scope 'hour', 'day' ya 'all' hona chahiye")
            cur = conn.execute(
                "DELETE FROM messages WHERE created >= ?", (time.time() - seconds,)
            )
        return cur.rowcount
