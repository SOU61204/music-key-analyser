import { useEffect, useState } from "react";
import WebcamView from "./components/WebcamView";
import KeyDisplay from "./components/KeyDisplay";
import { createSocket } from "./socket";

function Live() {
  console.log("🔥 LIVE COMPONENT RENDERED");

  const [keyData, setKeyData] = useState({
    key: "Detecting...",
    confidence: 0,
  });

  useEffect(() => {
    const socket = createSocket();

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);

      console.log("Updating React state:", data);

      setKeyData(data);
    };

    return () => {
      console.log("🛑 Leaving Live page");

      socket.close();
    };
  }, []);

  console.log("Current state:", keyData);

  return (
    <div>
      <WebcamView />
      <KeyDisplay keyData={keyData} />
    </div>
  );
}

export default Live;