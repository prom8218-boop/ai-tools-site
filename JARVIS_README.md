# 🤖 J.A.R.V.I.S. — Iron Man AI Assistant

A voice-controlled, Iron-Man-style AI assistant built into the AI Tools Suite.
Inspired by Tony Stark's **J.A.R.V.I.S.** (*Just A Rather Very Intelligent System*).

![status](https://img.shields.io/badge/status-online-cyan) ![voice](https://img.shields.io/badge/voice-enabled-cyan)

---

## ✨ Features

| Capability | Example Command |
|---|---|
| 🎙️ **Voice input** | Click the mic and speak naturally |
| 🔊 **Voice replies** | JARVIS speaks answers back to you (toggleable) |
| 🕒 **Time & date** | *"what time is it"* / *"what is today's date"* |
| 🌦️ **Weather** | *"weather in Dhaka"* / *"weather in Tokyo"* |
| 🧮 **Math** | *"calculate 256 times 18"* / *"what is 15 plus 27"* |
| 📚 **Wikipedia** | *"who is Albert Einstein"* / *"what is python"* |
| 🌐 **Open sites** | *"open youtube"* / *"open github"* / *"open gmail"* |
| 🔎 **Web search** | *"search for best ai tools"* |
| ₿ **Crypto prices** | *"price of bitcoin"* / *"what is ethereum worth"* |
| 🪙 **Coin / dice** | *"flip a coin"* / *"roll a dice"* / *"roll a d20"* |
| 😂 **Jokes & facts** | *"tell me a joke"* / *"tell me a fun fact"* |
| 📝 **Notes** | *"remember that the meeting is at 5pm"* / *"what are my notes"* |
| 💬 **Open chat** | Anything else → answered by Gemini AI |
| 📊 **System status** | *"system status"* / *"what can you do"* |

---

## 🚀 Run It

```bash
# 1. Install deps
pip install -r requirements.txt

# 2. Set your Gemini key (enables open-ended conversation)
export GEMINI_API_KEY="your_key_here"
# Optional: change how JARVIS addresses you
export JARVIS_OWNER="Tony"

# 3. Start the server
python app.py

# 4. Open the assistant
#    http://localhost:5000/jarvis
```

You can also reach it from the main suite's header **"🤖 JARVIS"** button.

---

## 🗣️ Voice Notes

- Voice uses the browser's built-in **Web Speech API**.
- Works best in **Chrome / Edge**. (Firefox has limited speech support.)
- On first use, **allow microphone access** when prompted.
- Press the **mic button** (or hit **Spacebar** when not typing) to talk.
- Toggle **"Voice replies"** off if you only want text.

---

## 🏗️ How It Works

```
templates/jarvis.html   →  Iron Man HUD UI (arc reactor, rings, waveform, mic)
        │  POST { command }  ▼
        └─►  app.py  /api/jarvis
                  │
                  ▼
            jarvis.py  →  JarvisBrain
                  │  1. try local Skills (fast, no API key)
                  │  2. fall back to Gemini for open conversation
                  ▼
            { text, action?, data? }
```

### Adding a new skill

Open `jarvis.py`, add a `Skill(...)` entry inside `JarvisBrain._build_skills()`
and a matching handler method. Each skill = a list of regex triggers + a function
that returns a response dict.

```python
Skill("name", [r"trigger pattern"], self._handler, "desc", priority=5),

def _handler(self, text, match):
    return self._resp("Response text, sir.", action="open_url", data={"url": "..."})
```

**Priority** controls order (higher runs first). Local skills are instant and
don't need any API key — only the open-conversation fallback needs Gemini.

---

## 🛠️ Tech

- **Backend:** Python + Flask, modular skill engine (`jarvis.py`)
- **Intelligence:** Google Gemini (open chat) + local offline skills
- **External data:** Open-Meteo (weather), CoinGecko (crypto), Wikipedia (facts)
- **Frontend:** Vanilla JS, Tailwind, Web Speech API, Canvas visualizer

> 🔒 Weather, crypto and Wikipedia use free public APIs — no extra keys needed.
> The sandbox here blocks outbound HTTPS, so those calls succeed on your real server.
