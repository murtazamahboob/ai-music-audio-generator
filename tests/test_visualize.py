import pytest

from musicgen.song import generate_song
from musicgen.synth import render_samples
from musicgen.visualize import piano_roll_ascii, svg_piano_roll, svg_waveform, waveform_ascii

TEXT = "golden morning sunshine dancing light, bright joy and laughter"


def test_waveform_ascii_shape():
    song = generate_song(TEXT)
    art = waveform_ascii(render_samples(song), width=60, height=10)
    lines = art.split("\n")
    assert len(lines) == 10
    assert all(len(line) <= 60 for line in lines)
    assert any("#" in line for line in lines)


def test_waveform_ascii_empty():
    assert waveform_ascii([]) == ""


def test_waveform_ascii_bad_size():
    with pytest.raises(ValueError):
        waveform_ascii([0.1, -0.1], width=0)


def test_piano_roll_has_one_row_per_pitch():
    song = generate_song(TEXT)
    roll = piano_roll_ascii(song)
    pitches = {n.midi for n in song.notes}
    assert len(roll.splitlines()) == len(pitches)
    assert all("#" in line for line in roll.splitlines())


def test_piano_roll_empty_song():
    song = generate_song(TEXT)
    song.notes = []
    assert piano_roll_ascii(song) == ""


def test_svg_waveform_is_valid_svg():
    svg = svg_waveform(render_samples(generate_song(TEXT)))
    assert svg.startswith("<svg")
    assert "<polyline" in svg
    assert svg.count("<svg") == 1


def test_svg_piano_roll_has_one_rect_per_note():
    song = generate_song(TEXT)
    svg = svg_piano_roll(song)
    assert svg.startswith("<svg")
    assert svg.count("<rect") == len(song.notes) + 1  # +1 background
    assert "C" in svg or "D" in svg  # note titles present


def test_svg_empty_inputs():
    assert svg_waveform([]).startswith("<svg")
    song = generate_song(TEXT)
    song.notes = []
    assert svg_piano_roll(song).startswith("<svg")
