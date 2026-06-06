import numpy as np
import librosa
import sounddevice as sd
import threading
import time
import cv2
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
# SHARED STATE
# ======================
BUFFER_SIZE = RATE * WINDOW_SECONDS
audio_buffer = np.zeros(BUFFER_SIZE, dtype=np.float32)

buffer_lock = threading.Lock()
key_lock = threading.Lock()

current_display_key = "Detecting..."
current_confidence = 0.0

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

        # Base harmonic scoring
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
# AUDIO CALLBACK
# ======================
def audio_callback(indata, frames, time_info, status):
    global audio_buffer

    chunk = indata[:, 0]

    with buffer_lock:
        audio_buffer = np.roll(audio_buffer, -len(chunk))
        audio_buffer[-len(chunk):] = chunk


# ======================
# PROCESSING THREAD
# ======================
def processing_loop():
    global audio_buffer, current_display_key, current_confidence

    global_hist = np.zeros(12)
    recent_keys = []

    stable_key = None
    stable_score = 0

    while True:
        time.sleep(HOP_SECONDS)

        with buffer_lock:
            frame = audio_buffer.copy()

        # Pitch detection
        f0 = librosa.yin(frame, fmin=80, fmax=400)
        f0 = f0[f0 > 0]

        if len(f0) < 50:
            continue

        # Stability filter
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

        # Faster adaptation (IMPORTANT for live switching)
        global_hist = 0.7 * global_hist + 0.3 * local_hist
        global_hist_norm = global_hist / (np.sum(global_hist) + 1e-6)

        combined_hist = 0.6 * global_hist_norm + 0.4 * local_hist

        key, confidence = detect_key_from_hist(combined_hist)
        score = confidence

        # Inertia
        if stable_key and key != stable_key:
            if score < stable_score * 1.1:
                key = stable_key
                score = stable_score

        print(f"DEBUG → {key} | {round(score, 2)}")

        if score < 0.15:
            continue

        recent_keys.append(key)
        if len(recent_keys) > 4:
            recent_keys.pop(0)

        most_common = Counter(recent_keys).most_common(1)[0][0]

        if len(recent_keys) >= 4 and recent_keys.count(most_common) >= 3:
            stable_key = most_common
            stable_score = score

            # 🔥 UPDATE UI STATE
            with key_lock:
                current_display_key = stable_key
                current_confidence = score


# ======================
# WEBCAM LOOP
# ======================
def webcam_loop():
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Flip for mirror view
        frame = cv2.flip(frame, 1)

        # Get key safely
        with key_lock:
            key = current_display_key
            conf = current_confidence

        # Draw UI panel
        cv2.rectangle(frame, (20, 20), (420, 120), (0, 0, 0), -1)

        # Draw text
        cv2.putText(frame, f"Key: {key}",
                    (40, 70),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.2, (0, 255, 0), 3)

        cv2.putText(frame, f"Conf: {round(conf,2)}",
                    (40, 105),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (200, 200, 200), 2)

        cv2.imshow("Live Key Detection", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


# ======================
# MAIN
# ======================
if __name__ == "__main__":
    print("🎤 + 📷 Live Key Detection Started (ESC to quit)\n")

    # Start audio stream
    stream = sd.InputStream(
        samplerate=RATE,
        channels=1,
        callback=audio_callback,
        blocksize=1024
    )
    stream.start()

    # Start processing thread
    threading.Thread(target=processing_loop, daemon=True).start()

    # Run webcam UI (main thread)
    webcam_loop()

    stream.stop()
    stream.close()