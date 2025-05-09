import { Route, Routes } from "react-router-dom";
import Adminlayout from "./layouts/Adminlayout";
import HomePage from "./pages/HomePage";
import History from "./pages/History";
import Forecast from "./pages/Forecast";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Adminlayout />}>
        <Route index element={<HomePage />} />
        <Route path="forecast" element={<Forecast />} />
        <Route path="history" element={<History />} />
      </Route>
    </Routes>
  );
}

export default App;