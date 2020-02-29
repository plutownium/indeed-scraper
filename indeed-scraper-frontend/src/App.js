import React, { Component } from "react";
import "./App.css";

import { BrowserRouter, Route, Switch } from "react-router-dom";

import Home from "./pages/Home";
import Results from "./pages/Results";

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
			<BrowserRouter>
				<div className="App">
					<Switch>
						<Route path="/results">
							<Results data={this.state.queryValue}></Results>
						</Route>
						<Route path="/">
							<Home retrieveData={this.supplyData}></Home>
						</Route>
					</Switch>
					{test}
				</div>
			</BrowserRouter>
		);
	}
}

export default App;
