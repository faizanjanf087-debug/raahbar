import json
import os
import uuid

import config
from security import vault


def _load():
    if not os.path.exists(config.VPS_PATH):
        return []
    with open(config.VPS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(items):
    with open(config.VPS_PATH, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def list_vps():
    """Public list: private key kabhi wapas nahi jati."""
    return [{k: v for k, v in item.items() if k != "key_enc"} for item in _load()]


def add_vps(name, host, user, private_key):
    items = _load()
    item = {
        "id": uuid.uuid4().hex[:8],
        "name": name,
        "host": host,
        "user": user,
        "key_enc": vault.encrypt(private_key),
    }
    items.append(item)
    _save(items)
    return {k: v for k, v in item.items() if k != "key_enc"}


def remove_vps(vps_id):
    items = [item for item in _load() if item["id"] != vps_id]
    _save(items)


def get_vps(vps_id):
    """Sirf internal use (SSH) ke liye: decrypted key ke saath."""
    for item in _load():
        if item["id"] == vps_id:
            return {**item, "key": vault.decrypt(item["key_enc"])}
    raise KeyError(f"VPS '{vps_id}' nahi mila")
