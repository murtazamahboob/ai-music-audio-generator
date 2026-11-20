"""Audio visualisation: ASCII and SVG waveform + piano-roll views.

No image libraries — the SVG is hand-built text, and the ASCII views
work in any terminal, so a song can be *seen* as well as heard.
"""

from __future__ import annotations

from .song import Song
from .theory import note_name


def waveform_ascii(samples: list[float], width: int = 60, height: int = 10) -> str:
    """Downsampled waveform: one column per bucket, '#' marks the range."""
    if not samples:
        return ""
    if width <= 0 or height <= 0:
        raise ValueError("width and height must be positive")
    bucket = max(1, len(samples) // width)
    rows: list[str] = []
    for row in range(height):
        line = ""
        for col in range(width):
            chunk = samples[col * bucket:(col + 1) * bucket] or [0.0]
            lo, hi = min(chunk), max(chunk)
            # Row covers amplitudes [top, bottom] top-down.
            top = 1.0 - 2.0 * row / height
            bottom = 1.0 - 2.0 * (row + 1) / height
            line += "#" if lo <= top and hi >= bottom else " "
        rows.append(line.rstrip())
    return "\n".join(rows)


def piano_roll_ascii(song: Song, width: int = 60) -> str:
    """Piano roll: one row per pitch present, '#' where a note sounds."""
    if not song.notes:
        return ""
    midis = sorted({n.midi for n in song.notes}, reverse=True)
    total = song.total_beats or 1.0
    lines: list[str] = []
    for midi in midis:
        row = ""
        for col in range(width):
            beat = total * col / width
            on = any(n.midi == midi and n.start_beat <= beat < n.start_beat + n.duration_beats
                     for n in song.notes)
            row += "#" if on else "."
        lines.append(f"{note_name(midi):>4} |{row}|")
    return "\n".join(lines)


def svg_waveform(samples: list[float], width: int = 800, height: int = 200) -> str:
    """SVG polyline of the waveform, downsampled to one point per pixel."""
    if not samples:
        return '<svg xmlns="http://www.w3.org/2000/svg"></svg>'
    step = max(1, len(samples) // width)
    points = []
    for x in range(width):
        chunk = samples[x * step:(x + 1) * step] or [0.0]
        value = sum(chunk) / len(chunk)
        y = height / 2 - value * (height / 2 - 4)
        points.append(f"{x},{y:.1f}")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
        f'<rect width="{width}" height="{height}" fill="#111827"/>'
        f'<line x1="0" y1="{height // 2}" x2="{width}" y2="{height // 2}" stroke="#374151"/>'
        f'<polyline points="{" ".join(points)}" fill="none" stroke="#22d3ee" stroke-width="1.5"/>'
        f"</svg>"
    )


def svg_piano_roll(song: Song, width: int = 800, height: int = 240) -> str:
    """SVG piano roll: one rectangle per note, pitch on the vertical axis."""
    if not song.notes:
        return '<svg xmlns="http://www.w3.org/2000/svg"></svg>'
    midis = [n.midi for n in song.notes]
    lo, hi = min(midis), max(midis)
    span = max(1, hi - lo + 1)
    total = song.total_beats or 1.0
    rects = []
    for note in song.notes:
        x = note.start_beat / total * width
        w = max(2.0, note.duration_beats / total * width)
        y = (hi - note.midi) / span * height
        h = max(4.0, height / span - 2)
        rects.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'fill="#a78bfa" rx="2"><title>{note_name(note.midi)}</title></rect>'
        )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
        f'<rect width="{width}" height="{height}" fill="#111827"/>'
        + "".join(rects)
        + "</svg>"
    )
