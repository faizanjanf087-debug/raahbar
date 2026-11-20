import time
import uuid

_pending = {}


def create(action, detail):
    approval_id = uuid.uuid4().hex[:8]
    _pending[approval_id] = {
        "id": approval_id,
        "action": action,
        "detail": detail,
        "status": "pending",
        "created": time.time(),
    }
    return _pending[approval_id]


def list_all(timeout=300):
    now = time.time()
    for item in _pending.values():
        if item["status"] == "pending" and now - item["created"] > timeout:
            item["status"] = "expired"
    return sorted(_pending.values(), key=lambda x: x["created"], reverse=True)


def get(approval_id):
    return _pending.get(approval_id)


def decide(approval_id, approve, timeout=300):
    item = _pending.get(approval_id)
    if not item or item["status"] != "pending":
        return None
    if time.time() - item["created"] > timeout:
        item["status"] = "expired"
        return None
    item["status"] = "approved" if approve else "denied"
    return item
