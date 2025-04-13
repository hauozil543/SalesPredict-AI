
import { Route, Routes } from "react-router-dom";
import Adminlayout from "./layouts/AdminLayout";
import HomePage from "./pages/HomePage";
import History from "./pages/History";
import Forecast from "./pages/Forecast";


function App() {
	return (
		<div>
			<Routes>
			<Route path="/" element={<Adminlayout />}>
        	<Route index element={<HomePage/>} />
        	<Route path="/history" element={<History/>} />
			<Route path="/forecast" element={<Forecast/>} />
			</Route>
		</Routes>
		</div>
	);
}

export default App;
