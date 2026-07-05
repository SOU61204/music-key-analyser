import librosa
import numpy as np

# ==========================================================
# Constants
# ==========================================================

RATE = 22050

NOTE_NAMES = [
    "C","C#","D","D#","E","F",
    "F#","G","G#","A","A#","B"
]

# Krumhansl-Schmuckler Profiles

KS_MAJOR = np.array([
    6.35,2.23,3.48,2.33,
    4.38,4.09,2.52,5.19,
    2.39,3.66,2.29,2.88
])

KS_MINOR = np.array([
    6.33,2.68,3.52,5.38,
    2.60,3.53,2.54,4.75,
    3.98,2.69,3.34,3.17
])

# ==========================================================
# Feature Extraction
# ==========================================================

def extract_pitch(audio):

    f0 = librosa.yin(
        audio,
        fmin=80,
        fmax=400
    )

    return f0[f0 > 0]


def pitch_classes(f0):

    midi = (
        69 +
        12 * np.log2(f0 / 440)
    )

    return (
        np.floor(midi + 0.5).astype(int)
    ) % 12


def pitch_histogram(pc):

    hist, _ = np.histogram(
        pc,
        bins=12,
        range=(0,12)
    )

    if np.sum(hist)==0:
        return hist

    return hist / np.sum(hist)

# ==========================================================
# Krumhansl-Schmuckler
# ==========================================================

def detect_key_from_hist(hist):

    scores = []

    for i in range(12):

        rotated = np.roll(hist,-i)

        major = np.dot(
            rotated,
            KS_MAJOR
        )

        minor = np.dot(
            rotated,
            KS_MINOR
        )

        scores.append(
            (
                major,
                f"{NOTE_NAMES[i]} Major"
            )
        )

        scores.append(
            (
                minor,
                f"{NOTE_NAMES[i]} Minor"
            )
        )

    scores.sort(
        reverse=True,
        key=lambda x:x[0]
    )

    best = scores[0]
    second = scores[1]

    confidence = (
        (best[0]-second[0])
        /
        (best[0]+1e-6)
    )

    confidence = float(

        np.clip(

            confidence*100,

            0,

            100

        )

    )

    return best[1], confidence

# ==========================================================
# Live Audio
# ==========================================================

def detect_key_from_frame(audio):

    rms = np.sqrt(np.mean(audio ** 2))

    if rms < 0.01:
        return "Listening...", 0.0

    f0 = extract_pitch(audio)

    voiced = f0[f0 > 0]

    MIN_VOICED_FRAMES = 80

    if len(voiced) < MIN_VOICED_FRAMES:
        return "Listening...", 0.0
    
    median_pitch = np.median(voiced)

    if median_pitch < 80:
        return "Listening...", 0.0

    if median_pitch > 600:
        return "Listening...", 0.0
    
    pitch_std = np.std(voiced)

    if pitch_std < 1.5:
        return "Listening...", 0.0

    if len(f0) < 50:

        return (
            "Listening...",
            0.0
        )

    pc = pitch_classes(f0)

    hist = pitch_histogram(pc)

    return detect_key_from_hist(hist)

# ==========================================================
# Uploaded File
# ==========================================================

def detect_key_from_audio(path):

    audio, _ = librosa.load(
        path,
        sr=RATE,
        mono=True
    )

    return detect_key_from_frame(audio)