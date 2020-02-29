import React, { Component } from "react";

import Checkbox from "../components/Checkbox";

import { Dropdown, DropdownButton } from "react-bootstrap";
import { withRouter } from "react-router-dom";

import "./Home.css";

class Homepage extends Component {
	state = {
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
			{ SQL: false, category: "database" },
			{ SQLite: false, category: "database" }
		],
		location: null
	};

	handleCheckboxChange = event => {
		const langName = event.target.name;
		const checkboxState = this.state.checked;
		for (let i = 0; i < checkboxState.length; i++) {
			// get the key of the checkbox[indexNum] object
			const checkboxKey = Object.keys(checkboxState[i])[0];
			if (checkboxKey === langName) {
				checkboxState[i][checkboxKey] = event.target.checked;
			}
		}

		this.setState({ checked: checkboxState });
	};

	handleDropdownChange = event => {
		// event has values like "Vancouver", "Seattle"

		// function is used to update state.queryValue with the value of the query!
		// preps the child Results page component with data.
		this.setState({ location: event });
		const selectedLanguages = this.state.checked.map(obj => {
			let getLanguageNameIfTrue = null;
			const langName = Object.keys(obj)[0];
			if (obj[langName] === true) {
				getLanguageNameIfTrue = langName;
			}
			return getLanguageNameIfTrue;
		});
		const selectedLanguagesNotNull = selectedLanguages.filter(x => {
			return x !== null;
		});
		this.props.retrieveData({
			location: this.state.location,
			values: selectedLanguagesNotNull
		});
		this.props.history.push("/results");
	};

	render() {
		const dbMsg = `<Database updated every week!>`;

		// TODO: Organize list of checkboxes into a nice pattern.

		let checkboxes = [];
		for (let i = 0; i < this.state.checked.length; i++) {
			// console.log("Key:" + Object.keys(this.state.checked[i])[0]);
			let checkboxJSX = null;
			if (Object.keys(this.state.checked[i])[0] === "cplusplus") {
				const objectKeys = Object.keys(this.state.checked[i]); // returns a list like [langKey, category]
				const trueOrFalse = this.state.checked[i][objectKeys[0]];
				checkboxJSX = (
					<div key={i} className="checkbox-parent">
						<label>
							<Checkbox
								name={Object.keys(this.state.checked[i])[0]}
								checked={trueOrFalse}
								onChange={this.handleCheckboxChange}
								value="C++"
							/>
						</label>
					</div>
				);
			} else if (Object.keys(this.state.checked[i])[0] === "csharp") {
				const objectKeys = Object.keys(this.state.checked[i]); // returns a list like [langKey, category]
				const trueOrFalse = this.state.checked[i][objectKeys[0]];
				checkboxJSX = (
					<div key={i} className="checkbox-parent">
						<label>
							<Checkbox
								name={Object.keys(this.state.checked[i])[0]}
								checked={trueOrFalse}
								onChange={this.handleCheckboxChange}
								value="C#"
							/>
						</label>
					</div>
				);
			} else {
				const objectKeys = Object.keys(this.state.checked[i]); // returns a list like [langKey, category]
				const trueOrFalse = this.state.checked[i][objectKeys[0]];
				checkboxJSX = (
					<div key={i} className="checkbox-parent">
						<label>
							<Checkbox
								name={Object.keys(this.state.checked[i])[0]}
								checked={trueOrFalse}
								onChange={this.handleCheckboxChange}
								value={Object.keys(this.state.checked[i])[0]}
							/>
						</label>
					</div>
				);
			}

			checkboxes.push(checkboxJSX);
		}

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

				<div className="checkbox-wrapper">{checkboxes}</div>

				<DropdownButton
					title="Cities"
					id="dropdown-cities"
					onSelect={this.handleDropdownChange}
				>
					<div id="dropdown-item-container">
						<Dropdown.Item
							key="1"
							eventKey="Vancouver"
							className="dropdown-option"
							onToggle={this.toggleDropdown}
						>
							Vancouver, BC
						</Dropdown.Item>
						<Dropdown.Item
							key="2"
							eventKey="Toronto"
							className="dropdown-option"
						>
							Toronto, ON
						</Dropdown.Item>
						<Dropdown.Item
							key="3"
							eventKey="Seattle"
							className="dropdown-option"
						>
							Seattle, WA
						</Dropdown.Item>
						<Dropdown.Item
							key="4"
							eventKey="New York City"
							className="dropdown-option"
						>
							New York City, NY
						</Dropdown.Item>
						<Dropdown.Item
							key="5"
							eventKey="Silicon Valley"
							className="dropdown-option"
						>
							Silicon Valley, CA
						</Dropdown.Item>
					</div>
				</DropdownButton>

				<h5>{dbMsg}</h5>
			</div>
		);
	}
}

export default withRouter(Homepage);
