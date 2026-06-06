import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

import Home from "./Home";
import Live from "./Live";
import Upload from "./Upload";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/live" element={<Live />} />
        <Route path="/upload" element={<Upload />} />
      </Routes>
    </Router>
  );
}

export default App;