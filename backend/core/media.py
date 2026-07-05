"""
media.py
--------

Media preprocessing utilities.

Every uploaded media file is converted into a
standard WAV file before feature extraction.

Output format
-------------
- WAV
- PCM 16-bit
- Mono
- 22050 Hz
"""

import subprocess
import tempfile
import os

import imageio_ffmpeg as imageio_ffmpeg


# Standard sample rate used throughout the project
TARGET_SAMPLE_RATE = 22050


def normalize_audio(input_path: str) -> str:
    """
    Convert any supported audio/video file into a
    temporary mono WAV file.

    Parameters
    ----------
    input_path : str
        Path to uploaded media.

    Returns
    -------
    str
        Path to normalized temporary WAV file.

    Raises
    ------
    RuntimeError
        If FFmpeg conversion fails.
    """

    if not os.path.exists(input_path):
        raise FileNotFoundError(input_path)

    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

    temp_file = tempfile.NamedTemporaryFile(
        suffix=".wav",
        delete=False
    )

    output_path = temp_file.name
    temp_file.close()

    command = [

        ffmpeg_path,

        "-y",

        "-i",
        input_path,

        "-vn",                 # ignore video stream

        "-ac",
        "1",                   # mono audio

        "-ar",
        str(TARGET_SAMPLE_RATE),

        "-sample_fmt",
        "s16",                 # PCM 16-bit

        output_path

    ]

    try:

        subprocess.run(

            command,

            stdout=subprocess.PIPE,

            stderr=subprocess.PIPE,

            check=True

        )

    except subprocess.CalledProcessError as e:

        if os.path.exists(output_path):
            os.remove(output_path)

        raise RuntimeError(
            "Failed to convert uploaded media."
        ) from e

    return output_path


def cleanup_temp_file(path: str):
    """
    Delete a temporary file safely.
    """

    try:

        if path and os.path.exists(path):
            os.remove(path)

    except Exception:
        pass


if __name__ == "__main__":

    test = "example.mp4"

    wav = normalize_audio(test)

    print("Converted to:", wav)

    cleanup_temp_file(wav)