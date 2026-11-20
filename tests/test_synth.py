import wave

import pytest

from musicgen.song import generate_song
from musicgen.synth import DEFAULT_SAMPLE_RATE, render_samples, render_wav

TEXT = "golden morning sunshine dancing light, bright joy and laughter"


def test_render_samples_length_matches_duration(tmp_path):
    song = generate_song(TEXT)
    samples = render_samples(song)
    expected = int((song.duration_seconds + 0.3) * DEFAULT_SAMPLE_RATE)
    assert len(samples) == expected


def test_samples_in_range_and_not_silent():
    song = generate_song(TEXT)
    samples = render_samples(song)
    assert all(-1.0 <= s <= 1.0 for s in samples)
    assert max(abs(s) for s in samples) > 0.1
    # The opening attack is quieter than the middle of the first note.
    assert abs(samples[100]) < max(abs(s) for s in samples[1000:5000])


def test_render_is_deterministic():
    song = generate_song(TEXT)
    assert render_samples(song) == render_samples(song)


def test_different_moods_sound_different():
    happy = render_samples(generate_song(TEXT, mood="happy"))
    sad = render_samples(generate_song(TEXT, mood="sad"))
    assert happy != sad


def test_wav_file_is_valid(tmp_path):
    song = generate_song(TEXT)
    path = tmp_path / "song.wav"
    assert render_wav(song, str(path)) == str(path)
    with wave.open(str(path), "rb") as wav:
        assert wav.getnchannels() == 1
        assert wav.getsampwidth() == 2
        assert wav.getframerate() == DEFAULT_SAMPLE_RATE
        assert wav.getnframes() == len(render_samples(song))


def test_wav_bytes_deterministic(tmp_path):
    song = generate_song(TEXT)
    first = tmp_path / "a.wav"
    second = tmp_path / "b.wav"
    render_wav(song, str(first))
    render_wav(song, str(second))
    assert first.read_bytes() == second.read_bytes()
