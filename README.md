# Raahbar (V4)

Flask ka personal AI assistant. Chat, live call, VPS status aur approvals.

## Setup

1. `pip install -r requirements.txt`
2. `.env.example` ko `.env` mein copy karein, aur values daalein.
3. VAULT_KEY banayein:
   `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
4. `python app.py`, phir `http://localhost:8080` kholein.

Replit par: Secrets mein same keys daalein, aur Run dabaayein.

## Features

- **Chat:** DeepSeek se jawab. `@` se pichli baat mention karein. `+` se image, audio ya video upload karein.
- **Live call:** Hold to talk (ElevenLabs STT, DeepSeek, ElevenLabs TTS). Mute, camera, aur snapshot ka option.
- **VPS:** add/remove. Key encrypted save hoti hai. `/status <id>` read-only hai.
- **Commands:** `/run <vps_id> <command>` pehle approval maangti hai. Blocked commands kabhi nahi chalte.
- **Approvals:** har write action ke liye popup. Timeout settings mein.
- **History:** pichla 1 ghanta, 1 din, ya sab delete.
- **Settings:** DeepSeek, Gemini, ElevenLabs models aur voice.
- **Audit log:** har important action ka record.

## Sahi istemaal ke liye

- Credentials kabhi chat mein na likhein. Passwords ke liye popup mein khud daalein.
- VPS par alag user banaein jiske paas sirf zaroori permissions hon.
- Replit free plan par app sleep ho sakti hai, is liye lamba kaam VPS par chalana behtar hai.

## Abhi kya adhoora hai (V4 ke baad)

- Live call full-duplex nahi hai. Abhi push-to-talk hai.
- Browser automation (Playwright) V3 mein aayega.
- Video frames ka deep analysis, scheduled tasks, aur mobile PWA agle versions mein.
- Gemini ke "live" mode ka real-time streaming abhi shamil nahi.
