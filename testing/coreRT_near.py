import librosa
import numpy as np
from collections import Counter

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F',
              'F#', 'G', 'G#', 'A', 'A#', 'B']

MAJOR_TEMPLATE = np.array([1, 0, 1, 0, 1, 1, 0,
                           1, 0, 1, 0, 1])

MINOR_TEMPLATE = np.array([1, 0, 1, 1, 0, 1, 0,
                           1, 1, 0, 1, 0])


def detect_key_from_hist(hist):
    best_score = -1
    best_key = None
    best_scale = None

    for i in range(12):
        rotated = np.roll(hist, -i)

        # 🎯 Base score
        major_score = np.dot(rotated, MAJOR_TEMPLATE)
        minor_score = np.dot(rotated, MINOR_TEMPLATE)

        # 🎯 Strong tonic emphasis
        tonic = rotated[0]
        dominant = rotated[7]   # 5th
        minor_third = rotated[3]

        major_score += tonic * 3.5 + dominant * 1.5
        minor_score += tonic * 4.5 + dominant * 1.5 + minor_third * 1.5

        # ⚠️ Penalize weak tonic
        if tonic < 0.08:
            major_score *= 0.7
            minor_score *= 0.7

        # Slight bias toward minor (helps A# minor vs C# major)
        minor_score *= 1.05

        if major_score > best_score:
            best_score = major_score
            best_key = NOTE_NAMES[i]
            best_scale = "Major"

        if minor_score > best_score:
            best_score = minor_score
            best_key = NOTE_NAMES[i]
            best_scale = "Minor"

    confidence = best_score / (np.sum(hist) + 1e-6)
    return f"{best_key} {best_scale}", confidence


def realtime_simulation(file_path):
    y, sr = librosa.load(file_path)

    frame_size = int(sr * 8)   # ~8 sec window
    hop_size = int(sr * 2)     # update every 2 sec

    recent_keys = []

    for i in range(0, len(y), hop_size):
        frame = y[i:i+frame_size]

        if len(frame) < frame_size:
            continue

        # Pitch extraction
        f0 = librosa.yin(frame, fmin=80, fmax=400)
        f0 = f0[f0 > 0]

        if len(f0) == 0:
            continue

        # Convert to pitch classes
        midi = 69 + 12 * np.log2(f0 / 440)
        pitch_classes = np.round(midi) % 12

        # Histogram
        hist, _ = np.histogram(pitch_classes, bins=12, range=(0, 12))
        hist = hist / np.sum(hist)

        key, confidence = detect_key_from_hist(hist)

        print(f"DEBUG → {key} | {round(confidence, 2)}")

        if confidence < 0.15:
            continue

        # 🧠 Smooth output
        recent_keys.append(key)
        if len(recent_keys) > 3:
            recent_keys.pop(0)

        most_common = Counter(recent_keys).most_common(1)[0][0]

        if len(recent_keys) == 3 and recent_keys.count(most_common) >= 2:
            print(f"Stable Key: {most_common}")


if __name__ == "__main__":
    file_path = input("Enter path to audio file: ")
    realtime_simulation(file_path)