import numpy as np
import librosa
import sounddevice as sd
import threading
import time
from collections import Counter

# ======================
# CONFIG
# ======================
RATE = 22050
WINDOW_SECONDS = 6
HOP_SECONDS = 2

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F',
              'F#', 'G', 'G#', 'A', 'A#', 'B']

MAJOR_TEMPLATE = np.array([1,0,1,0,1,1,0,1,0,1,0,1])
MINOR_TEMPLATE = np.array([1,0,1,1,0,1,0,1,1,0,1,0])

# ======================
# SHARED BUFFER
# ======================
BUFFER_SIZE = RATE * WINDOW_SECONDS
audio_buffer = np.zeros(BUFFER_SIZE, dtype=np.float32)
buffer_lock = threading.Lock()

# ======================
# KEY DETECTION
# ======================
def detect_key_from_hist(hist):
    best_score = -1
    best_key = None
    best_scale = None

    for i in range(12):
        rotated = np.roll(hist, -i)

        major_score = np.dot(rotated, MAJOR_TEMPLATE)
        minor_score = np.dot(rotated, MINOR_TEMPLATE)

        tonic = rotated[0]
        dominant = rotated[7]
        minor_third = rotated[3]
        major_third = rotated[4]

        # Harmonic base
        major_score += tonic * 4.0 + dominant * 1.5
        minor_score += tonic * 4.0 + dominant * 1.5

        # Smart third handling
        third_total = major_third + minor_third
        if third_total > 0.05:
            major_score += (major_third / third_total) * 3.0
            minor_score += (minor_third / third_total) * 3.0
        else:
            major_score += 0.5
            minor_score += 0.5

        # Weak tonic penalty
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


# ======================
# AUDIO CALLBACK (FAST)
# ======================
def audio_callback(indata, frames, time_info, status):
    global audio_buffer

    if status:
        print(status)

    chunk = indata[:, 0]  # mono

    with buffer_lock:
        audio_buffer = np.roll(audio_buffer, -len(chunk))
        audio_buffer[-len(chunk):] = chunk


# ======================
# PROCESSING LOOP (SLOW)
# ======================
def processing_loop():
    global audio_buffer

    global_hist = np.zeros(12)
    recent_keys = []

    current_stable_key = None
    current_stable_score = 0

    while True:
        time.sleep(HOP_SECONDS)

        with buffer_lock:
            frame = audio_buffer.copy()

        # 🎯 Pitch detection
        f0 = librosa.yin(frame, fmin=80, fmax=400)
        f0 = f0[f0 > 0]

        if len(f0) < 50:
            continue

        # Stability filtering
        median_f0 = np.median(f0)
        f0 = f0[np.abs(f0 - median_f0) < median_f0 * 0.2]

        if len(f0) == 0:
            continue

        # Pitch classes
        midi = 69 + 12 * np.log2(f0 / 440)
        pitch_classes = np.round(midi) % 12

        # Histogram
        local_hist, _ = np.histogram(pitch_classes, bins=12, range=(0, 12))
        if np.sum(local_hist) == 0:
            continue
        local_hist = local_hist / np.sum(local_hist)

        # Global smoothing
        global_hist = 0.9 * global_hist + 0.1 * local_hist
        global_hist_norm = global_hist / (np.sum(global_hist) + 1e-6)

        combined_hist = 0.7 * global_hist_norm + 0.3 * local_hist

        key, confidence = detect_key_from_hist(combined_hist)
        score = confidence

        # Inertia (prevents flipping)
        if current_stable_key and key != current_stable_key:
            if score < current_stable_score * 1.15:
                key = current_stable_key
                score = current_stable_score

        print(f"DEBUG → {key} | {round(score, 2)}")

        if score < 0.15:
            continue

        # Temporal smoothing
        recent_keys.append(key)
        if len(recent_keys) > 4:
            recent_keys.pop(0)

        most_common = Counter(recent_keys).most_common(1)[0][0]

        if len(recent_keys) >= 4 and recent_keys.count(most_common) >= 3:
            if most_common != current_stable_key:
                print(f"\n🎵 Stable Key: {most_common}\n")

            current_stable_key = most_common
            current_stable_score = score


# ======================
# RUN
# ======================
if __name__ == "__main__":
    print("🎤 Starting live key detection (sounddevice)... Press Ctrl+C to stop.\n")

    stream = sd.InputStream(
        samplerate=RATE,
        channels=1,
        callback=audio_callback,
        blocksize=1024  # small = low latency
    )

    stream.start()

    try:
        processing_loop()
    except KeyboardInterrupt:
        print("\n🛑 Stopped.")
        stream.stop()
        stream.close()