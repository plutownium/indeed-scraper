import React, { Component } from "react";

import Checkbox from "../components/Checkbox";

import { Form } from "react-bootstrap";

import "./home.css";

class Homepage extends Component {
	state = {
		// TODO: Should these have unique ids?
		checked: [
			{ vue: false, category: "framework" },
			{ angular: false, category: "framework" },
			{ react: false, category: "framework" },
			{ html: false, category: "frontend" },
			{ css: false, category: "frontend" },
			{ javascript: false, category: "frontend" },
			{ python: false, category: "backend" },
			// { java: false },
			// { cplusplus: false },
			// { csharp: false },
			// { c: false },
			// { ruby: false },
			// { php: false },
			// { swift: false },
			// { MySQL: false },
			// { PostgreSQL: false },
			// { mongoDB: false },
			// { SQL: false },
			{ SQLite: false, category: "database" }
		]
	};

	handleCheckboxChange = event => {
		// begin by setting langName to event.target.name to clear up confusion
		const langName = event.target.name;
		// create an immutable copy of this.state.checked
		const checkboxState = [...this.state.checked];

		// iterate over checkboxState looking for the object I want to update
		for (let i = 0; i < checkboxState.length; i++) {
			// get the key of the checkbox[indexNum] object to test whether it is the object matching langName
			const checkboxKey = Object.keys(checkboxState[i])[0];
			if (checkboxKey === langName) {
				// when the right object is found, select it from the list, enter its key, and set it to event.target.checked
				checkboxState[i][checkboxKey] = event.target.checked;
			}
		}
		this.setState({ checked: checkboxState });
	};

	render() {
		const dbMsg = `<Database updated every week!>`;

		// TODO: Organize list of checkboxes into a nice pattern.
		// TODO: Add a dropdown menu with "Vancouer, Toronto, Seattle, Silicon Valley, NYC"

		let checkboxes = [];
		for (let i = 0; i < this.state.checked.length; i++) {
			let checkboxJSX = null;
			const key = Object.keys(this.state.checked[i])[0];
			if (Object.keys(this.state.checked[i])[0] === "cplusplus") {
				checkboxJSX = (
					<div key={i}>
						<label>
							<Checkbox
								name={Object.keys(this.state.checked[i])[0]}
								checked={this.state.checked[i][key]}
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
								checked={this.state.checked[i][key]}
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
								checked={this.state.checked[i][key]}
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

				<Form>
					<Form.Label className="formLabel">
						Frontend Frameworks
					</Form.Label>
					{this.state.checked.map((obj, index) => {
						let box = null;
						if (obj.category === "framework") {
							box = (
								<Form.Check
									inline
									label={Object.keys(obj)[0]} // returns values like "vue", "react", "python"
									type={"checkbox"}
									id={index}
								/>
							);
						}
						return box;
					})}
				</Form>
				<Form>
					<Form.Label className="formLabel">Frontend</Form.Label>
					{this.state.checked.map((obj, index) => {
						let box = null;
						if (obj.category === "frontend") {
							box = (
								<Form.Check
									inline
									label={Object.keys(obj)[0]} // returns values like "vue", "react", "python"
									type={"checkbox"}
									id={index}
								/>
							);
						}
						return box;
					})}
				</Form>
				<Form>
					<Form.Label className="formLabel">Backend</Form.Label>
					{this.state.checked.map((obj, index) => {
						let box = null;
						if (obj.category === "backend") {
							box = (
								<Form.Check
									inline
									label={Object.keys(obj)[0]} // returns values like "vue", "react", "python"
									type={"checkbox"}
									id={index}
								/>
							);
						}
						return box;
					})}
					<Form.Label className="formLabel">Databases</Form.Label>
					{this.state.checked.map((obj, index) => {
						let box = null;
						if (obj.category === "database") {
							box = (
								<Form.Check
									inline
									label={Object.keys(obj)[0]} // returns values like "vue", "react", "python"
									type={"checkbox"}
									id={index}
								/>
							);
						}
						return box;
					})}
				</Form>

				<h5>{dbMsg}</h5>
			</div>
		);
	}
}

export default Homepage;
