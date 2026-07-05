# 🎵 Music Key Analyser

A full-stack web application that detects the **musical key** and **tempo (BPM)** of audio files, while also providing **real-time key detection** from live microphone input using WebSockets.

---

## Features

* 🎤 Real-time microphone key detection
* 📁 Upload audio files for analysis
* 🎼 Major and Minor key recognition
* 🥁 BPM (Tempo) detection
* 📊 Confidence scoring
* 🔄 Live updates using WebSockets
* 🎹 Krumhansl-Schmuckler key estimation
* 🌐 Full-stack React + FastAPI application
* 🎧 Browser-based microphone streaming (AudioWorklet)
* 📀 Supports MP3, WAV, MP4, FLAC, M4A and more

---

# Demo Modes

## 🎤 Live Detection

The browser streams microphone audio directly to the FastAPI backend over WebSockets.

Features:

* Real-time key detection
* Voice activity detection
* Confidence-weighted temporal smoothing
* Stable predictions with rolling analysis windows

---

## 📁 File Analysis

Upload an audio file and receive:

* Musical Key
* Confidence Score
* Estimated BPM (Tempo)

Supported formats include:

* MP3
* WAV
* MP4
* M4A
* FLAC
* OGG
* Most formats supported by FFmpeg

---

# Tech Stack

## Frontend

* React
* React Router
* WebSockets
* AudioWorklet API
* MediaDevices API

## Backend

* FastAPI
* Uvicorn
* WebSockets

## Audio Processing

* Librosa
* NumPy
* FFmpeg (media normalization)

---

# How It Works

## Live Detection Pipeline

1. Browser captures microphone audio.
2. AudioWorklet streams Float32 PCM samples over WebSocket.
3. Backend maintains a per-user rolling audio buffer.
4. Voice Activity Detection filters silence and background noise.
5. Librosa extracts pitch using the YIN algorithm.
6. Pitch classes are converted into a normalized histogram.
7. Krumhansl-Schmuckler key profiles estimate the musical key.
8. Confidence-weighted temporal smoothing stabilizes predictions.
9. Results are streamed back to the frontend in near real time.

---

## File Analysis Pipeline

1. User uploads an audio/video file.
2. Media is normalized to WAV using FFmpeg.
3. Pitch extraction is performed using Librosa.
4. Musical key is estimated.
5. BPM is estimated using Librosa's beat tracking.
6. Results are returned as JSON.

---

# Project Structure

```text
music-key-analyser/
│
├── frontend/
│   ├── public/
│   │   └── audio/
│   │       └── recorder-worklet.js
│   │
│   └── src/
│       ├── audio/
│       │   └── microphone.js
│       ├── components/
|       |   ├── KeyDisplay.jsx
|       |   └── WebcamView.jsx
│       ├── Home.jsx
│       ├── Live.jsx
│       ├── Upload.jsx
│       └── socket.js
│
├── backend/
│   ├── core/
│   │   ├── audio.py
│   │   ├── bpm.py
│   │   ├── core.py
│   │   ├── media.py
│   │   └── state.py
|   |
│   ├── requirements.txt
│   └── server.py
│
└── README.md
```

---

# Installation

## Clone Repository

```bash
git clone https://github.com/SOU61204/music-key-analyser.git

cd music-key-analyser
```

---

# Backend Setup

```bash
cd backend

pip install -r requirements.txt

uvicorn server:app --reload
```

Backend runs at

```text
http://localhost:8000
```

---

# Frontend Setup

```bash
cd frontend

npm install

npm start
```

Frontend runs at

```text
http://localhost:3000
```

---

# API

## Analyze Audio

```http
POST /analyze
```

Returns

```json
{
  "key": "C# Minor",
  "confidence": 0.91,
  "bpm": 124.8
}
```

---

## Live Detection

```text
ws://localhost:8000/ws
```

Streams

```json
{
  "key": "G Minor",
  "confidence": 0.84
}
```

---

# Future Improvements

* 🎶 Raag Detection
* 🎼 Scale Identification
* 🎹 Chord Detection
* 🎵 Melody Extraction
* 📈 Pitch Visualization
* ☁️ Cloud Deployment
* 📱 Mobile-Friendly UI

---

# License

MIT License
