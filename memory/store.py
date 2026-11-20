"""Chat history ka database.

DATABASE_URL set ho (Neon ka Postgres URL) to Postgres use hoga.
Warna local SQLite file (data/memory.db) use hogi, jo local development ke liye hai.
"""
import os
import sqlite3
import time

import config

DATABASE_URL = os.getenv("DATABASE_URL", "")
IS_POSTGRES = DATABASE_URL.startswith(("postgres://", "postgresql://"))


def _run(sql, params=(), fetch=None):
    """fetch: 'all' (rows), 'rowcount' (kitni rows badlin), ya None."""
    if IS_POSTGRES:
        import psycopg
        with psycopg.connect(DATABASE_URL) as conn, conn.cursor() as cur:
            cur.execute(sql, params)
            if fetch == "all":
                cols = [d.name for d in cur.description]
                return [dict(zip(cols, row)) for row in cur.fetchall()]
            if fetch == "rowcount":
                return cur.rowcount
            return None

    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.execute(sql.replace("%s", "?"), params)
        conn.commit()
        if fetch == "all":
            return [dict(r) for r in cur.fetchall()]
        if fetch == "rowcount":
            return cur.rowcount
        return None
    finally:
        conn.close()


def init():
    id_column = "BIGSERIAL PRIMARY KEY" if IS_POSTGRES else "INTEGER PRIMARY KEY AUTOINCREMENT"
    _run(
        f"CREATE TABLE IF NOT EXISTS messages (id {id_column}, role TEXT, content TEXT, created DOUBLE PRECISION)"
    )


def add(role, content):
    _run(
        "INSERT INTO messages (role, content, created) VALUES (%s, %s, %s)",
        (role, content, time.time()),
    )


def recent(limit=50):
    rows = _run(
        "SELECT id, role, content, created FROM messages ORDER BY id DESC LIMIT %s",
        (limit,),
        fetch="all",
    )
    return list(reversed(rows))


def delete_range(scope):
    """scope: 'hour', 'day' ya 'all'."""
    if scope == "all":
        return _run("DELETE FROM messages", fetch="rowcount")
    seconds = {"hour": 3600, "day": 86400}.get(scope)
    if seconds is None:
        raise ValueError("scope 'hour', 'day' ya 'all' hona chahiye")
    return _run(
        "DELETE FROM messages WHERE created >= %s",
        (time.time() - seconds,),
        fetch="rowcount",
    )


init()
