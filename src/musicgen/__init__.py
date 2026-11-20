"""AI Music & Audio Generator — text in, melody + WAV + visuals out."""

from .song import generate_song
from .synth import render_samples, render_wav
from .text import MOODS, analyze
from .theory import SCALES
from .visualize import piano_roll_ascii, svg_piano_roll, svg_waveform, waveform_ascii

__all__ = [
    "generate_song",
    "render_samples",
    "render_wav",
    "analyze",
    "MOODS",
    "SCALES",
    "piano_roll_ascii",
    "svg_piano_roll",
    "svg_waveform",
    "waveform_ascii",
]

__version__ = "1.0.0"
