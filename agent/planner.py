from memory import store
from providers import deepseek
from security import approvals, audit, policy
from settings_store import load as load_settings
from vps import registry, ssh, status as vps_status

SYSTEM_PROMPT = (
    "Tum mere personal assistant ho. Roman Urdu mein jawab do. "
    "Tum sirf wahi kaam batao jo user ne maangay hain. "
    "VPS par commands sirf user ke approval ke baad chalte hain."
)


def handle(user_text):
    settings = load_settings()
    text = user_text.strip()

    if text.startswith("/vps"):
        return _vps_list()

    if text.startswith("/status "):
        vps_id = text.split(maxsplit=1)[1].strip()
        return vps_status.check(vps_id)

    if text.startswith("/run "):
        parts = text.split(maxsplit=2)
        if len(parts) < 3:
            return "Istemaal: /run <vps_id> <command>"
        _, vps_id, command = parts
        return _request_command(vps_id, command, settings)

    return _ask_model(text, settings)


def _vps_list():
    items = registry.list_vps()
    if not items:
        return "Abhi koi VPS add nahi hua. Settings > VPS mein add karein."
    lines = [f"- {v['id']} | {v['name']} | {v['host']}" for v in items]
    return "Aap ke VPS:\n" + "\n".join(lines)


def _request_command(vps_id, command, settings):
    level = policy.classify(command)
    audit.log("command_requested", vps=vps_id, command=command, level=level)
    if level == "blocked":
        return "Ye command block hai aur nahi chalega."
    if level == "read":
        result = ssh.run(vps_id, command)
        audit.log("command_ran", vps=vps_id, command=command, exit_code=result["exit_code"])
        return _format_result(result)
    item = approvals.create("run_command", {"vps": vps_id, "command": command})
    return (
        f"Approval chahiye (id: {item['id']}). "
        "Approvals tab mein dekh kar confirm karein."
    )


def _format_result(result):
    body = result["stdout"] or result["stderr"] or "(koi output nahi)"
    return f"exit code {result['exit_code']}\n{body}"


def _ask_model(text, settings):
    history = store.recent(20)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for item in history:
        role = "assistant" if item["role"] == "assistant" else "user"
        messages.append({"role": role, "content": item["content"]})
    messages.append({"role": "user", "content": text})
    return deepseek.chat(messages, settings["deepseek_model"])
