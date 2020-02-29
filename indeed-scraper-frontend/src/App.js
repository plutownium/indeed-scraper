import React, { Component } from "react";
import "./App.css";

import Home from "./pages/Home";
import Results from "./pages/Results";

// TODO: Install Router
// TODO: When user clicks e.g. Vancouver from dropdown list, change Router display to Results page
// TODO: When router changes display to Results page, fwd state data from App

class App extends Component {
	state = {
		queryValue: null
	};

	supplyData = data => {
		this.setState({ queryValue: data });
	};

	render() {
		let test = "";
		if (this.state.queryValue) {
			test = Object.values(this.state.queryValue).join("");
		}
		return (
			<div className="App">
				<Home retrieveData={this.supplyData}></Home>
				{/* <Results></Results> */}
				{test}
			</div>
		);
	}
}

export default App;
