"""
gemini_client.py — Groq Drop-In Replacement for ResearchIt
===========================================================

Replaces the Gemini backend with Groq while keeping the EXACT same
public API — no other file needs any changes:

    from gemini_client import get_client
    text  = get_client().generate(prompt)
    texts = get_client().generate_batch(list_of_prompts)

Groq API is OpenAI-compatible, so we use the groq SDK.

Install dependency (once):
    pip install groq

.env — add ONE line:
    GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx

Get your free key at: https://console.groq.com/

Free tier limits (as of 2025):
    llama-3.3-70b-versatile : 30 RPM | 14,400 RPD | 131,072 ctx
    llama-3.1-8b-instant    : 30 RPM | 14,400 RPD | 131,072 ctx  ← fast fallback
    mixtral-8x7b-32768      : 30 RPM | 14,400 RPD | 32,768 ctx

DEFAULT_MODEL uses llama-3.3-70b-versatile — best quality on free tier.
FALLBACK_MODEL switches to llama-3.1-8b-instant when daily cap is near.
"""

import os
import time
import hashlib
import json
import random
import threading
from datetime import date
from pathlib import Path
from typing import List, Optional

from groq import Groq, RateLimitError, APIStatusError


# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURATION — tune to your plan
# ══════════════════════════════════════════════════════════════════════════════

DEFAULT_MODEL  = "llama-3.3-70b-versatile"   # best free-tier quality
FALLBACK_MODEL = "llama-3.1-8b-instant"       # fast fallback when cap is near

RPM_LIMIT   = 28          # stay safely under 30 RPM (Groq free tier)
RPD_LIMIT   = 13000       # stay under 14,400 RPD with a safety buffer
RPD_WARN_AT = 11000       # switch to fallback model above this count

MAX_RETRIES = 3
BASE_DELAY  = 2.0         # seconds before first retry
MAX_DELAY   = 30.0        # hard ceiling per retry

SESSION_BUDGET = 9999     # max API calls per process lifetime

CACHE_MAX_MEM  = 512
CACHE_FILE     = Path(".groq_cache.json")
CACHE_MAX_DISK = 2000
BATCH_SIZE     = 4        # prompts merged per API call

MAX_TOKENS     = 4096     # per-call token ceiling


# ══════════════════════════════════════════════════════════════════════════════
# DISK-PERSISTED CACHE
# ══════════════════════════════════════════════════════════════════════════════

class _Cache:
    def __init__(self):
        self._mem:  dict = {}
        self._lock       = threading.Lock()
        self._load_disk()

    def get(self, prompt: str) -> Optional[str]:
        with self._lock:
            return self._mem.get(self._key(prompt))

    def set(self, prompt: str, value: str) -> None:
        k = self._key(prompt)
        with self._lock:
            self._mem[k] = value
            if len(self._mem) > CACHE_MAX_MEM:
                evict = list(self._mem.keys())[: CACHE_MAX_MEM // 4]
                for ek in evict:
                    del self._mem[ek]
        threading.Thread(target=self._save_disk, daemon=True).start()

    def size(self) -> int:
        return len(self._mem)

    @staticmethod
    def _key(prompt: str) -> str:
        return hashlib.sha256(prompt.encode()).hexdigest()[:32]

    def _load_disk(self) -> None:
        try:
            if CACHE_FILE.exists():
                data = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
                with self._lock:
                    self._mem.update(data)
        except Exception:
            pass

    def _save_disk(self) -> None:
        try:
            with self._lock:
                snapshot = dict(list(self._mem.items())[-CACHE_MAX_DISK:])
            CACHE_FILE.write_text(json.dumps(snapshot, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass


# ══════════════════════════════════════════════════════════════════════════════
# DAILY REQUEST COUNTER
# ══════════════════════════════════════════════════════════════════════════════

class _DailyCounter:
    _FILE = Path(".groq_daily.json")

    def __init__(self):
        self._lock  = threading.Lock()
        self._today = str(date.today())
        self._count = self._load()

    def increment(self) -> int:
        with self._lock:
            if str(date.today()) != self._today:
                self._today = str(date.today())
                self._count = 0
            self._count += 1
            count = self._count
        threading.Thread(target=self._save, daemon=True).start()
        return count

    def value(self) -> int:
        with self._lock:
            if str(date.today()) != self._today:
                return 0
            return self._count

    def _load(self) -> int:
        try:
            if self._FILE.exists():
                data = json.loads(self._FILE.read_text())
                if data.get("date") == self._today:
                    return int(data.get("count", 0))
        except Exception:
            pass
        return 0

    def _save(self) -> None:
        try:
            with self._lock:
                data = {"date": self._today, "count": self._count}
            self._FILE.write_text(json.dumps(data))
        except Exception:
            pass


# ══════════════════════════════════════════════════════════════════════════════
# SESSION BUDGET
# ══════════════════════════════════════════════════════════════════════════════

class _SessionBudget:
    def __init__(self, limit: int = SESSION_BUDGET):
        self._limit = limit
        self._used  = 0
        self._lock  = threading.Lock()

    def acquire(self) -> bool:
        with self._lock:
            if self._used >= self._limit:
                return False
            self._used += 1
            return True

    def value(self) -> int:
        with self._lock:
            return self._used

    def remaining(self) -> int:
        with self._lock:
            return max(0, self._limit - self._used)


# ══════════════════════════════════════════════════════════════════════════════
# RPM THROTTLE
# ══════════════════════════════════════════════════════════════════════════════

class _RpmThrottle:
    def __init__(self, rpm: int = RPM_LIMIT):
        self._rpm    = rpm
        self._window = 60.0
        self._calls: List[float] = []
        self._lock   = threading.Lock()

    def acquire(self) -> None:
        while True:
            with self._lock:
                now = time.time()
                self._calls = [t for t in self._calls if now - t < self._window]
                if len(self._calls) < self._rpm:
                    self._calls.append(now)
                    return
                wait = self._window - (now - self._calls[0]) + 0.1
            time.sleep(wait)


# ══════════════════════════════════════════════════════════════════════════════
# PROMPT COMPRESSION
# ══════════════════════════════════════════════════════════════════════════════

def _compress(prompt: str) -> str:
    lines  = [ln.rstrip() for ln in prompt.splitlines()]
    result, blanks = [], 0
    for ln in lines:
        if ln == "":
            blanks += 1
            if blanks <= 1:
                result.append(ln)
        else:
            blanks = 0
            result.append(ln)
    return "\n".join(result).strip()


# ══════════════════════════════════════════════════════════════════════════════
# MAIN CLIENT
# ══════════════════════════════════════════════════════════════════════════════

class GeminiClient:
    """
    Groq-backed client. Named GeminiClient so every existing import keeps
    working without any changes anywhere else in the project.
    """

    def __init__(self, api_key: Optional[str] = None):
        key = api_key or os.getenv("GROQ_API_KEY")
        if not key:
            raise EnvironmentError(
                "GROQ_API_KEY not set.\n"
                "Add this line to your .env file:\n"
                "    GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx\n"
                "Get your free key at: https://console.groq.com/"
            )
        self._client   = Groq(api_key=key)
        self._cache    = _Cache()
        self._throttle = _RpmThrottle()
        self._daily    = _DailyCounter()
        self._session  = _SessionBudget()

    # ── single call ───────────────────────────────────────────────────────

    def generate(self, prompt: str, *, use_cache: bool = True, fallback: str = "") -> str:
        prompt = _compress(prompt)
        if use_cache:
            hit = self._cache.get(prompt)
            if hit is not None:
                return hit
        result = self._call(prompt, fallback)
        if use_cache and result:
            self._cache.set(prompt, result)
        return result

    # ── batch call ────────────────────────────────────────────────────────

    def generate_batch(
        self, prompts: List[str], *, use_cache: bool = True, fallback: str = ""
    ) -> List[str]:
        prompts  = [_compress(p) for p in prompts]
        results  = [""] * len(prompts)
        to_fetch = []

        for i, p in enumerate(prompts):
            if use_cache:
                hit = self._cache.get(p)
                if hit is not None:
                    results[i] = hit
                    continue
            to_fetch.append((i, p))

        for start in range(0, len(to_fetch), BATCH_SIZE):
            batch = to_fetch[start : start + BATCH_SIZE]

            if len(batch) == 1:
                idx, p       = batch[0]
                results[idx] = self._call(p, fallback)
                if use_cache and results[idx]:
                    self._cache.set(p, results[idx])
                continue

            raw    = self._call(self._build_merged(batch), fallback="")
            parsed = self._split_merged(raw, len(batch)) if raw else None

            if parsed:
                for (idx, p), text in zip(batch, parsed):
                    results[idx] = text or fallback
                    if use_cache and text:
                        self._cache.set(p, text)
            else:
                # Merged parse failed — fall back to individual calls
                for idx, p in batch:
                    results[idx] = self._call(p, fallback)
                    if use_cache and results[idx]:
                        self._cache.set(p, results[idx])

        return results

    # ── Streamlit quota widget ────────────────────────────────────────────

    def show_usage_status(self) -> None:
        try:
            import streamlit as st
            used      = self._daily.value()
            cached    = self._cache.size()
            sess_used = self._session.value()
            sess_left = self._session.remaining()
            pct       = round(used / RPD_LIMIT * 100)
            colour    = "green" if pct < 60 else ("orange" if pct < 85 else "red")
            st.markdown(
                f"**API quota today:** :{colour}[{used} / {RPD_LIMIT} calls ({pct} %)] &nbsp;|&nbsp;"
                f" 🔁 Session: **{sess_used} used, {sess_left} left** &nbsp;|&nbsp;"
                f" 📦 Cached: **{cached}** &nbsp;|&nbsp;"
                f" 🤖 Model: **{DEFAULT_MODEL}**"
            )
            if used >= RPD_WARN_AT:
                st.warning(f"⚠️ Approaching daily limit ({used}/{RPD_LIMIT}). Resets at midnight UTC.")
            if sess_left == 0:
                st.error("🛑 Session budget reached. Restart the app to continue.")
        except ImportError:
            pass

    # ── helpers ───────────────────────────────────────────────────────────

    def cache_size(self)  -> int:  return self._cache.size()
    def daily_used(self)  -> int:  return self._daily.value()
    def clear_cache(self) -> None: self._cache = _Cache()

    # ── internal ─────────────────────────────────────────────────────────

    def _pick_model(self) -> str:
        return FALLBACK_MODEL if self._daily.value() >= RPD_WARN_AT else DEFAULT_MODEL

    def _call(self, prompt: str, fallback: str) -> str:
        if self._daily.value() >= RPD_LIMIT:
            return fallback
        if not self._session.acquire():
            return fallback

        delay = BASE_DELAY
        for attempt in range(MAX_RETRIES):
            try:
                self._throttle.acquire()
                response = self._client.chat.completions.create(
                    model=self._pick_model(),
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=MAX_TOKENS,
                )
                text = (response.choices[0].message.content or "").strip()
                self._daily.increment()
                if text:
                    return text

            except RateLimitError:
                # Hard quota hit — bail immediately, no retries
                return self._cache.get(prompt) or fallback

            except APIStatusError as e:
                err       = str(e).lower()
                transient = any(k in err for k in ("503", "502", "unavailable", "overloaded"))
                if attempt < MAX_RETRIES - 1 and transient:
                    jitter = delay * (0.1 + random.random() * 0.3)
                    time.sleep(min(delay + jitter, MAX_DELAY))
                    delay  = min(delay * 2, MAX_DELAY)
                else:
                    break

            except Exception:
                break

        return fallback if fallback else "No response generated."

    @staticmethod
    def _build_merged(batch: List[tuple]) -> str:
        parts  = [f"=== TASK {i+1} ===\n{p}" for i, (_, p) in enumerate(batch)]
        header = (
            f"Answer {len(batch)} independent tasks IN ORDER.\n"
            f"Separate answers with exactly: <<<END>>>\n"
            f"No extra text between answers.\n\n"
        )
        return header + "\n\n".join(parts)

    @staticmethod
    def _split_merged(raw: str, expected: int) -> Optional[List[str]]:
        parts = [p.strip() for p in raw.split("<<<END>>>") if p.strip()]
        return parts if len(parts) == expected else None


# ══════════════════════════════════════════════════════════════════════════════
# SINGLETON ACCESSOR
# ══════════════════════════════════════════════════════════════════════════════

_client:      Optional[GeminiClient] = None
_client_lock: threading.Lock         = threading.Lock()


def get_client(api_key: Optional[str] = None) -> GeminiClient:
    """Return the shared GroqClient (created once on first call, reused everywhere)."""
    global _client
    if _client is None:
        with _client_lock:
            if _client is None:
                _client = GeminiClient(api_key=api_key)
    return _client