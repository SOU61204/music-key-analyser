import { useEffect, useRef } from "react";

export default function WebcamView() {
  const videoRef = useRef(null);
  const streamRef = useRef(null);

  useEffect(() => {
    navigator.mediaDevices
      .getUserMedia({
        video: true,
        audio: true,
      })
      .then((stream) => {
        streamRef.current = stream;

        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      })
      .catch((err) => {
        console.error("Media error:", err);
      });

    return () => {
      console.log("🛑 Stopping camera and microphone");

      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => {
          track.stop();
        });
      }
    };
  }, []);

  return (
    <div className="webcam-container">
      <video
        ref={videoRef}
        autoPlay
        playsInline
        muted
        className="webcam-video"
      />
    </div>
  );
}