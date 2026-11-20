from agent import browser, router, voice
from memory import store
from providers import deepseek
from security import approvals, audit, policy
from settings_store import load as load_settings
from vps import registry, ssh, status as vps_status

SYSTEM_PROMPT = (
    "Tum Raahbar ho, mere personal assistant. Roman Urdu mein jawab do. "
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
        return _request_command(vps_id, command)

    if text.startswith("/browse "):
        rest = text.split(maxsplit=1)[1].strip()
        want_shot = rest.endswith("--shot")
        url = rest.replace("--shot", "").strip()
        page = browser.read_page(url, screenshot=want_shot)
        reply = f"{page['title']}\n\n{page['text']}"
        if page["screenshot"]:
            name = page["screenshot"].rsplit("/", 1)[-1]
            reply += f"\n\nScreenshot: /api/screenshots/{name}"
        return reply

    if text.startswith("/act "):
        return _request_browser_action(text)

    if text.startswith("/voice "):
        name = voice.generate(text[len("/voice "):])
        return f"Voice tayyar hai: /api/audio/{name}"

    if text.startswith("/schedule"):
        return _schedule_command(text)

    return _ask_model(text, settings)


USAGE_ACT = (
    "Istemaal: /act <url> | click | <selector>\n"
    "ya: /act <url> | type | <selector> | <text>\n"
    "Kai steps ek saath: /act <url> | click | <sel> ;; type | <sel> | <text> ;; click | <sel>\n"
    "Password kabhi type na karein, wo khud daalein."
)


def _request_browser_action(text):
    # ;; se steps alag hote hain. Pehle step mein pehla hissa URL hai.
    chunks = [c.strip() for c in text[len("/act "):].split(";;") if c.strip()]
    if not chunks:
        return USAGE_ACT
    url = chunks[0].split("|")[0].strip()
    steps = []
    for index, chunk in enumerate(chunks):
        parts = [p.strip() for p in chunk.split("|")]
        if index == 0:
            parts = parts[1:]  # URL hata do
        if len(parts) < 2 or parts[0] not in ("click", "type"):
            return USAGE_ACT
        kind, selector = parts[0], parts[1]
        step = {"action": kind, "selector": selector}
        if kind == "type":
            if len(parts) < 3:
                return "type ke liye text bhi dein.\n" + USAGE_ACT
            step["text"] = parts[2]
        steps.append(step)
    browser.check_url(url)
    item = approvals.create("browser_actions", {"url": url, "actions": steps})
    audit.log("browser_action_requested", approval=item["id"], url=url, steps=len(steps))
    return (
        f"{len(steps)} step(s) ke liye approval chahiye (id: {item['id']}). "
        "Approvals tab mein dekh kar confirm karein."
    )


def _vps_list():
    items = registry.list_vps()
    if not items:
        return "Abhi koi VPS add nahi hua. Settings > VPS mein add karein."
    lines = [f"- {v['id']} | {v['name']} | {v['host']}" for v in items]
    return "Aap ke VPS:\n" + "\n".join(lines)


def _request_command(vps_id, command):
    level = policy.classify(command)
    audit.log("command_requested", vps=vps_id, command=command, level=level)
    if level == "blocked":
        return "Ye command block hai aur nahi chalega."
    if level == "read":
        result = ssh.run(vps_id, command)
        audit.log("command_ran", vps=vps_id, command=command, exit_code=result["exit_code"])
        return _format_result(result)
    item = approvals.create("run_command", {"vps": vps_id, "command": command})
    return f"Approval chahiye (id: {item['id']}). Approvals tab mein dekh kar confirm karein."


def _schedule_command(text):
    # /schedule list | /schedule add <minutes> <command> | /schedule remove <id>
    from agent import scheduler
    parts = text.split(maxsplit=3)
    if len(parts) == 1 or parts[1] == "list":
        items = scheduler.list_tasks()
        if not items:
            return "Koi scheduled task nahi."
        return "\n".join(
            f"- {t['id']} | har {t['interval_minutes']} min | {t['command']}" for t in items
        )
    if parts[1] == "add" and len(parts) == 4:
        item = scheduler.add_task(f"task-{len(scheduler.list_tasks()) + 1}", parts[3], parts[2])
        return f"Task add ho gaya (id: {item['id']})."
    if parts[1] == "remove" and len(parts) >= 3:
        scheduler.remove_task(parts[2])
        return "Task remove ho gaya."
    return "Istemaal: /schedule list | /schedule add <minutes> <command> | /schedule remove <id>"


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
    model = router.pick(text, settings["chat_model"])
    audit.log("model_selected", model=model, mode=settings["chat_model"])
    return deepseek.chat(messages, model)
