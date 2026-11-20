"""Song structure: turn text into a melody, chords and a bass line.

Melody rule (deterministic, no randomness beyond the text seed): walk
stepwise through the scale — each word moves the pitch by a small step
derived from the word itself, so the contour follows the text. Word length
sets note length; commas and full stops become rests.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .text import MOOD_PROGRESSION, MOOD_SCALE, MOOD_TEMPO, analyze, words_of
from .theory import chord_notes, progression_chords, scale_notes

BEATS_PER_BAR = 4


@dataclass(frozen=True)
class Note:
    midi: int
    start_beat: float
    duration_beats: float
    velocity: float = 0.8


@dataclass
class Song:
    title: str
    text: str
    mood: str
    tempo_bpm: int
    key: str
    scale: str
    progression: str
    notes: list[Note] = field(default_factory=list)
    chords: list[tuple[int, str]] = field(default_factory=list)
    bass_notes: list[Note] = field(default_factory=list)

    @property
    def total_beats(self) -> float:
        if not self.notes:
            return 0.0
        return max(n.start_beat + n.duration_beats for n in self.notes)

    @property
    def bars(self) -> int:
        return max(1, math.ceil(self.total_beats / BEATS_PER_BAR))

    @property
    def duration_seconds(self) -> float:
        return self.total_beats * 60.0 / self.tempo_bpm

    def summary(self) -> dict:
        return {
            "title": self.title,
            "mood": self.mood,
            "tempo_bpm": self.tempo_bpm,
            "key": self.key,
            "scale": self.scale,
            "progression": self.progression,
            "notes": len(self.notes),
            "bars": self.bars,
            "total_beats": self.total_beats,
            "duration_seconds": round(self.duration_seconds, 2),
        }


def _word_step(word: str) -> int:
    """Step in the scale for one word: -2..+2, from the word's letters."""
    return (sum(ord(c) for c in word) % 5) - 2


def _word_duration(word: str) -> float:
    if len(word) <= 3:
        return 0.5
    if len(word) <= 6:
        return 1.0
    return 1.5


def _rests_after_words(text: str, words: list[str]) -> list[float]:
    """Rest length after each word, from the punctuation that follows it."""
    rests: list[float] = []
    pos = 0
    lower = text.lower()
    for word in words:
        idx = lower.find(word, pos)
        pos = idx + len(word)
        rest = 0.0
        while pos < len(text) and text[pos] in ",.;:!?":
            rest = 1.0 if text[pos] in ".!?" else max(rest, 0.5)
            pos += 1
        rests.append(rest)
    return rests


def generate_song(
    text: str,
    title: str | None = None,
    mood: str | None = None,
    tempo_bpm: int | None = None,
    key: str | None = None,
    scale: str | None = None,
    seed: int | None = None,
) -> Song:
    """Build a Song from text. Explicit arguments override the analysis."""
    info = analyze(text)
    mood_overridden = mood is not None
    mood = mood or info["mood"]
    if mood not in ("happy", "sad", "calm", "energetic"):
        raise ValueError(f"unknown mood: {mood!r}")
    # An explicit mood brings its own tempo, scale and progression;
    # explicit tempo/scale arguments still win over the mood defaults.
    tempo = tempo_bpm if tempo_bpm is not None else (
        MOOD_TEMPO[mood] if mood_overridden else info["tempo_bpm"])
    if tempo <= 0:
        raise ValueError("tempo_bpm must be positive")
    key = key or info["key"]
    scale = scale or (MOOD_SCALE[mood] if mood_overridden else info["scale"])
    progression = MOOD_PROGRESSION[mood] if mood_overridden else info["progression"]
    # Seed is accepted for API stability; the melody is a pure function
    # of the text, so the same text always gives the same song.
    _ = seed if seed is not None else info["seed"]

    scale_midis = scale_notes(key, scale, 60, 83)
    words = words_of(text)
    rests = _rests_after_words(text, words)

    notes: list[Note] = []
    index = len(scale_midis) // 2
    beat = 0.0
    for word, rest in zip(words, rests):
        index = max(0, min(len(scale_midis) - 1, index + _word_step(word)))
        duration = _word_duration(word)
        notes.append(Note(midi=scale_midis[index], start_beat=beat, duration_beats=duration))
        beat += duration + rest

    # Short texts get a second pass an octave lower so every song has
    # enough material to visualise and to hear.
    if len(notes) < 8:
        extra: list[Note] = []
        start = beat
        for note in notes:
            extra.append(Note(midi=note.midi - 12, start_beat=start + note.start_beat,
                              duration_beats=note.duration_beats))
        notes.extend(extra)

    song = Song(
        title=title or (text.strip().splitlines()[0][:40] if text.strip() else "Untitled"),
        text=text,
        mood=mood,
        tempo_bpm=tempo,
        key=key,
        scale=scale,
        progression=progression,
        notes=notes,
    )
    song.chords = progression_chords(key, scale, song.progression, song.bars)
    song.bass_notes = [
        Note(midi=root - 12, start_beat=float(bar * BEATS_PER_BAR),
             duration_beats=float(BEATS_PER_BAR), velocity=0.6)
        for bar, (root, _kind) in enumerate(song.chords)
    ]
    return song


def chord_note_list(song: Song) -> list[list[int]]:
    """Expanded chord notes (MIDI) for each bar of the song."""
    return [chord_notes(root, kind) for root, kind in song.chords]
