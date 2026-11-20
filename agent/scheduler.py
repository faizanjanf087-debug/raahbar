"""Scheduled tasks: ek background thread jo har minute check karta hai.

Sirf read-level commands aur read-only browse schedule ho sakte hain.
Write kaam (install, delete, upload) schedule nahi hote, un ke liye
approval chahiye hota hai, jo sirf aap ki maujoodgi mein milta hai.
"""
import json
import os
import threading
import time
import uuid

import config
from security import audit, policy

TASKS_PATH = os.path.join(config.DATA_DIR, "scheduled_tasks.json")
_lock = threading.Lock()
_started = False


def _load():
    if not os.path.exists(TASKS_PATH):
        return []
    with open(TASKS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(items):
    with open(TASKS_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def list_tasks():
    with _lock:
        return _load()


def add_task(name, command, interval_minutes):
    interval_minutes = max(5, int(interval_minutes))
    if command.startswith("/browse "):
        allowed = True
    elif command.startswith("/status "):
        allowed = True
    elif command.startswith("/run "):
        parts = command.split(maxsplit=2)
        allowed = len(parts) == 3 and policy.classify(parts[2]) == "read"
    else:
        allowed = False
    if not allowed:
        raise ValueError("sirf /browse, /status, ya read-level /run schedule ho sakte hain")
    with _lock:
        items = _load()
        item = {
            "id": uuid.uuid4().hex[:8],
            "name": name,
            "command": command,
            "interval_minutes": interval_minutes,
            "last_run": None,
            "last_result": None,
        }
        items.append(item)
        _save(items)
    audit.log("task_added", task=item["id"], command=command)
    return item


def remove_task(task_id):
    with _lock:
        items = [t for t in _load() if t["id"] != task_id]
        _save(items)
    audit.log("task_removed", task=task_id)


def _run_command(command):
    # planner circular import se bachne ke liye yahan import
    from agent import planner
    return planner.handle(command)


def _loop():
    while True:
        now = time.time()
        with _lock:
            items = _load()
            due = [
                t for t in items
                if t["last_run"] is None
                or now - t["last_run"] >= t["interval_minutes"] * 60
            ]
        for task in due:
            try:
                result = _run_command(task["command"])
            except Exception as exc:
                result = f"Error: {exc}"
            with _lock:
                items = _load()
                for t in items:
                    if t["id"] == task["id"]:
                        t["last_run"] = time.time()
                        t["last_result"] = str(result)[:2000]
                _save(items)
            audit.log("task_ran", task=task["id"], command=task["command"])
        time.sleep(60)


def start():
    global _started
    if _started:
        return
    _started = True
    threading.Thread(target=_loop, daemon=True).start()
