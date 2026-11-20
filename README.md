# AI Music & Audio Generator — Text to Melody, WAV & Visuals

Turn plain text into an **original song**: type a sentence, get a melody, a
playable WAV file, and waveform + piano-roll visuals. No model, no API key,
no network — everything runs offline in pure standard-library Python.

## Why this is different

- **Text-to-melody, not text-to-audio black box.** The mood, tempo, scale,
  key and every note are derived transparently from your words: happy words
  → major scale at 120 BPM, sad words → minor at 72 BPM, calm words →
  pentatonic at 88 BPM, energetic words → dorian at 140 BPM.
- **Deterministic.** The same text always produces the same song —
  byte-identical WAV files — so results are reproducible and testable.
- **See the music.** Every song ships with an ASCII waveform and piano roll
  in the terminal, plus SVG waveform and piano-roll files you can open in a
  browser.
- **Real audio, from scratch.** Melody (sine + harmonics, ADSR envelope),
  chord pads and a bass line are synthesised into a 16-bit WAV file with
  nothing but `wave`, `math` and `struct`.

## Quickstart

```bash
pip install -e .
musicgen "golden morning sunshine dancing light" --out sunrise.wav --svg sunrise.svg
```

Or run the demo (three moods, three songs):

```bash
python examples/demo.py
# outputs/sunrise.wav, outputs/rain.wav, outputs/storm.wav + SVGs + summary.json
```

## How text becomes music

| Step | Rule |
| --- | --- |
| Mood | Word lists per mood (joy/sun/dance → happy; rain/lonely/tears → sad; …). No match → calm. |
| Tempo & scale | Happy 120 BPM major · Sad 72 BPM minor · Calm 88 BPM pentatonic · Energetic 140 BPM dorian |
| Key | Derived from the SHA-256 of the text, so a text keeps its key |
| Melody | One note per word, walking stepwise through the scale; word length sets note length |
| Rests | Commas pause half a beat, full stops a full beat |
| Harmony | One chord per bar from a mood progression (pop / sad / calm / drive), bass on the root |

Short texts (under 8 words) are repeated an octave lower so every song has
enough material to hear and see.

## CLI

```bash
musicgen "lonely rain at night, tears and goodbye" --out rain.wav --svg rain.svg --wave-svg rain-wave.svg --report rain.json
musicgen "fire and thunder run fast" --mood energetic --tempo 150 --key D --scale blues
musicgen --list-scales   # major minor pentatonic dorian phrygian blues
musicgen --list-moods    # happy sad calm energetic
```

## Library

```python
from musicgen import generate_song, render_wav
from musicgen.visualize import svg_piano_roll

song = generate_song("golden morning sunshine dancing light")
print(song.summary())
# {'mood': 'happy', 'tempo_bpm': 120, 'key': '...', 'scale': 'major', 'notes': 10, ...}
render_wav(song, "sunrise.wav")
open("sunrise.svg", "w").write(svg_piano_roll(song))
```

## Demo results

| Song | Mood | Tempo | Notes | Duration |
| --- | --- | --- | --- | --- |
| sunrise | happy | 120 BPM | 9 | 5.25 s |
| rain | sad | 72 BPM | 11 | 8.33 s |
| storm | energetic | 140 BPM | 10 | 4.93 s |

(Reproduced by `python examples/demo.py`; durations depend on word lengths and rests.)

## Project layout

```
src/musicgen/
  theory.py     notes, scales, chords, progressions
  text.py       mood / tempo / key / seed from text
  song.py       melody, chords, bass line
  synth.py      offline WAV synthesis (ADSR, harmonics)
  visualize.py  ASCII + SVG waveform and piano roll
  cli.py        musicgen command
examples/demo.py
tests/          60 tests — theory, text, song, synth, visuals, CLI
```

## Tests

```bash
python -m pytest -q   # 60 tests, all offline
```

## Keywords

AI music generator, text-to-music, text-to-melody, generative music, WAV
synthesis, audio visualisation, piano roll, waveform, music theory, Python,
offline AI, creative coding, procedural music.
