import pytest

from musicgen.theory import (
    CHORD_INTERVALS,
    PROGRESSIONS,
    SCALES,
    chord_for_degree,
    chord_notes,
    key_to_pitch_class,
    midi_to_freq,
    note_name,
    progression_chords,
    scale_notes,
)


def test_a4_is_440hz():
    assert midi_to_freq(69) == pytest.approx(440.0)


def test_octave_doubles_frequency():
    assert midi_to_freq(81) == pytest.approx(880.0)
    assert midi_to_freq(57) == pytest.approx(220.0)


def test_note_names():
    assert note_name(60) == "C4"
    assert note_name(69) == "A4"
    assert note_name(61) == "C#4"
    assert note_name(59) == "B3"


def test_key_parsing_sharps_and_flats():
    assert key_to_pitch_class("C") == 0
    assert key_to_pitch_class("F#") == 6
    assert key_to_pitch_class("Bb") == 10
    assert key_to_pitch_class("Eb") == 3


def test_unknown_key_raises():
    with pytest.raises(ValueError):
        key_to_pitch_class("H")


def test_major_scale_notes_in_c():
    notes = scale_notes("C", "major", 60, 71)
    assert notes == [60, 62, 64, 65, 67, 69, 71]
    assert all(note_name(n).startswith(("C", "D", "E", "F", "G", "A", "B")) for n in notes)


def test_minor_scale_has_flat_third():
    notes = scale_notes("A", "minor", 60, 71)
    assert 60 in notes  # C natural is the minor third of A
    assert 61 not in notes  # C# is not in A minor


def test_all_scales_nonempty_and_sorted():
    for name in SCALES:
        notes = scale_notes("C", name, 60, 83)
        assert notes == sorted(notes)
        assert len(notes) >= 10


def test_unknown_scale_raises():
    with pytest.raises(ValueError):
        scale_notes("C", "locrian-ish")


def test_chord_notes():
    assert chord_notes(60, "major") == [60, 64, 67]
    assert chord_notes(60, "minor") == [60, 63, 67]
    assert chord_notes(60, "dominant7") == [60, 64, 67, 70]
    assert len(CHORD_INTERVALS["major7"]) == 4


def test_unknown_chord_raises():
    with pytest.raises(ValueError):
        chord_notes(60, "mystery")


def test_chord_for_degree_major_scale():
    root, kind = chord_for_degree("C", "major", 0)
    assert root == 48 and kind == "major"  # C major, tonic
    root, kind = chord_for_degree("C", "major", 5)
    assert kind == "minor"  # vi chord


def test_progression_chords_one_per_bar():
    chords = progression_chords("C", "major", "pop", 6)
    assert len(chords) == 6
    assert chords[0] == chords[4]  # progression cycles every 4 bars
    assert all(isinstance(root, int) and kind in ("major", "minor") for root, kind in chords)


def test_unknown_progression_raises():
    with pytest.raises(ValueError):
        progression_chords("C", "major", "nope", 2)


def test_progression_names_known():
    assert set(PROGRESSIONS) == {"pop", "sad", "calm", "drive"}
