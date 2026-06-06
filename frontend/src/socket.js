export function createSocket() {
  const socket = new WebSocket("ws://127.0.0.1:8000/ws");

  socket.onopen = () => {
    console.log("✅ WebSocket connected");
  };

  socket.onerror = (error) => {
    console.error("❌ WebSocket error:", error);
  };

  socket.onclose = () => {
    console.log("🔌 WebSocket closed");
  };

  return socket;
}