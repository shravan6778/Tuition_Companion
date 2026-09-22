import { Route, Routes } from "react-router-dom";
import Landing from "./shared/Landing.jsx";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
    </Routes>
  );
}
