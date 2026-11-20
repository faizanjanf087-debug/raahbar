import json
import time

import config


def log(event, **details):
    entry = {"time": time.strftime("%Y-%m-%d %H:%M:%S"), "event": event, **details}
    with open(config.AUDIT_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def tail(limit=100):
    try:
        with open(config.AUDIT_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()[-limit:]
    except FileNotFoundError:
        return []
    return [json.loads(line) for line in lines]
