import React from "react";
import "./App.css";

import Home from "./pages/Home";
import Display from "./pages/Display";

// TODO: Get the db data using axios
// TODO: Parse the data into usable format
// TODO: Display the data on localhost:3000

function App() {
	return (
		<div className="App">
			<Home></Home>
			{/* <Display></Display> */}
		</div>
	);
}

export default App;
