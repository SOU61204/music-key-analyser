import { useState } from "react";
import "./App.css";

function Upload() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/analyze",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();
      setResult(data);

    } catch (err) {
      console.error(err);
    }

    setLoading(false);
  };

  return (
    <div className="app">
      <div className="overlay">

        <h1 className="title">
          Upload Audio File
        </h1>

        <p className="subtitle">
          Analyze an audio file and detect its musical key.
        </p>

        <div className="upload-container">

          <label className="upload-card">
            <h2>📂 Choose Audio File</h2>

            {file ? (
              <p>{file.name}</p>
            ) : (
              <p>Select MP3, MP4, WAV, FLAC or M4A</p>
            )}

            <input
              type="file"
              accept=".mp3,.mp4,.wav,.flac,.m4a"
              style={{ display: "none" }}
              onChange={(e) => {
                setFile(e.target.files[0]);
                setResult(null);
              }}
            />
          </label>

          <button
            className={`upload-button ${result ? "result-mode" : ""}`}
            onClick={handleUpload}
            disabled={!file || loading}
          >
            {loading ? (
              "Analyzing..."
            ) : result ? (
              <>
                <div className="result-layout">

                  <div className="result-left">

                    <div className="result-row">
                      <span className="result-label">Key:</span>
                      <span className="result-value">{result.key}</span>
                    </div>

                    <div className="result-row">
                      <span className="result-label">Confidence:</span>
                      <span className="result-value">
                        {result.confidence?.toFixed(2)}
                      </span>
                    </div>

                  </div>

                  <div className="result-divider"></div>

                  <div className="result-right">

                    <div className="result-row">
                      <span className="result-label">BPM:</span>
                      <span className="result-value">
                        {result.bpm?.toFixed(1)}
                      </span>
                    </div>

                  </div>

                </div>
              </>
            ) : (
              "🎵 Analyze"
            )}
          </button>

        </div>

      </div>
    </div>
  );
}

export default Upload;