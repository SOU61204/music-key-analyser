import numpy as np
import librosa
import sounddevice as sd
import threading
import time

from core.state import update_state

RATE = 22050

WINDOW_SECONDS = 15
HOP_SECONDS = 4

BUFFER_SIZE = RATE * WINDOW_SECONDS

audio_buffer = np.zeros(
    BUFFER_SIZE,
    dtype=np.float32
)

buffer_lock = threading.Lock()

# Audio engine state
audio_stream = None
audio_running = False

NOTE_NAMES = [
    'C', 'C#', 'D', 'D#', 'E', 'F',
    'F#', 'G', 'G#', 'A', 'A#', 'B'
]

# Krumhansl-Schmuckler Profiles
KS_MAJOR = np.array([
    6.35, 2.23, 3.48, 2.33,
    4.38, 4.09, 2.52, 5.19,
    2.39, 3.66, 2.29, 2.88
])

KS_MINOR = np.array([
    6.33, 2.68, 3.52, 5.38,
    2.60, 3.53, 2.54, 4.75,
    3.98, 2.69, 3.34, 3.17
])


def detect_key_from_hist(hist):

    scores = []

    for i in range(12):

        rotated = np.roll(hist, -i)

        major_score = np.dot(
            rotated,
            KS_MAJOR
        )

        minor_score = np.dot(
            rotated,
            KS_MINOR
        )

        tonic = rotated[0]
        dominant = rotated[7]

        major_third = rotated[4]
        minor_third = rotated[3]

        # Strong tonic weighting
        major_score += tonic * 10
        major_score += dominant * 3

        minor_score += tonic * 10
        minor_score += dominant * 3

        third_total = (
            major_third +
            minor_third
        )

        if third_total > 0.05:

            major_score += (
                major_third /
                third_total
            ) * 4

            minor_score += (
                minor_third /
                third_total
            ) * 4

        if tonic < 0.08:
            major_score *= 0.75
            minor_score *= 0.75

        scores.append(
            (
                major_score,
                f"{NOTE_NAMES[i]} Major"
            )
        )

        scores.append(
            (
                minor_score,
                f"{NOTE_NAMES[i]} Minor"
            )
        )

    scores.sort(
        key=lambda x: x[0],
        reverse=True
    )

    best_score = scores[0][0]
    second_score = scores[1][0]

    best_key = scores[0][1]

    # Confidence based on score separation
    confidence = (
        (best_score - second_score)
        / (best_score + 1e-6)
    )

    confidence = np.clip(
        confidence * 100,
        0,
        100
    )

    return best_key, float(confidence)


def audio_callback(
    indata,
    frames,
    time_info,
    status
):
    global audio_buffer

    if status:
        print("Audio Status:", status)

    chunk = indata[:, 0]

    with buffer_lock:

        audio_buffer = np.roll(
            audio_buffer,
            -len(chunk)
        )

        audio_buffer[-len(chunk):] = chunk


def processing_loop():

    global audio_buffer
    global audio_running

    global_hist = np.zeros(12)

    print("🎵 Processing thread started")

    while audio_running:

        time.sleep(HOP_SECONDS)

        with buffer_lock:

            frame = audio_buffer[
                -RATE * 5:
            ].copy()

        try:

            # ----------------------------------
            # Vocal Activity Detection
            # ----------------------------------

            rms = np.sqrt(
                np.mean(frame ** 2)
            )

            print(
                f"🔊 RMS: {rms:.5f}"
            )

            if rms < 0.01:

                print(
                    "🔇 No singing detected"
                )

                continue

            f0 = librosa.yin(
                frame,
                fmin=80,
                fmax=400
            )

            f0 = f0[f0 > 0]

            print(
                f"Detected pitches: {len(f0)}"
            )

            # Ignore weak detections
            if len(f0) < 80:

                print(
                    "⚠️ Not enough vocal content"
                )

                continue

            midi = (
                69 +
                12 *
                np.log2(f0 / 440)
            )

            pitch_classes = (
                np.floor(
                    midi + 0.5
                )
            ) % 12

            local_hist, _ = np.histogram(
                pitch_classes,
                bins=12,
                range=(0, 12)
            )

            if np.sum(local_hist) == 0:

                print(
                    "⚠️ Empty histogram"
                )

                continue

            local_hist = (
                local_hist /
                np.sum(local_hist)
            )

            # Long-term memory
            global_hist = (
                0.95 * global_hist +
                0.05 * local_hist
            )

            global_hist_norm = (
                global_hist /
                (
                    np.sum(global_hist)
                    + 1e-6
                )
            )

            combined = (
                0.6 * global_hist_norm +
                0.4 * local_hist
            )

            key, confidence = (
                detect_key_from_hist(
                    combined
                )
            )

            print(
                f"🎼 Detected Key: {key}"
            )

            print(
                f"📊 Confidence: "
                f"{confidence:.1f}%"
            )

            update_state(
                key,
                confidence
            )

        except Exception as e:

            print(
                "❌ Processing Error:"
            )

            print(e)

    print(
        "🛑 Processing thread stopped"
    )


def start_audio_stream():

    global audio_stream
    global audio_running

    if audio_running:

        print(
            "⚠️ Audio engine already running"
        )

        return

    try:

        print(
            "🎤 Initializing microphone..."
        )

        audio_running = True

        audio_stream = sd.InputStream(
            samplerate=RATE,
            channels=1,
            callback=audio_callback,
            blocksize=1024
        )

        audio_stream.start()

        print(
            "✅ Microphone stream started"
        )

        threading.Thread(
            target=processing_loop,
            daemon=True
        ).start()

    except Exception as e:

        print(
            "❌ Audio Stream Error:"
        )

        print(e)


def stop_audio_stream():

    global audio_stream
    global audio_running

    print(
        "🛑 Stopping audio engine..."
    )

    audio_running = False

    if audio_stream is not None:

        audio_stream.stop()
        audio_stream.close()

        audio_stream = None

    print(
        "✅ Audio engine stopped"
    )