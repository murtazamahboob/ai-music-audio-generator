"""Music theory helpers: notes, scales, chords and progressions.

Pure standard library. A MIDI number is the single source of truth for
pitch; note names, frequencies and scale membership are all derived from it.
"""

from __future__ import annotations

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
_FLATS = {"Db": 1, "Eb": 3, "Gb": 6, "Ab": 8, "Bb": 10}

SCALES = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "pentatonic": [0, 2, 4, 7, 9],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "blues": [0, 3, 5, 6, 7, 10],
}

CHORD_INTERVALS = {
    "major": [0, 4, 7],
    "minor": [0, 3, 7],
    "diminished": [0, 3, 6],
    "major7": [0, 4, 7, 11],
    "minor7": [0, 3, 7, 10],
    "dominant7": [0, 4, 7, 10],
}

# Scale-degree progressions, as indices into the scale (0-based).
PROGRESSIONS = {
    "pop": [0, 4, 5, 3],        # I - V - vi - IV
    "sad": [0, 5, 3, 4],        # i - VI - III - VII
    "calm": [0, 3, 4, 3],       # I - IV - V - IV
    "drive": [0, 0, 3, 4],      # I - I - IV - V
}


def midi_to_freq(midi: int) -> float:
    """Equal-tempered frequency of a MIDI note; A4 (69) is 440 Hz."""
    return 440.0 * (2.0 ** ((midi - 69) / 12.0))


def note_name(midi: int) -> str:
    """E.g. 60 -> 'C4', 69 -> 'A4'."""
    return f"{NOTE_NAMES[midi % 12]}{midi // 12 - 1}"


def key_to_pitch_class(key: str) -> int:
    """'C' -> 0, 'F#' -> 6, 'Bb' -> 10. Raises ValueError on unknown keys."""
    key = key.strip()
    if key in NOTE_NAMES:
        return NOTE_NAMES.index(key)
    if key in _FLATS:
        return _FLATS[key]
    raise ValueError(f"unknown key: {key!r} (use C, C#, D, Eb, ...)")


def scale_notes(key: str, scale: str, low_midi: int = 60, high_midi: int = 83) -> list[int]:
    """All MIDI notes of ``scale`` in ``key`` between low_midi and high_midi."""
    if scale not in SCALES:
        raise ValueError(f"unknown scale: {scale!r} (try {sorted(SCALES)})")
    pc = key_to_pitch_class(key)
    intervals = set(SCALES[scale])
    return [m for m in range(low_midi, high_midi + 1) if (m - pc) % 12 in intervals]


def chord_notes(root_midi: int, kind: str) -> list[int]:
    """MIDI notes of a chord built on root_midi."""
    if kind not in CHORD_INTERVALS:
        raise ValueError(f"unknown chord kind: {kind!r} (try {sorted(CHORD_INTERVALS)})")
    return [root_midi + i for i in CHORD_INTERVALS[kind]]


def chord_for_degree(key: str, scale: str, degree: int, octave_midi: int = 48) -> tuple[int, str]:
    """Root MIDI note and kind of the chord on a scale degree.

    The kind is read off the third: a major third (4 semitones) means a
    major chord, anything else a minor chord for the scales we ship.
    """
    notes = scale_notes(key, scale, octave_midi, octave_midi + 11)
    root = notes[degree % len(notes)]
    third = notes[(degree + 2) % len(notes)]
    # Third may wrap into the next octave; compare pitch classes.
    interval = (third - root) % 12
    kind = "major" if interval == 4 else "minor"
    return root, kind


def progression_chords(key: str, scale: str, name: str, bars: int) -> list[tuple[int, str]]:
    """One chord per bar, cycling the named progression."""
    if name not in PROGRESSIONS:
        raise ValueError(f"unknown progression: {name!r} (try {sorted(PROGRESSIONS)})")
    degrees = PROGRESSIONS[name]
    return [chord_for_degree(key, scale, degrees[i % len(degrees)]) for i in range(bars)]
