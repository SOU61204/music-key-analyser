from threading import Lock

state = {
    "key": "Detecting...",
    "confidence": 0.0
}

lock = Lock()

def update_state(key, confidence):
    with lock:
        state["key"] = key
        state["confidence"] = confidence

def get_state():
    with lock:
        return dict(state)