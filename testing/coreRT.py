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

        major_score = np.dot(rotated, MAJOR_TEMPLATE)
        minor_score = np.dot(rotated, MINOR_TEMPLATE)

        # 🎯 Core features
        tonic = rotated[0]
        dominant = rotated[7]
        minor_third = rotated[3]
        major_third = rotated[4]

        # Base harmonic structure
        major_score += tonic * 4.0 + dominant * 1.5
        minor_score += tonic * 4.0 + dominant * 1.5

        # 🎯 SMART third handling (relative, not absolute)
        third_total = major_third + minor_third

        if third_total > 0.05:
            major_score += (major_third / third_total) * 3.0
            minor_score += (minor_third / third_total) * 3.0
        else:
            # ambiguous → stay neutral
            major_score += 0.5
            minor_score += 0.5

        # Penalize weak tonic
        if tonic < 0.08:
            major_score *= 0.75
            minor_score *= 0.75

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

    global_hist = np.zeros(12)
    recent_keys = []

    current_stable_key = None
    current_stable_score = 0

    for i in range(0, len(y), hop_size):
        frame = y[i:i+frame_size]

        if len(frame) < frame_size:
            continue

        # 🎯 Pitch extraction
        f0 = librosa.yin(frame, fmin=80, fmax=400)

        # Remove invalid
        f0 = f0[f0 > 0]

        # ❗ Require enough data
        if len(f0) < 50:
            continue

        # 🎯 Stability filtering (VERY IMPORTANT)
        median_f0 = np.median(f0)
        f0 = f0[np.abs(f0 - median_f0) < median_f0 * 0.2]

        if len(f0) == 0:
            continue

        # Convert to pitch classes
        midi = 69 + 12 * np.log2(f0 / 440)
        pitch_classes = np.round(midi) % 12

        # Local histogram
        local_hist, _ = np.histogram(pitch_classes, bins=12, range=(0, 12))
        if np.sum(local_hist) == 0:
            continue
        local_hist = local_hist / np.sum(local_hist)

        # 🧠 Exponential smoothing
        global_hist = 0.9 * global_hist + 0.1 * local_hist
        global_hist_norm = global_hist / (np.sum(global_hist) + 1e-6)

        # 🎯 Combine global + local
        combined_hist = 0.7 * global_hist_norm + 0.3 * local_hist

        key, confidence = detect_key_from_hist(combined_hist)
        score = confidence

        # 🧠 INERTIA (prevents flipping)
        if current_stable_key is not None and key != current_stable_key:
            if score < current_stable_score * 1.15:
                key = current_stable_key
                score = current_stable_score

        print(f"DEBUG → {key} | {round(score, 2)}")

        if score < 0.15:
            continue

        # 🧠 Temporal smoothing
        recent_keys.append(key)
        if len(recent_keys) > 4:
            recent_keys.pop(0)

        most_common = Counter(recent_keys).most_common(1)[0][0]

        # 🎯 Stable decision
        if len(recent_keys) >= 4 and recent_keys.count(most_common) >= 3:
            if most_common != current_stable_key:
                print(f"Stable Key: {most_common}")

            current_stable_key = most_common
            current_stable_score = score


if __name__ == "__main__":
    file_path = input("Enter path to audio file: ")
    realtime_simulation(file_path)