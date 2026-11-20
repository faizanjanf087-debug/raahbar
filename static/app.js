// ---------- helpers ----------
const $ = (sel) => document.querySelector(sel);

async function api(path, options = {}) {
  const res = await fetch(path, {
    headers: options.body && !(options.body instanceof FormData)
      ? { "Content-Type": "application/json" }
      : {},
    ...options,
    body: options.body && !(options.body instanceof FormData)
      ? JSON.stringify(options.body)
      : options.body,
  });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error(data.error || `HTTP ${res.status}`);
  }
  return res;
}

const getJSON = (path) => api(path).then((r) => r.json());
const postJSON = (path, body) => api(path, { method: "POST", body }).then((r) => r.json());

function addMessage(role, text) {
  const log = $("#chat-log");
  const div = document.createElement("div");
  div.className = `msg ${role}`;
  div.textContent = text;
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
}

// ---------- tabs ----------
document.querySelectorAll(".sidebar nav button").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".sidebar nav button").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
    btn.classList.add("active");
    $(`#tab-${btn.dataset.tab}`).classList.add("active");
    loadTab(btn.dataset.tab);
  });
});

function loadTab(name) {
  if (name === "vps") loadVps();
  if (name === "approvals") loadApprovals();
  if (name === "history") loadHistory();
  if (name === "settings") loadSettings();
  if (name === "tasks") loadTasks();
  if (name === "audit") loadAudit();
}

// ---------- chat ----------
async function sendChat(text) {
  if (!text.trim()) return;
  addMessage("user", text);
  $("#chat-text").value = "";
  try {
    const data = await postJSON("/api/chat", { message: text });
    addMessage("assistant", data.reply);
    return data.reply;
  } catch (e) {
    addMessage("assistant", `Error: ${e.message}`);
  }
}

$("#send-btn").addEventListener("click", () => sendChat($("#chat-text").value));
$("#chat-text").addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendChat($("#chat-text").value);
  }
});

// Mention: pichli baat chat mein quote karein
$("#mention-btn").addEventListener("click", async () => {
  const list = $("#mention-list");
  if (!list.classList.contains("hidden")) {
    list.classList.add("hidden");
    return;
  }
  const items = await getJSON("/api/history?limit=20");
  list.innerHTML = "";
  items.slice().reverse().forEach((item) => {
    const div = document.createElement("div");
    div.className = "mention-item";
    div.textContent = `${item.role}: ${item.content.slice(0, 120)}`;
    div.addEventListener("click", () => {
      $("#chat-text").value += `\n> ${item.content}\n`;
      list.classList.add("hidden");
      $("#chat-text").focus();
    });
    list.appendChild(div);
  });
  list.classList.remove("hidden");
});

// File upload: image, audio, video
$("#attach-btn").addEventListener("click", () => $("#file-input").click());
$("#file-input").addEventListener("change", async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const prompt = $("#chat-text").value.trim() || "Is file ko samjhao.";
  addMessage("user", `[file: ${file.name}] ${prompt}`);
  const form = new FormData();
  form.append("file", file);
  form.append("prompt", prompt);
  try {
    const data = await api("/api/media", { method: "POST", body: form }).then((r) => r.json());
    addMessage("assistant", data.reply);
  } catch (err) {
    addMessage("assistant", `Error: ${err.message}`);
  }
  $("#chat-text").value = "";
  e.target.value = "";
});

// ---------- voice helpers ----------
async function speak(text) {
  const settings = await getJSON("/api/settings");
  if (!settings.live_auto_speak) return;
  const res = await api("/api/voice/tts", { method: "POST", body: { text } });
  const blob = await res.blob();
  const audio = new Audio(URL.createObjectURL(blob));
  await audio.play();
}

async function transcribe(blob) {
  const form = new FormData();
  form.append("audio", blob, "voice.webm");
  const data = await api("/api/voice/stt", { method: "POST", body: form }).then((r) => r.json());
  return data.text;
}

// ---------- live call ----------
let stream = null;
let recorder = null;
let chunks = [];
let muted = false;
let cameraOn = false;

const liveStatus = (t) => ($("#live-status").textContent = t);

$("#live-start").addEventListener("click", async () => {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    liveStatus("Call chal rahi hai. Hold to talk dabaayein.");
    ["#live-mute", "#live-camera", "#live-end", "#live-ptt", "#live-snapshot"].forEach(
      (id) => ($(id).disabled = false)
    );
    $("#live-start").disabled = true;
  } catch (e) {
    liveStatus(`Mic nahi mila: ${e.message}`);
  }
});

$("#live-mute").addEventListener("click", () => {
  muted = !muted;
  stream.getAudioTracks().forEach((t) => (t.enabled = !muted));
  $("#live-mute").textContent = muted ? "Unmute" : "Mute";
});

$("#live-camera").addEventListener("click", async () => {
  const video = $("#camera");
  if (!cameraOn) {
    const cam = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = cam;
    video.classList.remove("hidden");
    cameraOn = true;
    $("#live-camera").textContent = "Camera off";
  } else {
    video.srcObject.getTracks().forEach((t) => t.stop());
    video.srcObject = null;
    video.classList.add("hidden");
    cameraOn = false;
    $("#live-camera").textContent = "Camera on";
  }
});

$("#live-snapshot").addEventListener("click", async () => {
  const video = $("#camera");
  if (!cameraOn) return liveStatus("Pehle camera on karein.");
  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext("2d").drawImage(video, 0, 0);
  const blob = await new Promise((r) => canvas.toBlob(r, "image/jpeg", 0.9));
  const form = new FormData();
  form.append("file", blob, "snapshot.jpg");
  form.append("prompt", "Is tasveer mein kya hai? Roman Urdu mein batao.");
  const data = await api("/api/media", { method: "POST", body: form }).then((r) => r.json());
  $("#live-transcript").insertAdjacentHTML("beforeend", `<div class="msg assistant">${data.reply}</div>`);
  await speak(data.reply);
});

const ptt = $("#live-ptt");
async function startTalk(e) {
  if (e) e.preventDefault();
  if (!stream || muted || (recorder && recorder.state === "recording")) return;
  chunks = [];
  recorder = new MediaRecorder(stream);
  recorder.ondataavailable = (ev) => chunks.push(ev.data);
  recorder.start();
  ptt.classList.add("active");
  liveStatus("Sun raha hoon...");
}

async function stopTalk() {
  if (!recorder || recorder.state !== "recording") return;
  ptt.classList.remove("active");
  liveStatus("Samajh raha hoon...");
  await new Promise((resolve) => {
    recorder.onstop = resolve;
    recorder.stop();
  });
  const blob = new Blob(chunks, { type: "audio/webm" });
  try {
    const said = await transcribe(blob);
    $("#live-transcript").insertAdjacentHTML("beforeend", `<div class="msg user">${said}</div>`);
    const reply = await sendChat(said);
    if (reply) await speak(reply);
  } catch (err) {
    liveStatus(`Error: ${err.message}`);
    return;
  }
  liveStatus("Call chal rahi hai. Hold to talk dabaayein.");
}

ptt.addEventListener("mousedown", startTalk);
ptt.addEventListener("touchstart", startTalk, { passive: false });
ptt.addEventListener("mouseup", stopTalk);
ptt.addEventListener("mouseleave", stopTalk);
ptt.addEventListener("touchend", stopTalk);

// Hands-free: awaaz ki level dekh kar khud bolna shuru/band hota hai (simple VAD)
let vadTimer = null;
let vadCtx = null;
function startHandsFree() {
  vadCtx = new (window.AudioContext || window.webkitAudioContext)();
  const source = vadCtx.createMediaStreamSource(stream);
  const analyser = vadCtx.createAnalyser();
  analyser.fftSize = 512;
  source.connect(analyser);
  const data = new Uint8Array(analyser.fftSize);
  const SPEECH_LEVEL = 0.04;   // is se upar awaaz = bol rahe hain
  const SILENCE_MS = 1200;     // itni khamoshi ke baad message bheja jaye
  let silentSince = null;

  vadTimer = setInterval(() => {
    if (muted) return;
    analyser.getByteTimeDomainData(data);
    let sum = 0;
    for (const v of data) {
      const n = (v - 128) / 128;
      sum += n * n;
    }
    const rms = Math.sqrt(sum / data.length);
    if (rms > SPEECH_LEVEL) {
      silentSince = null;
      startTalk();
    } else if (recorder && recorder.state === "recording") {
      if (silentSince === null) silentSince = Date.now();
      if (Date.now() - silentSince > SILENCE_MS) {
        silentSince = null;
        stopTalk();
      }
    }
  }, 100);
}

function stopHandsFree() {
  if (vadTimer) clearInterval(vadTimer);
  vadTimer = null;
  if (vadCtx) vadCtx.close();
  vadCtx = null;
}

$("#live-start").addEventListener("click", () => {
  if ($("#live-handsfree").checked && stream) startHandsFree();
});

$("#live-end").addEventListener("click", () => {
  stopHandsFree();
  if (stream) stream.getTracks().forEach((t) => t.stop());
  if (cameraOn) $("#camera").srcObject = null;
  stream = null;
  cameraOn = false;
  muted = false;
  ["#live-mute", "#live-camera", "#live-end", "#live-ptt", "#live-snapshot"].forEach(
    (id) => ($(id).disabled = true)
  );
  $("#live-start").disabled = false;
  $("#camera").classList.add("hidden");
  liveStatus("Call khatam.");
});

// ---------- VPS ----------
async function loadVps() {
  const items = await getJSON("/api/vps");
  const box = $("#vps-list");
  box.innerHTML = "";
  if (!items.length) box.innerHTML = '<p class="hint">Abhi koi VPS add nahi hua.</p>';
  items.forEach((v) => {
    const div = document.createElement("div");
    div.className = "card";
    div.innerHTML = `<strong>${v.name}</strong> (${v.host}) id: ${v.id}
      <div class="actions"><button class="danger">Remove</button></div>`;
    div.querySelector("button").addEventListener("click", async () => {
      if (!confirm(`${v.name} remove karein?`)) return;
      await api(`/api/vps/${v.id}`, { method: "DELETE" });
      loadVps();
    });
    box.appendChild(div);
  });
}

$("#vps-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const body = Object.fromEntries(new FormData(e.target).entries());
  await postJSON("/api/vps", body);
  e.target.reset();
  loadVps();
});

// ---------- approvals ----------
async function loadApprovals() {
  const items = await getJSON("/api/approvals");
  const pending = items.filter((i) => i.status === "pending");
  $("#pending-count").textContent = pending.length ? `(${pending.length})` : "";
  const box = $("#approvals-list");
  box.innerHTML = "";
  if (!items.length) box.innerHTML = '<p class="hint">Koi approval nahi.</p>';
  items.forEach((item) => {
    const div = document.createElement("div");
    div.className = "card";
    const detail = JSON.stringify(item.detail);
    div.innerHTML = `<strong>${item.action}</strong> [${item.status}] id: ${item.id}
      <pre>${detail}</pre>`;
    if (item.status === "pending") {
      const actions = document.createElement("div");
      actions.className = "actions";
      const yes = document.createElement("button");
      yes.textContent = "Approve";
      const no = document.createElement("button");
      no.textContent = "Deny";
      no.className = "danger";
      yes.addEventListener("click", () => decide(item.id, true));
      no.addEventListener("click", () => decide(item.id, false));
      actions.append(yes, no);
      div.appendChild(actions);
    }
    box.appendChild(div);
  });
}

async function decide(id, approve) {
  try {
    const data = await postJSON(`/api/approvals/${id}`, { approve });
    if (data.result) {
      addMessage("assistant", `Command ka natija (exit ${data.result.exit_code}):\n${data.result.stdout || data.result.stderr}`);
    }
  } catch (e) {
    alert(e.message);
  }
  loadApprovals();
}

// ---------- history ----------
async function loadHistory() {
  const items = await getJSON("/api/history?limit=200");
  const box = $("#history-list");
  box.innerHTML = "";
  items.slice().reverse().forEach((item) => {
    const div = document.createElement("div");
    div.className = "card";
    div.textContent = `${item.role}: ${item.content}`;
    box.appendChild(div);
  });
}

document.querySelectorAll(".del-btn").forEach((btn) => {
  btn.addEventListener("click", async () => {
    if (!confirm(`History delete karein (${btn.dataset.scope})?`)) return;
    await postJSON("/api/history/delete", { scope: btn.dataset.scope });
    loadHistory();
  });
});

// ---------- settings ----------
async function loadSettings() {
  const settings = await getJSON("/api/settings");
  const form = $("#settings-form");
  for (const [key, value] of Object.entries(settings)) {
    const el = form.elements[key];
    if (!el) continue;
    if (el.type === "checkbox") el.checked = !!value;
    else el.value = value;
  }
  const voices = await getJSON("/api/voices").catch(() => []);
  const select = $("#voice-select");
  select.innerHTML = '<option value="">-- voice chunein --</option>';
  voices.forEach((v) => {
    const opt = document.createElement("option");
    opt.value = v.id;
    opt.textContent = v.name;
    if (v.id === settings.elevenlabs_voice_id) opt.selected = true;
    select.appendChild(opt);
  });
}

$("#settings-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.target;
  const body = {
    profile_name: form.profile_name.value,
    deepseek_model: form.deepseek_model.value,
    gemini_model: form.gemini_model.value,
    elevenlabs_model: form.elevenlabs_model.value,
    elevenlabs_voice_id: form.elevenlabs_voice_id.value,
    approval_timeout: Number(form.approval_timeout.value),
    live_auto_speak: form.live_auto_speak.checked,
  };
  await postJSON("/api/settings", body);
  $("#settings-msg").textContent = "Save ho gaya.";
});

// ---------- scheduled tasks ----------
async function loadTasks() {
  const items = await getJSON("/api/tasks");
  const box = $("#tasks-list");
  box.innerHTML = "";
  if (!items.length) box.innerHTML = '<p class="hint">Abhi koi task nahi.</p>';
  items.forEach((t) => {
    const div = document.createElement("div");
    div.className = "card";
    div.innerHTML = `<strong>${t.name}</strong> — har ${t.interval_minutes} min<br>
      <code>${t.command}</code>
      <pre>${t.last_result ? t.last_result : "abhi tak nahi chala"}</pre>
      <div class="actions"><button class="danger">Remove</button></div>`;
    div.querySelector("button").addEventListener("click", async () => {
      if (!confirm(`${t.name} remove karein?`)) return;
      await api(`/api/tasks/${t.id}`, { method: "DELETE" });
      loadTasks();
    });
    box.appendChild(div);
  });
}

$("#task-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const form = e.target;
  try {
    await postJSON("/api/tasks", {
      name: form.name.value,
      command: form.command.value,
      interval_minutes: Number(form.interval_minutes.value),
    });
    form.reset();
    form.interval_minutes.value = 60;
  } catch (err) {
    alert(err.message);
  }
  loadTasks();
});

// ---------- audit ----------
async function loadAudit() {
  const items = await getJSON("/api/audit");
  $("#audit-log").textContent = items.map((i) => JSON.stringify(i)).join("\n");
}

// ---------- start ----------
setInterval(() => {
  if ($("#tab-approvals").classList.contains("active")) loadApprovals();
  else getJSON("/api/approvals").then((items) => {
    const pending = items.filter((i) => i.status === "pending").length;
    $("#pending-count").textContent = pending ? `(${pending})` : "";
  }).catch(() => {});
}, 4000);

getJSON("/api/history?limit=50").then((items) => {
  items.forEach((item) => addMessage(item.role, item.content));
}).catch(() => {});

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/static/sw.js").catch(() => {});
}
