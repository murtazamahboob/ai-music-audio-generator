"""Text analysis: mood, tempo, key and a deterministic seed from raw text.

The mapping is deliberately transparent — a word list per mood, a fixed
tempo and scale per mood — so the same text always produces the same song
and a user can see exactly why a song sounds the way it does.
"""

from __future__ import annotations

import hashlib
import re

from .theory import NOTE_NAMES

MOODS = ("happy", "sad", "calm", "energetic")

MOOD_WORDS = {
    "happy": {
        "joy", "sun", "sunshine", "bright", "dance", "love", "happy", "smile",
        "light", "celebrate", "party", "golden", "laugh", "sweet", "warm",
        "morning", "spring", "hope", "free", "alive",
    },
    "sad": {
        "rain", "lonely", "dark", "tear", "tears", "loss", "sad", "blue",
        "night", "goodbye", "alone", "cold", "empty", "broken", "fall",
        "winter", "grey", "gray", "miss", "gone",
    },
    "calm": {
        "calm", "peace", "peaceful", "quiet", "soft", "slow", "dream",
        "ocean", "breeze", "gentle", "still", "moon", "stars", "sleep",
        "river", "cloud", "easy", "rest",
    },
    "energetic": {
        "run", "fire", "fast", "wild", "power", "beat", "drive", "storm",
        "electric", "loud", "rush", "jump", "fight", "speed", "thunder",
        "blaze", "race", "heart", "pump", "charge",
    },
}

MOOD_TEMPO = {"happy": 120, "sad": 72, "calm": 88, "energetic": 140}
MOOD_SCALE = {"happy": "major", "sad": "minor", "calm": "pentatonic", "energetic": "dorian"}
MOOD_PROGRESSION = {"happy": "pop", "sad": "sad", "calm": "calm", "energetic": "drive"}

_WORD_RE = re.compile(r"[A-Za-z']+")


def words_of(text: str) -> list[str]:
    return _WORD_RE.findall(text.lower())


def text_seed(text: str) -> int:
    """Deterministic integer seed for a text (first 8 bytes of SHA-256)."""
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big")


def detect_mood(text: str) -> str:
    """Mood with the most matching words; 'calm' when nothing matches."""
    words = words_of(text)
    if not words:
        return "calm"
    scores = {mood: sum(1 for w in words if w in lex) for mood, lex in MOOD_WORDS.items()}
    best = max(scores.values())
    if best == 0:
        return "calm"
    # MOODS order breaks ties deterministically: happy, sad, calm, energetic.
    return next(mood for mood in MOODS if scores[mood] == best)


def default_key(text: str) -> str:
    """Key derived from the text seed, so the same text keeps its key."""
    return NOTE_NAMES[text_seed(text) % 12]


def analyze(text: str) -> dict:
    """Full text analysis: mood, tempo, scale, progression, key and seed."""
    if not text or not text.strip():
        raise ValueError("text must not be empty")
    mood = detect_mood(text)
    return {
        "mood": mood,
        "tempo_bpm": MOOD_TEMPO[mood],
        "scale": MOOD_SCALE[mood],
        "progression": MOOD_PROGRESSION[mood],
        "key": default_key(text),
        "seed": text_seed(text),
        "word_count": len(words_of(text)),
    }
