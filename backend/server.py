from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
    UploadFile,
    File
)

from fastapi.middleware.cors import CORSMiddleware

import asyncio
import threading
import traceback
import tempfile
import os

from core.audio import (
    start_audio_stream,
    stop_audio_stream
)

from core.state import get_state
from core.core import detect_key

app = FastAPI()

# Track live users
active_connections = 0
audio_started = False

# Allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global active_connections
    global audio_started

    await websocket.accept()

    active_connections += 1

    print(
        f"✅ WebSocket connected "
        f"({active_connections} active)"
    )

    # Start audio engine on first connection
    if not audio_started:
        try:
            print("🎤 Starting audio engine...")

            threading.Thread(
                target=start_audio_stream,
                daemon=True
            ).start()

            audio_started = True

            print("✅ Audio thread launched")

        except Exception:
            print("❌ AUDIO ENGINE ERROR")
            traceback.print_exc()

    try:
        while True:
            state = get_state()

            await websocket.send_json(state)

            await asyncio.sleep(0.5)

    except WebSocketDisconnect:

        active_connections -= 1

        print(
            f"🔌 WebSocket disconnected "
            f"({active_connections} active)"
        )

        # Stop audio when nobody is using Live mode
        if active_connections <= 0:

            stop_audio_stream()

            audio_started = False

    except Exception:

        print("❌ WEBSOCKET ERROR")
        traceback.print_exc()


@app.post("/analyze")
async def analyze_audio(file: UploadFile = File(...)):
    try:
        print(f"📁 Received file: {file.filename}")

        suffix = os.path.splitext(file.filename)[1]

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as temp_file:

            content = await file.read()
            temp_file.write(content)

            temp_path = temp_file.name

        print("🎵 Running key detection...")

        key, confidence = detect_key(temp_path)

        os.remove(temp_path)

        print("✅ Analysis complete")
        print("Key:", key)
        print("Confidence:", confidence)

        return {
            "key": key,
            "confidence": confidence
        }

    except Exception as e:

        print("❌ ANALYSIS ERROR")
        traceback.print_exc()

        return {
            "error": str(e)
        }


@app.get("/")
def root():
    return {
        "status": "running"
    }