"""
bpm.py

Tempo estimation using Librosa.
"""

import librosa
import numpy as np


TARGET_SR = 22050


def detect_bpm(audio_path: str) -> float:
    """
    Estimate song tempo.

    Parameters
    ----------
    audio_path : str

    Returns
    -------
    float
        Estimated BPM.
    """

    y, sr = librosa.load(
        audio_path,
        sr=TARGET_SR,
        mono=True
    )

    # Remove silence
    y, _ = librosa.effects.trim(
        y,
        top_db=30
    )

    if len(y) == 0:
        return 0.0

    onset_env = librosa.onset.onset_strength(
        y=y,
        sr=sr
    )

    tempo = librosa.feature.tempo(
        onset_envelope=onset_env,
        sr=sr
    )[0]

    return round(float(tempo), 1)