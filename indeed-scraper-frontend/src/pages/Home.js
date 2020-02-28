import React, { Component } from "react";

import Checkbox from "../components/Checkbox";

class Homepage extends Component {
	state = {
		checked: [
			{ vue: false },
			{ angular: false },
			{ react: false },
			{ html: false },
			{ css: false },
			{ javascript: false },
			{ python: false },
			{ java: false },
			{ cplusplus: false },
			{ csharp: false },
			{ c: false },
			{ ruby: false },
			{ php: false },
			{ swift: false },
			{ MySQL: false },
			{ PostgreSQL: false },
			{ mongoDB: false },
			{ SQL: false },
			{ SQLite: false }
		]
	};

	handleCheckboxChange = event => {
		const langName = event.target.name;
		const checkboxState = this.state.checked;
		console.log("A:");
		console.log(checkboxState);
		for (let i = 0; i < checkboxState.length; i++) {
			// get the key of the checkbox[indexNum] object
			const checkboxKey = Object.keys(checkboxState[i])[0];
			if (checkboxKey === langName) {
				checkboxState[i][checkboxKey] = event.target.checked;
			}
		}

		this.setState({ checked: checkboxState });
		console.log("b:");
		console.log(this.state.checked);
	};

	render() {
		const dbMsg = `<Database updated every week!>`;

		// TODO: Organize list of checkboxes into a nice pattern.

		let checkboxes = [];
		for (let i = 0; i < this.state.checked.length; i++) {
			// console.log("Key:" + Object.keys(this.state.checked[i])[0]);
			let checkboxJSX = null;
			if (Object.keys(this.state.checked[i])[0] === "cplusplus") {
				checkboxJSX = (
					<div key={i}>
						<label>
							<Checkbox
								name={Object.keys(this.state.checked[i])[0]}
								checked={
									this.state.checked[
										Object.keys(this.state.checked[i])[0]
									]
								}
								onChange={this.handleCheckboxChange}
								value="C++"
							/>
						</label>
					</div>
				);
			} else if (Object.keys(this.state.checked[i])[0] === "csharp") {
				checkboxJSX = (
					<div key={i}>
						<label>
							<Checkbox
								name={Object.keys(this.state.checked[i])[0]}
								checked={
									this.state.checked[
										Object.keys(this.state.checked[i])[0]
									]
								}
								onChange={this.handleCheckboxChange}
								value="C#"
							/>
						</label>
					</div>
				);
			} else {
				checkboxJSX = (
					<div key={i}>
						<label>
							<Checkbox
								name={Object.keys(this.state.checked[i])[0]}
								checked={
									this.state.checked[
										Object.keys(this.state.checked[i])[0]
									]
								}
								onChange={this.handleCheckboxChange}
								value={Object.keys(this.state.checked[i])[0]}
							/>
						</label>
					</div>
				);
			}

			checkboxes.push(checkboxJSX);
		}
		// console.log("A:" + checkboxes);
		// console.log(this.state.checked);

		return (
			<div>
				<h1>Welcome to Market Scraper!</h1>
				<h3>Select a city & some languages to research below! </h3>
				{/* <label>
					<Checkbox
						name="vue"
						checked={this.state.checked["vue"]}
						onChange={this.handleCheckboxChange}
					/>
				</label>
				<label>
					<Checkbox
						name="angular"
						checked={this.state.checked["angular"]}
						onChange={this.handleCheckboxChange}
					/>
				</label>
				<label>
					<Checkbox
						name="php"
						checked={this.state.checked["php"]}
						onChange={this.handleCheckboxChange}
					/>
				</label> */}

				<div>{checkboxes}</div>

				<h5>{dbMsg}</h5>
			</div>
		);
	}
}

export default Homepage;
