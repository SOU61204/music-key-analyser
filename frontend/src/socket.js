import MicrophoneStreamer from "./audio/microphone";

export function createSocket(onMessage) {
  // Automatically switch WebSocket protocols based on your environment
  const WS_URL = window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
    ? "ws://127.0.0.1:8000/ws"
    : "wss://sou61204-music-key-analyser-backend.hf.space/ws";

  const socket = new WebSocket(WS_URL);

  // We are sending binary Float32 PCM
  socket.binaryType = "arraybuffer";

  let microphone = null;

  socket.onopen = async () => {
    console.log("✅ WebSocket connected");

    try {
      microphone = new MicrophoneStreamer(socket);

      await microphone.start();

      console.log("🎤 Microphone streaming");
    } catch (err) {
      console.error(
        "❌ Unable to start microphone:",
        err
      );
    }
  };

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);

      if (onMessage) {
        onMessage(data);
      }
    } catch (err) {
      console.error(
        "Invalid server message",
        err
      );
    }
  };

  socket.onerror = (err) => {
    console.error(
      "❌ WebSocket Error",
      err
    );
  };

  socket.onclose = () => {
    console.log("🔌 WebSocket closed");

    if (microphone) {
      microphone.stop();
      microphone = null;
    }
  };

  return socket;
}