import pytest

from musicgen.text import MOOD_SCALE, MOOD_TEMPO, analyze, default_key, detect_mood, text_seed, words_of


def test_words_of_lowercases_and_strips_punctuation():
    assert words_of("Golden Morning, dancing!") == ["golden", "morning", "dancing"]


def test_detect_mood_happy():
    assert detect_mood("golden sunshine, dancing with joy and love") == "happy"


def test_detect_mood_sad():
    assert detect_mood("lonely rain at night, tears and goodbye") == "sad"


def test_detect_mood_calm():
    assert detect_mood("quiet ocean breeze, soft moon and gentle dreams") == "calm"


def test_detect_mood_energetic():
    assert detect_mood("fire and thunder, run fast, wild power") == "energetic"


def test_detect_mood_defaults_to_calm():
    assert detect_mood("the quick brown fox") == "calm"
    assert detect_mood("") == "calm"


def test_text_seed_deterministic():
    assert text_seed("hello world") == text_seed("hello world")
    assert text_seed("hello world") != text_seed("hello there")


def test_default_key_deterministic_and_valid():
    key = default_key("golden morning")
    assert key in ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
    assert default_key("golden morning") == key


def test_analyze_happy():
    info = analyze("golden sunshine dancing with joy")
    assert info["mood"] == "happy"
    assert info["tempo_bpm"] == MOOD_TEMPO["happy"]
    assert info["scale"] == MOOD_SCALE["happy"]
    assert info["word_count"] == 5


def test_analyze_sad_is_slower():
    assert analyze("lonely rain tears goodbye")["tempo_bpm"] < analyze("fire thunder run fast")["tempo_bpm"]


def test_analyze_empty_raises():
    with pytest.raises(ValueError):
        analyze("   ")
    with pytest.raises(ValueError):
        analyze("")
