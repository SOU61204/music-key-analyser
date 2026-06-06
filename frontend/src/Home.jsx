import "./App.css";
import { useNavigate } from "react-router-dom";

function Home() {
  const navigate = useNavigate();

  return (
    <div className="app">
      <div className="overlay">

        <h1 className="title">
          AI - Powered Music Key Detection
        </h1>

        <p className="subtitle">
          Identify the key in which you're singing...live, as you perform.
        </p>

        <div className="card-container">

          <div className="card" onClick={() => navigate("/live")}>
            <h2>🎤</h2>
            <h2>Sing in Real Time</h2>
            <p>Real time key detection from live vocals</p>
          </div>

          <div className="card" onClick={() => navigate("/upload")}>
            <h2>📂</h2>
            <h2>Upload Your Music</h2>
            <p>Key detection from audio processing</p>
          </div>

        </div>

      </div>
    </div>
  );
}

export default Home;