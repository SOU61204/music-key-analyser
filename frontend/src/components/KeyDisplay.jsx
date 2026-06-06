export default function KeyDisplay({ keyData }) {
  return (
    <div
      style={{
        position: "absolute",
        top: 20,
        left: 20,
        padding: 10,
        background: "rgba(0,0,0,0.6)",
        color: "white",
        fontSize: "24px",
        zIndex: 999
      }}
    >
      🎵Key: {keyData.key}
      <br />
      Conf: {Number(keyData.confidence).toFixed(0)}%
    </div>
  );
}