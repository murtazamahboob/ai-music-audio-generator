"""Command line: ``musicgen "golden morning, dancing light" --out song.wav``."""

from __future__ import annotations

import argparse
import json
import sys

from .song import generate_song
from .synth import render_samples, render_wav
from .text import MOODS
from .theory import SCALES
from .visualize import piano_roll_ascii, svg_piano_roll, svg_waveform, waveform_ascii


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="musicgen",
        description="Turn text into an original melody: WAV audio plus waveform and piano-roll visuals. Fully offline, stdlib only.",
    )
    parser.add_argument("text", nargs="?", help="text to turn into music")
    parser.add_argument("--mood", choices=list(MOODS), help="override the detected mood")
    parser.add_argument("--tempo", type=int, help="tempo in BPM (overrides the mood default)")
    parser.add_argument("--key", help="musical key, e.g. C, F#, Bb (overrides the text-derived key)")
    parser.add_argument("--scale", choices=sorted(SCALES), help="scale (overrides the mood default)")
    parser.add_argument("--seed", type=int, help="accepted for reproducibility; the melody is a pure function of the text")
    parser.add_argument("--title", help="song title")
    parser.add_argument("--out", default="song.wav", help="WAV output path (default: song.wav)")
    parser.add_argument("--svg", help="write an SVG piano roll to this path")
    parser.add_argument("--wave-svg", help="write an SVG waveform to this path")
    parser.add_argument("--report", help="write a JSON summary to this path")
    parser.add_argument("--list-scales", action="store_true", help="list the scales and exit")
    parser.add_argument("--list-moods", action="store_true", help="list the moods and exit")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.list_scales:
        print(" ".join(sorted(SCALES)))
        return 0
    if args.list_moods:
        print(" ".join(MOODS))
        return 0
    if not args.text or not args.text.strip():
        print("musicgen: error: provide text to turn into music", file=sys.stderr)
        return 2
    try:
        song = generate_song(
            args.text, title=args.title, mood=args.mood,
            tempo_bpm=args.tempo, key=args.key, scale=args.scale, seed=args.seed,
        )
    except ValueError as exc:
        print(f"musicgen: error: {exc}", file=sys.stderr)
        return 2

    render_wav(song, args.out)
    samples = render_samples(song)
    if args.svg:
        with open(args.svg, "w", encoding="utf-8") as fh:
            fh.write(svg_piano_roll(song))
    if args.wave_svg:
        with open(args.wave_svg, "w", encoding="utf-8") as fh:
            fh.write(svg_waveform(samples))
    summary = song.summary()
    summary["wav"] = args.out
    if args.report:
        with open(args.report, "w", encoding="utf-8") as fh:
            json.dump(summary, fh, indent=2)
    print(f"{song.title} — {song.mood}, {song.key} {song.scale}, {song.tempo_bpm} BPM, "
          f"{summary['notes']} notes, {summary['bars']} bars, {summary['duration_seconds']}s -> {args.out}")
    print(waveform_ascii(samples))
    print(piano_roll_ascii(song))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
