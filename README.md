# Raahbar (V4)

Flask ka personal AI assistant. Chat, live call, VPS status aur approvals.

## Setup

1. `pip install -r requirements.txt`
2. `.env.example` ko `.env` mein copy karein, aur values daalein.
3. VAULT_KEY banayein:
   `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
4. `python app.py`, phir `http://localhost:8080` kholein.

Replit par: Secrets mein same keys daalein, aur Run dabaayein.

## Database (Neon Postgres)

1. neon.tech par free project banayein, aur connection string copy karein (postgresql://...).
2. Replit Secrets (ya .env) mein `DATABASE_URL` ke naam se daalein.
3. App chalayein. Table apne aap ban jati hai (`messages`).

Agar `DATABASE_URL` khali ho, to local SQLite (`data/memory.db`) use hogi.

## UI

- Sidebar ☰ button se chhupaaya aur dikhaya ja sakta hai.
- Jawab Markdown mein dikhte hain (headings, lists, code, tables).
- Jawab aane se pehle typing dots dikhte hain.
- Animations ko system ki "reduced motion" setting ke hisab se band kiya ja sakta hai.

## Features

- **Chat:** DeepSeek se jawab. `@` se pichli baat mention karein. `+` se image, audio ya video upload karein.
- **Live call:** Hold to talk (ElevenLabs STT, DeepSeek, ElevenLabs TTS). Mute, camera, aur snapshot ka option.
- **VPS:** add/remove. Key encrypted save hoti hai. `/status <id>` read-only hai.
- **Commands:** `/run <vps_id> <command>` pehle approval maangti hai. Blocked commands kabhi nahi chalte.
- **Approvals:** har write action ke liye popup. Timeout settings mein.
- **History:** pichla 1 ghanta, 1 din, ya sab delete.
- **Settings:** Chat model (Auto ya khud chunein), Gemini image model, ElevenLabs voice model aur voice.
- **Auto model:** Chat model "Auto" ho to DeepSeek har message ko `general`, `code`, ya `reasoning` mein parakh kar model chunta hai (`agent/router.py`).
- **Voice:** `/voice <text>` MP3 banata hai, jo chat mein link ke taur par sun aur download ho sakta hai.
- **Voice clone:** Settings mein "Voice clone" form. Consent checkbox zaroori hai, aur sirf apni awaaz ya likhit ijazat wali awaaz ke liye.
- **Audit log:** har important action ka record.
- **Browser:** `/browse <url>` page ka text nikalta hai (read-only). `/browse <url> --shot` screenshot bhi leta hai, jo `/api/screenshots/<name>` par milta hai. `/act <url> | click | <selector>` ya `/act <url> | type | <selector> | <text>` se action hota hai. Kai steps ke liye `;;` se alag karein. Ek approval poore batch par lagti hai. Password fields par agent kaam nahi karta, login aap khud karein.
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
- Replit par data (SQLite file) persist nahi hota. Data VPS par rakhna hai, to database ko VPS se connect karne ka kaam baaki hai (abhi SQLite local file hai).

## Abhi kya adhoora hai

- Live call full-duplex nahi hai. Hands-free simple VAD hai, real-time streaming nahi.
- Browser actions ke liye screenshot approval card abhi nahi hai. Abhi approval ke baad result text mein aata hai.
- Browser profile (cookies) data/browser_profile mein rehti hai. Ise Replit par persist karne ke liye Replit storage ka dhyan rakhein.
- Gemini "live" mode ka real-time streaming abhi shamil nahi.
- Video ko frames mein tod kar analyze karna abhi nahi hai. Chhoti video seedha Gemini ko jaati hai (20MB tak).
- Ye code sirf lokal test hua hai, aur is session mein packages install nahi ho sake, is liye pehli baar chalane par error aa sakta hai.
