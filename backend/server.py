from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
    UploadFile,
    File
)

from fastapi.middleware.cors import CORSMiddleware

import asyncio
import numpy as np
import tempfile
import os
import traceback

from core.audio import (
    RATE,
    create_session
)

from core.core import (
    detect_key_from_audio,
    detect_key_from_frame
)

from core.media import (
    normalize_audio,
    cleanup_temp_file
)

from core.bpm import detect_bpm

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://music-key-analyser-frontend.onrender.com",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await websocket.accept()

    print("✅ Browser connected")

    session = create_session()

    last_analysis = asyncio.get_event_loop().time()

    ANALYSIS_INTERVAL = 2.0   # seconds

    last_key = "Listening..."
    last_confidence = 0.0

    try:

        while True:

            audio_bytes = await websocket.receive_bytes()

            chunk = np.frombuffer(audio_bytes, dtype=np.float32)

            session.append_chunk(chunk)

            print(f"Chunk: {len(chunk)} samples")

            now = asyncio.get_event_loop().time()

            should_analyze = (now - last_analysis >= ANALYSIS_INTERVAL)

            if should_analyze:

                last_analysis = now

                frame = session.get_recent_audio(5)

                print("Frame RMS:", session.rms(frame))
                print("Voice:", session.has_voice(frame))

                frame = session.get_recent_audio(5)

                key, confidence = last_key, last_confidence

                try:
                        voice = session.has_voice(frame)
                        print("Voice:", voice)
                        print("Running key detection...")

                        detected_key, detected_conf = detect_key_from_frame(frame)

                        if detected_key is not None:

                            key = detected_key
                            confidence = detected_conf

                            last_key = key
                            last_confidence = confidence

                except Exception:
                    traceback.print_exc()

            # 🔥 ALWAYS SEND STATE (THIS IS THE FIX)
            payload = {
                "key": last_key,
                "confidence": last_confidence,
            }

            print(">>> Sending to frontend:", payload)

            await websocket.send_json(payload)

    except WebSocketDisconnect:

        print("🔌 Browser disconnected")

        session.clear()

        del session

    except Exception as e:

        print("❌ WebSocket Error")

        traceback.print_exc()

        # Free this client's audio session
        session.clear()

        del session

        try:
            await websocket.close()
        except:
            pass

@app.post("/analyze")
async def analyze_audio(
    file: UploadFile = File(...)
):
    temp_path = None
    wav_path = None

    try:

        suffix = os.path.splitext(
            file.filename
        )[1]

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as temp:

            temp.write(
                await file.read()
            )

            temp_path = temp.name

        # --------------------------------------
        # Normalize uploaded media
        # Supports:
        # mp3, wav, mp4, m4a, flac, ogg, ...
        # --------------------------------------

        wav_path = normalize_audio(
            temp_path
        )

        # --------------------------------------
        # Run key detection on normalized WAV
        # --------------------------------------

        key, confidence = detect_key_from_audio(
            wav_path
        )

        bpm = detect_bpm(
            wav_path
        )

        return {

            "key": key,

            "confidence": confidence,

            "bpm": bpm

        }

    except Exception as e:

        traceback.print_exc()

        return {

            "error": str(e)

        }

    finally:

        cleanup_temp_file(temp_path)

        cleanup_temp_file(wav_path)


@app.get("/")
def root():

    return {

        "status": "running"

    }