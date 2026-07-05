"""
audio.py

Per-user audio session.

Each WebSocket connection owns its own AudioSession,
so multiple users can stream simultaneously without
sharing buffers.
"""

import threading
import numpy as np

# ==========================================================
# Configuration
# ==========================================================

RATE = 22050

WINDOW_SECONDS = 15

PROCESS_WINDOW = 5

BUFFER_SIZE = RATE * WINDOW_SECONDS


# ==========================================================
# Audio Session
# ==========================================================

class AudioSession:

    def __init__(self):

        self.buffer = np.zeros(
            BUFFER_SIZE,
            dtype=np.float32
        )

        self.lock = threading.Lock()

    # ------------------------------------------------------
    # Append audio
    # ------------------------------------------------------

    def append_chunk(
        self,
        chunk: np.ndarray
    ):

        if len(chunk) == 0:
            return

        chunk = np.asarray(
            chunk,
            dtype=np.float32
        )

        with self.lock:

            n = len(chunk)

            if n >= BUFFER_SIZE:

                self.buffer[:] = chunk[-BUFFER_SIZE:]

                return

            self.buffer = np.roll(
                self.buffer,
                -n
            )

            self.buffer[-n:] = chunk

    # ------------------------------------------------------
    # Read latest audio
    # ------------------------------------------------------

    def get_recent_audio(
        self,
        seconds=PROCESS_WINDOW
    ):

        samples = int(seconds * RATE)

        with self.lock:

            return self.buffer[-samples:].copy()

    # ------------------------------------------------------
    # Voice Detection
    # ------------------------------------------------------

    @staticmethod
    def rms(audio):

        if len(audio) == 0:
            return 0.0

        return float(
            np.sqrt(
                np.mean(audio ** 2)
            )
        )

    def has_voice(
        self,
        audio,
        threshold=0.02
    ):
        """
        Voice Activity Detection.

        Uses both RMS and Zero Crossing Rate to reject
        fan noise / AC noise / hum.
        """

        rms = self.rms(audio)

        if rms < threshold:
            return False

        zcr = np.mean(
            np.abs(
                np.diff(
                    np.sign(audio)
                )
            )
        )

        if zcr < 0.01:
            return False

        return True

    # ------------------------------------------------------
    # Utilities
    # ------------------------------------------------------

    def clear(self):

        with self.lock:

            self.buffer[:] = 0

    @property
    def duration(self):

        return WINDOW_SECONDS

    @property
    def samples(self):

        return BUFFER_SIZE


# ==========================================================
# Factory
# ==========================================================

def create_session():

    return AudioSession()


# ==========================================================
# Debug
# ==========================================================

if __name__ == "__main__":

    session = create_session()

    print("Buffer Duration :", session.duration)

    print("Buffer Samples  :", session.samples)