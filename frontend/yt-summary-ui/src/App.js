import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import SummaryView from "./SummaryView";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/view" element={<SummaryView />} />
        {/* Other routes if needed */}
      </Routes>
    </Router>
  );
}

export default App;
