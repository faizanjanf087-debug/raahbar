import os
from functools import wraps

from flask import Flask, jsonify, render_template, request, session

import config
import settings_store
from agent import browser, planner, scheduler
from memory import store
from providers import deepseek, elevenlabs, gemini
from security import approvals, audit
from vps import registry, ssh

app = Flask(__name__)
app.secret_key = config.FLASK_SECRET


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if config.OWNER_PASSWORD and not session.get("ok"):
            return jsonify({"error": "login chahiye"}), 401
        return view(*args, **kwargs)

    return wrapper


@app.route("/")
def index():
    if config.OWNER_PASSWORD and not session.get("ok"):
        return render_template("login.html")
    return render_template(
        "index.html",
        deepseek_models=config.DEEPSEEK_MODELS,
        gemini_models=config.GEMINI_MODELS,
        elevenlabs_models=config.ELEVENLABS_MODELS,
    )


@app.route("/login", methods=["POST"])
def login():
    if request.form.get("password") == config.OWNER_PASSWORD:
        session["ok"] = True
        audit.log("login_ok")
        return jsonify({"ok": True})
    audit.log("login_failed")
    return jsonify({"error": "galat password"}), 403


@app.route("/api/chat", methods=["POST"])
@login_required
def chat():
    text = (request.json or {}).get("message", "").strip()
    if not text:
        return jsonify({"error": "message khali hai"}), 400
    store.add("user", text)
    try:
        reply = planner.handle(text)
    except Exception as exc:  # error ko user tak pahunchana
        reply = f"Error: {exc}"
    store.add("assistant", reply)
    return jsonify({"reply": reply})


@app.route("/api/history")
@login_required
def history():
    limit = int(request.args.get("limit", 50))
    return jsonify(store.recent(limit))


@app.route("/api/history/delete", methods=["POST"])
@login_required
def history_delete():
    scope = (request.json or {}).get("scope", "")
    try:
        removed = store.delete_range(scope)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    audit.log("history_deleted", scope=scope, removed=removed)
    return jsonify({"removed": removed})


@app.route("/api/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        saved = settings_store.save(request.json or {})
        audit.log("settings_changed", keys=list((request.json or {}).keys()))
        return jsonify(saved)
    return jsonify(settings_store.load())


@app.route("/api/vps", methods=["GET", "POST"])
@login_required
def vps():
    if request.method == "POST":
        data = request.json or {}
        item = registry.add_vps(
            data["name"], data["host"], data.get("user", "root"), data["private_key"]
        )
        audit.log("vps_added", vps=item["id"], host=item["host"])
        return jsonify(item)
    return jsonify(registry.list_vps())


@app.route("/api/vps/<vps_id>", methods=["DELETE"])
@login_required
def vps_delete(vps_id):
    registry.remove_vps(vps_id)
    audit.log("vps_removed", vps=vps_id)
    return jsonify({"removed": vps_id})


@app.route("/api/approvals")
@login_required
def approvals_list():
    timeout = settings_store.load()["approval_timeout"]
    return jsonify(approvals.list_all(timeout))


@app.route("/api/approvals/<approval_id>", methods=["POST"])
@login_required
def approvals_decide(approval_id):
    approve = bool((request.json or {}).get("approve"))
    item = approvals.decide(approval_id, approve)
    if not item:
        return jsonify({"error": "approval nahi mili ya already decide ho chuki"}), 404
    if approve and item["action"] == "run_command":
        detail = item["detail"]
        result = ssh.run(detail["vps"], detail["command"])
        audit.log("command_ran", vps=detail["vps"], command=detail["command"], exit_code=result["exit_code"])
        return jsonify({"status": item["status"], "result": result})
    if approve and item["action"] == "browser_actions":
        detail = item["detail"]
        try:
            res = browser.run_actions(detail["url"], detail["actions"])
        except Exception as exc:
            audit.log("browser_action_failed", approval_id=approval_id, error=str(exc))
            return jsonify({"status": item["status"], "error": str(exc)}), 400
        body = "\n".join(res["steps"]) + f"\n\n{res['title']}\n{res['text']}"
        return jsonify({"status": item["status"], "result": {"stdout": body, "stderr": "", "exit_code": 0}})
    audit.log("approval_decided", approval_id=approval_id, approved=approve)
    return jsonify({"status": item["status"]})


@app.route("/api/audit")
@login_required
def audit_view():
    return jsonify(audit.tail(100))


@app.route("/api/voice/generate", methods=["POST"])
@login_required
def voice_generate():
    from agent import voice
    try:
        name = voice.generate((request.json or {}).get("text", ""))
    except (ValueError, RuntimeError) as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"file": name, "url": f"/api/audio/{name}"})


@app.route("/api/audio/<name>")
@login_required
def audio_file(name):
    from flask import send_from_directory
    from agent import voice
    if "/" in name or ".." in name:
        return jsonify({"error": "galat naam"}), 400
    download = request.args.get("download") == "1"
    return send_from_directory(voice.AUDIO_DIR, name, as_attachment=download)


@app.route("/api/voice/clone", methods=["POST"])
@login_required
def voice_clone():
    from agent import voice
    name = request.form.get("name", "").strip()
    consent = request.form.get("consent") == "yes"
    samples = []
    for f in request.files.getlist("samples"):
        samples.append((f.filename or "sample.mp3", f.read(), f.mimetype or "audio/mpeg"))
    try:
        voice_id = voice.clone(name, samples, consent)
    except (ValueError, PermissionError, RuntimeError) as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify({"voice_id": voice_id})


@app.route("/api/screenshots/<name>")
@login_required
def screenshot(name):
    from flask import send_from_directory
    if "/" in name or ".." in name:
        return jsonify({"error": "galat naam"}), 400
    return send_from_directory(browser.SHOTS_DIR, name)


@app.route("/api/tasks", methods=["GET", "POST"])
@login_required
def tasks():
    if request.method == "POST":
        data = request.json or {}
        try:
            item = scheduler.add_task(
                data.get("name", "task"), data["command"], data.get("interval_minutes", 60)
            )
        except (ValueError, KeyError) as exc:
            return jsonify({"error": str(exc)}), 400
        return jsonify(item)
    return jsonify(scheduler.list_tasks())


@app.route("/api/tasks/<task_id>", methods=["DELETE"])
@login_required
def tasks_delete(task_id):
    scheduler.remove_task(task_id)
    return jsonify({"removed": task_id})


@app.route("/api/voices")
@login_required
def voices():
    return jsonify(elevenlabs.list_voices())


@app.route("/api/voice/stt", methods=["POST"])
@login_required
def voice_stt():
    audio = request.files.get("audio")
    if not audio:
        return jsonify({"error": "audio file chahiye"}), 400
    text = elevenlabs.stt(audio.read(), audio.filename or "voice.webm", audio.mimetype)
    return jsonify({"text": text})


@app.route("/api/voice/tts", methods=["POST"])
@login_required
def voice_tts():
    settings = settings_store.load()
    text = (request.json or {}).get("text", "")
    if not settings["elevenlabs_voice_id"]:
        return jsonify({"error": "Settings mein voice select karein"}), 400
    audio = elevenlabs.tts(text, settings["elevenlabs_voice_id"], settings["elevenlabs_model"])
    return app.response_class(audio, mimetype="audio/mpeg")


@app.route("/api/media", methods=["POST"])
@login_required
def media():
    file = request.files.get("file")
    prompt = request.form.get("prompt", "Is file ko samjhao.")
    if not file:
        return jsonify({"error": "file chahiye"}), 400
    data = file.read()
    if len(data) > 20 * 1024 * 1024:
        return jsonify({"error": "file 20MB se choti honi chahiye"}), 400
    model = settings_store.load()["gemini_model"]
    answer = gemini.analyze(data, file.mimetype, prompt, model)
    store.add("user", f"[file: {file.filename}] {prompt}")
    store.add("assistant", answer)
    return jsonify({"reply": answer})


scheduler.start()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=False)
