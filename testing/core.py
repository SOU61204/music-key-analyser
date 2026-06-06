import librosa
import numpy as np

# Note names
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F',
              'F#', 'G', 'G#', 'A', 'A#', 'B']

# Scale templates (1 = note present, 0 = absent)
MAJOR_TEMPLATE = np.array([1, 0, 1, 0, 1, 1, 0,
                           1, 0, 1, 0, 1])

MINOR_TEMPLATE = np.array([1, 0, 1, 1, 0, 1, 0,
                           1, 1, 0, 1, 0])


def extract_pitch(y, sr):
    """Extract pitch using librosa YIN"""
    f0 = librosa.yin(y, fmin=80, fmax=400)
    
    # Remove unvoiced / invalid values
    f0 = f0[f0 > 0]
    
    return f0


def freq_to_pitch_class(frequencies):
    """Convert frequency (Hz) → pitch class (0–11)"""
    midi = 69 + 12 * np.log2(frequencies / 440.0)
    pitch_classes = np.round(midi) % 12
    return pitch_classes.astype(int)


def build_histogram(pitch_classes):
    """Build normalized histogram of pitch classes"""
    hist, _ = np.histogram(pitch_classes, bins=12, range=(0, 12))
    
    if np.sum(hist) == 0:
        return hist
    
    return hist / np.sum(hist)


def rotate_histogram(hist, steps):
    """Rotate histogram for trying different roots"""
    return np.roll(hist, -steps)


def compute_score(hist, template):
    """Compute similarity score"""
    return np.dot(hist, template)


def detect_key(file_path):
    # Step 1: Load audio
    y, sr = librosa.load(file_path)

    # Step 2: Extract pitch
    f0 = extract_pitch(y, sr)

    if len(f0) == 0:
        return "No pitch detected", 0.0

    # Step 3: Convert to pitch classes
    pitch_classes = freq_to_pitch_class(f0)

    # Step 4: Build histogram
    hist = build_histogram(pitch_classes)

    best_score = -1
    best_key = None
    best_scale = None

    # Step 5: Try all 12 roots
    for i in range(12):
        rotated = rotate_histogram(hist, i)

        major_score = compute_score(rotated, MAJOR_TEMPLATE)
        minor_score = compute_score(rotated, MINOR_TEMPLATE)

        if major_score > best_score:
            best_score = major_score
            best_key = NOTE_NAMES[i]
            best_scale = "Major"

        if minor_score > best_score:
            best_score = minor_score
            best_key = NOTE_NAMES[i]
            best_scale = "Minor"

    # Normalize confidence (rough)
    confidence = float(best_score / np.sum(hist))

    return f"{best_key} {best_scale}", confidence


if __name__ == "__main__":
    file_path = input("Enter path to audio file: ")
    
    key, confidence = detect_key(file_path)
    
    print("\n🎵 Result:")
    print("Detected Key:", key)
    print("Confidence:", round(confidence, 3))