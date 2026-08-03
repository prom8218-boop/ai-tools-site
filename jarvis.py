"""
JARVIS AI Assistant - Core Brain Module
========================================
An Iron-Man style AI assistant engine. Parses spoken/typed commands,
dispatches them to "skills" (local fast handlers) and falls back to
Gemini for open-ended conversation.

Designed to be modular: add a new skill by registering it in the
`Skill` list inside JarvisBrain.__init__.
"""

import os
import re
import json
import math
import time
import random
import datetime
import calendar
import requests

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

WMO_WEATHER = {
    0: "clear sky", 1: "mainly clear", 2: "partly cloudy", 3: "overcast",
    45: "foggy", 48: "depositing rime fog", 51: "light drizzle",
    53: "moderate drizzle", 55: "dense drizzle", 56: "light freezing drizzle",
    57: "dense freezing drizzle", 61: "light rain", 63: "moderate rain",
    65: "heavy rain", 66: "light freezing rain", 67: "heavy freezing rain",
    71: "light snowfall", 73: "moderate snowfall", 75: "heavy snowfall",
    77: "snow grains", 80: "light rain showers", 81: "moderate rain showers",
    82: "violent rain showers", 85: "light snow showers",
    86: "heavy snow showers", 95: "thunderstorm", 96: "thunderstorm with hail",
    99: "severe thunderstorm with hail",
}

JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs, sir.",
    "I would tell you a UDP joke, but you might not get it.",
    "Why did the developer go broke? Because he used up all his cache.",
    "There are only 10 types of people in the world: those who understand binary and those who don't.",
    "Why was the JavaScript developer sad? Because he didn't 'null' how to express his feelings.",
    "A SQL query walks into a bar, approaches two tables and asks: 'May I join you?'",
    "Why do Java developers wear glasses? Because they don't C#.",
    "I told my computer I needed a break, and now it won't stop sending me KitKat ads.",
    "Debugging: being the detective in a crime movie where you are also the murderer.",
    "How many programmers does it take to change a light bulb? None — that's a hardware problem.",
]

FACTS = [
    "The first computer bug was an actual moth found in a relay in 1947, sir.",
    "The average human heart beats around 100,000 times a day.",
    "A bolt of lightning contains enough energy to toast about 100,000 slices of bread.",
    "Octopuses have three hearts and blue blood.",
    "The speed of light is approximately 299,792 kilometers per second.",
    "Honey never spoils — archaeologists have found edible honey in ancient Egyptian tombs.",
    "There are more possible games of chess than atoms in the observable universe.",
]

COMPLIMENTS = [
    "Always a pleasure, sir.", "At your service.", "Glad I could help.",
    "Anytime, sir.", "Consider it done.",
]

WEBSITES = {
    "google": "https://www.google.com",
    "youtube": "https://www.youtube.com",
    "github": "https://github.com",
    "gmail": "https://mail.google.com",
    "facebook": "https://www.facebook.com",
    "twitter": "https://twitter.com",
    "x": "https://twitter.com",
    "instagram": "https://www.instagram.com",
    "whatsapp": "https://web.whatsapp.com",
    "wikipedia": "https://www.wikipedia.org",
    "stackoverflow": "https://stackoverflow.com",
    "amazon": "https://www.amazon.com",
    "netflix": "https://www.netflix.com",
    "spotify": "https://open.spotify.com",
    "chatgpt": "https://chat.openai.com",
    "linkedin": "https://www.linkedin.com",
    "reddit": "https://www.reddit.com",
    "maps": "https://maps.google.com",
    "translate": "https://translate.google.com",
    "weather": "https://wttr.in",
}

CRYPTO_IDS = {
    "bitcoin": "bitcoin", "btc": "bitcoin", "ethereum": "ethereum", "eth": "ethereum",
    "solana": "solana", "sol": "solana", "dogecoin": "dogecoin", "doge": "dogecoin",
    "ripple": "ripple", "xrp": "ripple", "cardano": "cardano", "ada": "cardano",
    "binance": "binancecoin", "bnb": "binancecoin", "tron": "tron", "trx": "tron",
}


def safe_eval(expression):
    """Safely evaluate a basic math expression using a restricted grammar."""
    # Allow digits, operators, parentheses, decimal points, math functions
    allowed = set("0123456789+-*/().,%^ \t")
    if not expression or any(ch not in allowed for ch in expression):
        return None
    # Replace human-friendly operators
    expr = expression.replace("^", "**").replace("%", "/100")
    # Remove trailing operator
    expr = expr.rstrip("+-*/")
    try:
        result = eval(expr, {"__builtins__": {}}, {"math": math})
        return result
    except Exception:
        return None


def call_gemini(prompt, system_instruction=None, api_key=None):
    """Call the Gemini API and return the text response."""
    key = api_key or GEMINI_API_KEY
    if not key:
        return None, "Gemini API key is not configured on the server."
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={key}"
    )
    headers = {"Content-Type": "application/json"}
    contents = [{"parts": [{"text": prompt}]}]
    body = {"contents": contents}
    if system_instruction:
        body["systemInstruction"] = {"parts": [{"text": system_instruction}]}
    try:
        resp = requests.post(url, json=body, headers=headers, timeout=30)
        data = resp.json()
        if "candidates" not in data:
            msg = data.get("error", {}).get("message", "Unknown error")
            return None, f"Gemini error: {msg}"
        return data["candidates"][0]["content"]["parts"][0]["text"].strip(), None
    except requests.RequestException as exc:
        return None, f"Network error: {str(exc)}"
    except Exception as exc:
        return None, f"Error: {str(exc)}"


# ---------------------------------------------------------------------------
# Skill definition
# ---------------------------------------------------------------------------

class Skill:
    """A single JARVIS capability with trigger patterns and a handler."""

    def __init__(self, name, patterns, handler, description="", priority=0):
        self.name = name
        self.patterns = [re.compile(p, re.IGNORECASE) for p in patterns]
        self.handler = handler
        self.description = description
        self.priority = priority

    def match(self, text):
        for pat in self.patterns:
            m = pat.search(text)
            if m:
                return m
        return None


# ---------------------------------------------------------------------------
# The Brain
# ---------------------------------------------------------------------------

class JarvisBrain:
    """Central JARVIS brain. Owns skills, memory and conversation context."""

    GREETING_PROMPT = (
        "You are JARVIS, a sophisticated, witty and loyal AI assistant inspired by "
        "Iron Man's JARVIS. You address the user politely as 'sir' occasionally, "
        "keep answers concise and helpful, and have a calm British-butler tone. "
        "Never reveal your underlying model. If unsure, say so gracefully."
    )

    def __init__(self, api_key=None, owner=None):
        self.api_key = api_key or GEMINI_API_KEY
        self.owner = owner or os.environ.get("JARVIS_OWNER", "Sir")
        self.notes = []
        self.context = []  # recent turns for conversational memory
        self.max_context = 6
        self.skills = self._build_skills()

    # -- Skill registry ----------------------------------------------------

    def _build_skills(self):
        s = [
            Skill("greeting", [
                r"\b(hello|hi|hey|yo|good (morning|afternoon|evening)|greetings)\b",
            ], self._greeting, "Greet the user", priority=1),

            Skill("identity", [
                r"\b(who are you|what('?s| is) your name|are you jarvis|introduce yourself)\b",
            ], self._identity, "Introduce JARVIS", priority=5),

            Skill("time", [r"\b(time|what time is it)\b"], self._time,
                  "Tell the current time", priority=5),

            Skill("date", [
                r"\b(date|what day is it|today'?s date|what'?s the day|day of the week)\b",
            ], self._date, "Tell the current date", priority=5),

            Skill("weather", [
                r"\bweather\b.*\bin\b",
                r"\bweather\b",
                r"\btemperature\b.*\bin\b",
                r"\bhow (hot|cold)\b.*\bin\b",
            ], self._weather, "Weather report", priority=5),

            Skill("joke", [r"\b(joke|make me laugh|funny)\b"], self._joke,
                  "Tell a joke", priority=5),

            Skill("fact", [r"\b(fun fact|tell me a fact|random fact|something interesting)\b"],
                  self._fact, "Share a fact", priority=5),

            Skill("coinflip", [r"\b(flip|toss) (a )?coin\b"], self._coinflip,
                  "Flip a coin", priority=5),

            Skill("dice", [r"\b(roll|throw) (a )?(the )?dice\b", r"\broll (a )?d(\d+)\b"],
                  self._dice, "Roll dice", priority=5),

            Skill("math", [
                r"\b(calculate|compute|solve)\b.*\d",
                r"\b(what is|what'?s|how much is)\b.*\d",
                r"\d+\s*(times|plus|minus|divided by|over|multiplied by|x|\*|\+|/|-)\s*\d+",
                r"^[\d\s\+\-\*/\(\)\.\%\^]+$",
            ], self._math, "Do math", priority=4),

            Skill("crypto", [
                r"\b(price|value|rate)\b.*\b(bitcoin|btc|ethereum|eth|solana|sol|doge|dogecoin|xrp|ripple|cardano|ada|bnb|binance|tron|trx)\b",
                r"\b(bitcoin|btc|ethereum|eth|solana|sol|doge|dogecoin|xrp|ripple|cardano|ada|bnb|binance|tron|trx)\b.*\b(price|value|rate|worth)\b",
                r"\bhow much\b.*\b(bitcoin|btc|ethereum|eth|solana|sol)\b",
            ], self._crypto, "Crypto prices", priority=5),

            Skill("wikipedia", [
                r"\b(who is|who was|who are)\b",
                r"\b(what is|what are|what was)\b",
                r"\b(tell me about|search wikipedia for|wikipedia)\b",
            ], self._wikipedia, "Wikipedia lookup", priority=3),

            Skill("open", [
                r"\b(open|launch|go to|navigate to|take me to)\b\s+(\w+)",
            ], self._open_site, "Open a website", priority=4),

            Skill("search", [
                r"\b(search( the web| google)? for|google|look up|find online)\b",
            ], self._search, "Web search", priority=3),

            Skill("note", [
                r"\b(remember that|take a note|note that|remember this)\b",
                r"\b(add a note|save a note)\b",
            ], self._add_note, "Take a note", priority=5),

            Skill("notes_list", [r"\b(what are my notes|show (my )?notes|read my notes)\b"],
                  self._list_notes, "List notes", priority=5),

            Skill("status", [
                r"\b(system status|status report|how are you|how('?s| is) it going|report)\b",
            ], self._status, "System status report", priority=5),

            Skill("capabilities", [
                r"\b(what can you do|help|commands|what do you do|your (abilities|skills|features))\b",
            ], self._capabilities, "List capabilities", priority=5),

            Skill("thanks", [
                r"\b(thank you|thanks|thank u|thx|cheers|appreciate it)\b",
            ], self._thanks, "Acknowledge thanks", priority=5),

            Skill("bye", [
                r"\b(bye|goodbye|see you|see ya|good night|exit|quit|shut down|power off|go to sleep)\b",
            ], self._bye, "Say goodbye", priority=5),
        ]
        # Higher priority first
        s.sort(key=lambda sk: -sk.priority)
        return s

    # -- Public API --------------------------------------------------------

    def process(self, command):
        """Process a raw command string and return a response dict."""
        text = (command or "").strip()
        if not text:
            return self._resp("I didn't catch that, sir. Could you repeat?")

        self.context.append({"role": "user", "text": text})
        if len(self.context) > self.max_context:
            self.context = self.context[-self.max_context:]

        for skill in self.skills:
            m = skill.match(text)
            if m:
                try:
                    result = skill.handler(text, m)
                    if result is not None:
                        if isinstance(result, str):
                            result = self._resp(result)
                        self.context.append({"role": "jarvis", "text": result.get("text", "")})
                        return result
                except Exception as exc:  # defensive: a skill should never crash the brain
                    return self._resp(f"I ran into a problem with that, sir: {exc}")

        # Fallback: open-ended conversation via Gemini
        return self._converse(text)

    # -- Response helpers --------------------------------------------------

    @staticmethod
    def _resp(text, action=None, data=None, speak=True):
        body = {"text": text, "speak": speak}
        if action:
            body["action"] = action
        if data:
            body["data"] = data
        return body

    # -- Skill handlers ----------------------------------------------------

    def _greeting(self, text, m):
        hour = datetime.datetime.now().hour
        if 5 <= hour < 12:
            part = "Good morning"
        elif 12 <= hour < 17:
            part = "Good afternoon"
        elif 17 <= hour < 21:
            part = "Good evening"
        else:
            part = "Good evening"
        return self._resp(f"{part}, {self.owner}. JARVIS is online and at your service. How may I assist you?")

    def _identity(self, text, m):
        return self._resp(
            "I am JARVIS — Just A Rather Very Intelligent System. "
            "Your personal AI assistant, sir. I can tell the time, fetch the weather, "
            "search the web, look up facts, do calculations and much more."
        )

    def _time(self, text, m):
        now = datetime.datetime.now()
        pretty = now.strftime("%I:%M %p").lstrip("0")
        return self._resp(f"The current time is {pretty}, {self.owner}.")

    def _date(self, text, m):
        now = datetime.datetime.now()
        day_name = now.strftime("%A")
        pretty = now.strftime("%B %d, %Y")
        return self._resp(f"Today is {day_name}, {pretty}.")

    def _weather(self, text, m):
        loc = m.group(0)
        # Extract a location after "in"
        city_match = re.search(r"\bin\s+([a-zA-Z\s,]+)", text)
        city = (city_match.group(1).strip().rstrip(".?!,")
                if city_match else "London")
        city = re.sub(r"\b(today|right now|currently|please|the|weather)\b", "", city, flags=re.I).strip()
        if not city:
            city = "London"
        try:
            geo = requests.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": city, "count": 1, "language": "en", "format": "json"},
                timeout=10,
            ).json()
            if not geo.get("results"):
                return self._resp(f"I couldn't find a place called {city}, sir.")
            place = geo["results"][0]
            lat, lon = place["latitude"], place["longitude"]
            name = place.get("name", city)
            country = place.get("country", "")
            forecast = requests.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": lat, "longitude": lon,
                    "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m",
                    "temperature_unit": "celsius",
                },
                timeout=10,
            ).json()
            cur = forecast.get("current", {})
            temp = cur.get("temperature_2m")
            feels = cur.get("apparent_temperature")
            hum = cur.get("relative_humidity_2m")
            wind = cur.get("wind_speed_10m")
            code = cur.get("weather_code")
            desc = WMO_WEATHER.get(code, "clear")
            loc_name = f"{name}, {country}".strip(", ")
            msg = (f"The weather in {loc_name} is currently {desc} at "
                   f"{temp}°C, feeling like {feels}°C. "
                   f"Humidity is {hum}% with wind speeds of {wind} kilometers per hour, {self.owner}.")
            return self._resp(msg, data={"location": loc_name, "temp": temp})
        except requests.RequestException:
            return self._resp("I couldn't reach the weather service, sir. Please try again later.")
        except Exception as exc:
            return self._resp(f"Weather lookup failed: {exc}")

    def _joke(self, text, m):
        return self._resp(random.choice(JOKES))

    def _fact(self, text, m):
        return self._resp(f"Here's something, {self.owner}: {random.choice(FACTS)}")

    def _coinflip(self, text, m):
        result = random.choice(["heads", "tails"])
        return self._resp(f"It's {result}, {self.owner}.")

    def _dice(self, text, m):
        d_match = re.search(r"\bd(\d+)\b", text)
        sides = int(d_match.group(1)) if d_match else 6
        sides = max(2, min(sides, 1000))
        return self._resp(f"You rolled a {random.randint(1, sides)} on a d{sides}.")

    def _math(self, text, m):
        expr = re.sub(r"\b(calculate|compute|what is|what'?s|solve|equals?|please|the|result of|how much is)\b",
                      "", text, flags=re.I)
        expr = expr.replace("x", "*").replace("times", "*").replace("plus", "+") \
                   .replace("minus", "-").replace("divided by", "/").replace("over", "/") \
                   .replace("into", "*").replace("?", "").strip().rstrip("= ")
        result = safe_eval(expr)
        if result is None:
            return self._resp("I couldn't parse that calculation, sir. Try something like '12 times 8'.")
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        return self._resp(f"That equals {result}, {self.owner}.")

    def _crypto(self, text, m):
        coin = None
        for word, cid in CRYPTO_IDS.items():
            if re.search(rf"\b{word}\b", text, re.I):
                coin = cid
                break
        if not coin:
            coin = "bitcoin"
        try:
            data = requests.get(
                "https://api.coingecko.com/api/v3/simple/price",
                params={"ids": coin, "vs_currencies": "usd"},
                timeout=10,
            ).json()
            price = data.get(coin, {}).get("usd")
            if price is None:
                return self._resp("I couldn't fetch that price right now, sir.")
            return self._resp(f"One {coin.replace('coin', '').strip()} is currently worth ${price:,.2f} US dollars, {self.owner}.")
        except requests.RequestException:
            return self._resp("The crypto market service is unreachable at the moment, sir.")

    def _wikipedia(self, text, m):
        topic = re.sub(
            r"\b(who is|who was|who are|what is|what are|what was|tell me about|"
            r"search wikipedia for|wikipedia|the|a|an|please|define)\b", "", text, flags=re.I
        ).strip().rstrip(".?!")
        if not topic:
            return self._resp("What would you like me to look up, sir?")
        try:
            resp = requests.get(
                f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(topic)}",
                headers={"Accept": "application/json"}, timeout=10,
            )
            if resp.status_code == 404:
                return self._converse(text)  # fall back to Gemini
            data = resp.json()
            summary = data.get("extract", "")
            title = data.get("title", topic)
            if not summary:
                return self._converse(text)
            summary = summary if len(summary) < 420 else summary[:417].rsplit(" ", 1)[0] + "…"
            return self._resp(f"{title}: {summary}")
        except requests.RequestException:
            return self._converse(text)

    def _open_site(self, text, m):
        target = m.group(2).lower().rstrip(".")
        url = WEBSITES.get(target)
        if url:
            return self._resp(f"Opening {target} for you, {self.owner}.",
                              action="open_url", data={"url": url})
        if "." in target or target.startswith("http"):
            url2 = target if target.startswith("http") else f"https://{target}"
            return self._resp(f"Opening {target}, {self.owner}.",
                              action="open_url", data={"url": url2})
        return self._resp(f"I'm not sure which site '{target}' is, sir. Try 'open youtube'.")

    def _search(self, text, m):
        query = re.sub(
            r"\b(search( the web| google)? for|google|look up|find online|please)\b",
            "", text, flags=re.I).strip()
        if not query:
            return self._resp("What should I search for, sir?")
        url = f"https://www.google.com/search?q={requests.utils.quote(query)}"
        return self._resp(f"Searching the web for {query}, {self.owner}.",
                          action="open_url", data={"url": url})

    def _add_note(self, text, m):
        note = re.sub(r"\b(remember that|take a note|note that|remember this|"
                      r"add a note|save a note|please|jarvis)\b", "", text, flags=re.I).strip()
        if not note:
            return self._resp("What would you like me to remember, sir?")
        self.notes.append({"text": note, "time": datetime.datetime.now().strftime("%H:%M")})
        return self._resp(f"Noted, {self.owner}. I'll remember that.")

    def _list_notes(self, text, m):
        if not self.notes:
            return self._resp("You have no notes saved, sir.")
        listing = "; ".join(f"{n['text']} (at {n['time']})" for n in self.notes)
        return self._resp(f"You have {len(self.notes)} note(s), sir: {listing}", data={"notes": self.notes})

    def _status(self, text, m):
        now = datetime.datetime.now()
        note_count = len(self.notes)
        return self._resp(
            f"All systems operational, {self.owner}. It is {now.strftime('%H:%M')} on "
            f"{now.strftime('%A')}. I have {note_count} note(s) stored and conversation "
            "memory is active. How may I assist?"
        )

    def _capabilities(self, text, m):
        caps = [
            "Tell the time and date", "Weather for any city", "Web search and open sites",
            "Wikipedia lookups", "Math calculations", "Crypto prices", "Tell jokes and facts",
            "Flip coins and roll dice", "Take and read back notes", "Open-ended conversation",
        ]
        body = "Here's what I can do, sir: " + "; ".join(caps) + ". Just ask naturally."
        return self._resp(body)

    def _thanks(self, text, m):
        return self._resp(random.choice(COMPLIMENTS))

    def _bye(self, text, m):
        return self._resp(f"Powering down. It's been a pleasure, {self.owner}. Goodbye.",
                          action="goodbye")

    # -- Conversational fallback ------------------------------------------

    def _converse(self, text):
        reply, err = call_gemini(
            f"User: {text}",
            system_instruction=self.GREETING_PROMPT,
            api_key=self.api_key,
        )
        if err or not reply:
            return self._resp(
                "I'm not quite sure how to respond to that, sir. Could you rephrase?"
            )
        return self._resp(reply)


# Module-level singleton for simple import
_brain = None


def get_brain():
    global _brain
    if _brain is None:
        _brain = JarvisBrain()
    return _brain
