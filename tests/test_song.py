import pytest

from musicgen.song import generate_song
from musicgen.theory import scale_notes

TEXT = "golden morning sunshine dancing light, bright joy and laughter"


def test_generate_deterministic():
    a = generate_song(TEXT)
    b = generate_song(TEXT)
    assert [(n.midi, n.start_beat, n.duration_beats) for n in a.notes] == [
        (n.midi, n.start_beat, n.duration_beats) for n in b.notes
    ]
    assert a.summary() == b.summary()


def test_one_note_per_word():
    song = generate_song(TEXT)
    assert len(song.notes) == 9  # 9 words in TEXT


def test_notes_stay_in_scale():
    song = generate_song(TEXT, key="C", scale="major")
    allowed = set(scale_notes("C", "major", 60, 83))
    assert all(n.midi in allowed for n in song.notes)


def test_notes_are_ordered_and_non_overlapping():
    song = generate_song(TEXT)
    starts = [n.start_beat for n in song.notes]
    assert starts == sorted(starts)
    for first, second in zip(song.notes, song.notes[1:]):
        assert first.start_beat + first.duration_beats <= second.start_beat + 1e-9


def test_punctuation_creates_rests():
    plain = generate_song("golden morning sunshine dancing light bright joy laughter")
    punct = generate_song(TEXT)  # same words, with a comma
    assert punct.total_beats > plain.total_beats


def test_mood_override_changes_scale_and_tempo():
    song = generate_song(TEXT, mood="sad")
    assert song.mood == "sad"
    assert song.scale == "minor"
    assert song.tempo_bpm == 72


def test_explicit_key_scale_tempo_win():
    song = generate_song(TEXT, key="G", scale="pentatonic", tempo_bpm=100)
    assert song.key == "G" and song.scale == "pentatonic" and song.tempo_bpm == 100


def test_unknown_mood_raises():
    with pytest.raises(ValueError):
        generate_song(TEXT, mood="spooky")


def test_bad_tempo_raises():
    with pytest.raises(ValueError):
        generate_song(TEXT, tempo_bpm=0)


def test_empty_text_raises():
    with pytest.raises(ValueError):
        generate_song("   ")


def test_chords_one_per_bar_and_bass_matches():
    song = generate_song(TEXT)
    assert len(song.chords) == song.bars
    assert len(song.bass_notes) == song.bars
    for (root, _kind), bass in zip(song.chords, song.bass_notes):
        assert bass.midi == root - 12


def test_short_text_gets_second_pass():
    song = generate_song("sun light")
    assert len(song.notes) == 4  # 2 words, repeated an octave lower
    assert song.notes[2].midi == song.notes[0].midi - 12


def test_duration_seconds_matches_tempo():
    song = generate_song(TEXT, tempo_bpm=120)
    assert song.duration_seconds == pytest.approx(song.total_beats * 0.5)


def test_summary_fields():
    summary = generate_song(TEXT).summary()
    assert summary["notes"] == 9
    assert summary["bars"] >= 1
    assert summary["duration_seconds"] > 0
