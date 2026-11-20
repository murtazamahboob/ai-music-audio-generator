"""Offline WAV synthesis: turn a Song into audible audio, stdlib only.

Melody notes are sine waves with two harmonics under a simple ADSR
envelope; chords are soft pads and the bass is a pure sine an octave
below the chord root. Everything is deterministic — rendering the same
song twice produces byte-identical WAV files.
"""

from __future__ import annotations

import math
import struct
import wave

from .song import Song
from .theory import chord_notes, midi_to_freq

DEFAULT_SAMPLE_RATE = 22050


def _adsr(t: float, duration: float) -> float:
    """Attack-decay-sustain-release envelope, 0..1, for time t in a note."""
    if duration <= 0:
        return 0.0
    attack = min(0.05, duration * 0.2)
    release = min(0.10, duration * 0.3)
    if t < attack:
        return t / attack if attack else 1.0
    if t > duration - release:
        return max(0.0, (duration - t) / release) if release else 0.0
    return 1.0


def _tone(freq: float, t: float, duration: float, velocity: float) -> float:
    env = _adsr(t, duration)
    # Fundamental + 2nd and 3rd harmonics, decaying in strength.
    value = (
        math.sin(2 * math.pi * freq * t)
        + 0.5 * math.sin(2 * math.pi * freq * 2 * t)
        + 0.25 * math.sin(2 * math.pi * freq * 3 * t)
    )
    return velocity * env * value / 1.75


def render_samples(song: Song, sample_rate: int = DEFAULT_SAMPLE_RATE) -> list[float]:
    """Float samples in [-1, 1] for the whole song."""
    seconds_per_beat = 60.0 / song.tempo_bpm
    total_seconds = song.duration_seconds + 0.3  # let the last note ring out
    count = int(total_seconds * sample_rate)
    samples = [0.0] * count

    def add_note(midi: int, start_beat: float, duration_beats: float, velocity: float, gain: float = 1.0):
        freq = midi_to_freq(midi)
        start = int(start_beat * seconds_per_beat * sample_rate)
        length = int(duration_beats * seconds_per_beat * sample_rate)
        duration = duration_beats * seconds_per_beat
        for i in range(length):
            idx = start + i
            if idx >= count:
                break
            samples[idx] += gain * _tone(freq, i / sample_rate, duration, velocity)

    for note in song.notes:
        add_note(note.midi, note.start_beat, note.duration_beats, note.velocity, gain=0.55)
    for bar, (root, kind) in enumerate(song.chords):
        for midi in chord_notes(root, kind):
            add_note(midi, bar * 4.0, 4.0, 0.25, gain=0.30)
    for note in song.bass_notes:
        add_note(note.midi, note.start_beat, note.duration_beats, note.velocity, gain=0.45)

    peak = max((abs(s) for s in samples), default=0.0)
    if peak > 1.0:
        samples = [s / peak for s in samples]
    return samples


def render_wav(song: Song, path: str, sample_rate: int = DEFAULT_SAMPLE_RATE) -> str:
    """Write the song as a 16-bit mono WAV file; returns the path."""
    samples = render_samples(song, sample_rate)
    frames = b"".join(struct.pack("<h", max(-32768, min(32767, int(s * 32767)))) for s in samples)
    with wave.open(path, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(frames)
    return path
