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
		console.log(event.target.name);
		// TODO: Set a unique state for every language in the languages list.
		const checkboxState = this.state.checked;
		checkboxState[event.target.name] = event.target.checked;
		this.setState({ checked: checkboxState });
	};

	render() {
		const dbMsg = `<Database updated every week!>`;

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
		console.log("A:" + checkboxes);
		console.log(this.state.checked);

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
