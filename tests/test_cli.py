import json

import pytest

from musicgen.cli import main


def test_cli_writes_wav_svg_and_report(tmp_path, capsys):
    out = tmp_path / "song.wav"
    svg = tmp_path / "roll.svg"
    report = tmp_path / "report.json"
    rc = main(["golden morning sunshine dancing light", "--out", str(out),
               "--svg", str(svg), "--report", str(report)])
    assert rc == 0
    assert out.exists() and out.stat().st_size > 1000
    assert svg.read_text().startswith("<svg")
    data = json.loads(report.read_text())
    assert data["mood"] == "happy" and data["notes"] == 10  # 5 words, repeated an octave lower
    captured = capsys.readouterr()
    assert "happy" in captured.out and str(out) in captured.out


def test_cli_mood_override(tmp_path):
    out = tmp_path / "song.wav"
    assert main(["rain tears goodbye", "--mood", "happy", "--out", str(out)]) == 0


def test_cli_no_text_errors(capsys):
    assert main([]) == 2
    assert "provide text" in capsys.readouterr().err


def test_cli_bad_mood_errors():
    # argparse rejects an unknown --mood choice with SystemExit(2).
    with pytest.raises(SystemExit) as exc:
        main(["hello world", "--mood", "spooky"])
    assert exc.value.code == 2


def test_cli_list_scales_and_moods(capsys):
    assert main(["--list-scales"]) == 0
    assert "major" in capsys.readouterr().out
    assert main(["--list-moods"]) == 0
    assert "happy" in capsys.readouterr().out


def test_cli_wave_svg(tmp_path):
    out = tmp_path / "song.wav"
    wave_svg = tmp_path / "wave.svg"
    assert main(["sun light", "--out", str(out), "--wave-svg", str(wave_svg)]) == 0
    assert "<polyline" in wave_svg.read_text()
