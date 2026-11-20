"""Demo: three texts in three moods -> three WAVs, SVGs and a summary."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from musicgen import generate_song, render_samples, render_wav  # noqa: E402
from musicgen.visualize import piano_roll_ascii, svg_piano_roll, svg_waveform, waveform_ascii  # noqa: E402

PROMPTS = [
    ("sunrise", "golden morning sunshine dancing light, bright joy and laughter"),
    ("rain", "lonely rain at night, tears and goodbye in the cold dark"),
    ("storm", "fire and thunder, run fast, wild power, electric storm drive"),
]

OUT = Path(__file__).resolve().parents[1] / "outputs"
OUT.mkdir(exist_ok=True)


def main() -> None:
    rows = []
    for name, text in PROMPTS:
        song = generate_song(text, title=name)
        wav = OUT / f"{name}.wav"
        render_wav(song, str(wav))
        samples = render_samples(song)
        (OUT / f"{name}-piano-roll.svg").write_text(svg_piano_roll(song), encoding="utf-8")
        (OUT / f"{name}-waveform.svg").write_text(svg_waveform(samples), encoding="utf-8")
        rows.append({**song.summary(), "wav": str(wav)})
        print(f"{name}: {song.mood}, {song.key} {song.scale}, {song.tempo_bpm} BPM, "
              f"{len(song.notes)} notes, {song.duration_seconds:.2f}s")
        print(waveform_ascii(samples))
        print(piano_roll_ascii(song))
        print()
    (OUT / "summary.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print(f"wrote {len(rows)} songs to {OUT}")


if __name__ == "__main__":
    main()
