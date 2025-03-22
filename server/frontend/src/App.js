import LoginPanel from "./components/Login/Login"
import { Routes, Route } from "react-router-dom";
import React from "react";

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPanel />} />
    </Routes>
  );
}
export default App;
