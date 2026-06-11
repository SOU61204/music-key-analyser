# 🎵 Music Key Analyser

A real-time music key detection web application that analyzes uploaded audio files or live microphone input and predicts the musical key being sung or played.

## Features

* 🎤 Real-time microphone key detection
* 📁 Audio file upload and analysis
* 🎼 Major and Minor key recognition
* 📊 Confidence scoring
* 🔄 Live updates through WebSockets
* 🎹 Krumhansl-Schmuckler based key estimation
* 🌐 Full-stack web interface

---

## Demo Modes

### Live Detection

Uses the system microphone and continuously analyzes incoming audio to estimate the current musical key.

### File Analysis

Upload an audio file and receive:

* Detected Key
* Confidence Score

---

## Tech Stack

### Frontend

* React
* React Router
* WebSockets
* Axios

### Backend

* FastAPI
* Uvicorn
* WebSockets

### Audio Processing

* Librosa
* NumPy
* SoundDevice

---

## How It Works

### 1. Audio Capture

Audio is captured either from:

* Microphone input (Live Mode)
* Uploaded audio files

### 2. Pitch Extraction

The application uses Librosa's YIN pitch detection algorithm to estimate the fundamental frequency (F0) of the audio signal.

### 3. Pitch Class Mapping

Detected frequencies are converted into MIDI notes and then mapped to one of the 12 pitch classes:

C, C#, D, D#, E, F, F#, G, G#, A, A#, B

### 4. Histogram Generation

A normalized pitch-class histogram is created from the detected notes.

### 5. Key Detection

The histogram is compared against Krumhansl-Schmuckler key profiles for all major and minor keys.

The key with the highest score is selected as the predicted key.

### 6. Live Updates

The backend streams detection results to the frontend using WebSockets for near real-time feedback.

---

## Project Structure

```text
music-key-detection/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── Home.jsx
│   │   ├── Live.jsx
│   │   ├── Upload.jsx
│   │   └── socket.js
│   │
│   └── public/
│
├── backend/
│   ├── core/
│   │   ├── audio.py
│   │   ├── core.py
│   │   └── state.py
│   │
│   ├── requirements.txt
│   └── server.py
│
└── README.md
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/SOU61204/music-key-analyser.git
cd music-key-analyser
```

---

## Backend Setup

```bash
cd backend

pip install -r requirements.txt

uvicorn server:app --reload
```

Backend runs on:

```text
http://localhost:8000
```

---

## Frontend Setup

```bash
cd frontend

npm install

npm start
```

Frontend runs on:

```text
http://localhost:3000
```

---

## API Endpoints

### Analyze Uploaded Audio

```http
POST /analyze
```

Returns:

```json
{
  "key": "C# Minor",
  "confidence": 0.91
}
```

---

### Live WebSocket

```text
ws://localhost:8000/ws
```

Streams:

```json
{
  "key": "C# Minor",
  "confidence": 0.91
}
```

---

## Future Improvements

* 🎶 Raag Detection
* 🎼 Scale Identification
* 📈 Pitch Visualization
* 🎤 Vocal Activity Detection
* ☁️ Cloud Deployment

---

## License

MIT License

```
```
