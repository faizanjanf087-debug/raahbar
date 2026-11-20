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
- **Browser (read-only):** `/browse <url>` page ka text nikalta hai (Playwright, headless). Click, type, aur login wo khud nahi karta.
- **Scheduled tasks:** `/schedule add <minutes> <command>`, `/schedule list`, `/schedule remove <id>`. Ya Scheduled tasks tab se. Sirf read-only kaam schedule hote hain.
- **Hands-free live call:** Live Call mein "Hands-free" on karein. Awaaz ruk jaye to message khud bheja jaata hai (simple VAD).
- **PWA:** browser mein "Add to Home Screen" karke app ki tarah khul sakta hai (manifest aur service worker).

## Playwright setup (browse ke liye)

```
pip install playwright
playwright install chromium
```

## Sahi istemaal ke liye

- Credentials kabhi chat mein na likhein. Passwords ke liye popup mein khud daalein.
- VPS par alag user banaein jiske paas sirf zaroori permissions hon.
- Replit free plan par app sleep ho sakti hai, is liye lamba kaam VPS par chalana behtar hai.
- Repo ko private rakhein, aur data/ aur .env kabhi commit na karein.

## Abhi kya adhoora hai

- Live call full-duplex nahi hai. Hands-free simple VAD hai, real-time streaming nahi.
- Browser se click, type ya login abhi nahi hota. Ye approval flow ke saath agle version mein aayega.
- Gemini "live" mode ka real-time streaming abhi shamil nahi.
- Video ko frames mein tod kar analyze karna abhi nahi hai. Chhoti video seedha Gemini ko jaati hai (20MB tak).
- Ye code sirf lokal test hua hai, aur is session mein packages install nahi ho sake, is liye pehli baar chalane par error aa sakta hai.
