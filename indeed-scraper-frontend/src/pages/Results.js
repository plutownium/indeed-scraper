import React, { Component } from "react";
import axios from "axios";
import {
	VictoryBar,
	VictoryChart,
	VictoryTheme,
	VictoryAxis,
	VictoryStack,
	VictoryLabel
} from "victory";

class Results extends Component {
	state = {
		// Each entry in "queries" is an object: {lang, loc, jobs, posts}
		queries: []
	};

	getData(lang, loc, testMode = false) {
		// lang: the language aka .what to query
		// loc: the location aka .where to query

		if (testMode) {
			// use Test Mode to avoid dealing with the mySQL server errors
			const testValues = [
				{ lang: "vue", loc: "Vancouver, BC", jobs: 134, posts: null },
				{
					lang: "angular",
					loc: "Vancouver, BC",
					jobs: 344,
					posts: null
				},
				{ lang: "PHP", loc: "Vancouver, BC", jobs: 378, posts: null }
			];
			this.setState({ queries: testValues });
		} else {
			const postsToAdd = [];
			console.log("getting json for " + lang + " at " + loc);
			let queryToAdd = null;

			axios
				.get(`http://127.0.0.1:5000/lang/${lang}/loc/${loc}`)
				.then(posts => {
					// console.log(posts.data);
					for (let i = 0; i < posts.data.length; i++) {
						// console.log(posts.data[i]);
						postsToAdd.push(posts.data[i]);
					}
					queryToAdd = {
						lang: postsToAdd[0].language,
						loc: postsToAdd[0].location,
						jobs: postsToAdd.length,
						posts: postsToAdd
					};
					console.log("Success");
				})
				.then(x => {
					// Generate a new array to hold the current state
					const state = [];
					// Push the current state into the state array
					for (let i = 0; i < this.state.queries.length; i++) {
						state.push(this.state.queries[i]);
					}
					// Finally, push the new Query to add
					state.push(queryToAdd);
					// and then set Queries equal to the State array
					this.setState({ queries: state });
				});
		}
	}

	checkIfDataNeeded(queriesList) {
		// takes an array of arrays as an arg. each array in the array is [lang, loc]
		// depreciated: lang, loc as args

		let dataToDisplay = "";

		// why am i doing it this way tho? what's up with the else block?
		if (this.state.queries.length === 0) {
			console.log("222");
			for (let i = 0; i < queriesList.length; i++) {
				const lang = queriesList[i][0];
				const loc = queriesList[i][1];
				this.getData(lang, loc);
			}
		} else {
			// console.log("4000");
			// console.log(this.state.queries.length); // should be like 3
			for (let i = 0; i < this.state.queries.length; i++) {
				// console.log("queries[i]: " + this.state.queries[i]);
				// console.log("QUERIES:" + this.state.queries);
				dataToDisplay += this.state.queries[i].lang;
			}
			return dataToDisplay;
		}
	}

	render() {
		// const queryList = [
		// 	["vue", "Vancouver,+BC"],
		// 	["angular", "Vancouver,+BC"],
		// 	["PHP", "Vancouver,+BC"]
		// ];

		const graphData = [];
		if (this.props.data) {
			for (let i = 0; i < this.props.data.values.length; i++) {
				// comes out as e.g. ["python", "Vancouver"] and ["php", "Vancouver"]
				const lang = this.props.data.values[i];
				const loc = this.props.data.location;
				const query = [lang, loc];
				graphData.push(query);
			}
		} else {
			// TODO: Do something here if the user got to the Results page without passing data from the homepg.
			// Maybe "do a random query & show it to the user as an example w/ the text,
			// 'hey! here's a random query for you since you didn't tell us what to search'"
		}
		this.checkIfDataNeeded(graphData);

		// TODO: Now I need to GET that data into getData and use it as input for the Victory Chart.

		let data = [];
		if (this.state.queries.length > 0) {
			for (let i = 0; i < this.state.queries.length; i++) {
				const dataObject = {
					language: this.state.queries[i].lang,
					jobs: this.state.queries[i].jobs
				};
				data.push(dataObject);
			}
		}

		const chartDisplay = data ? (
			<VictoryChart
				theme={VictoryTheme.material}
				domainPadding={20}
				height={200}
				width={200}
			>
				<VictoryAxis
					tickValues={[1, 2, 3, 4]}
					style={{
						// axisLabel: {
						// 	fontSize: 20,
						// 	padding: 30,
						// 	angle: 90
						// }
						tickLabels: {
							fontSize: 10,
							padding: 10,
							angle: 40
						}
					}}
				/>
				<VictoryAxis dependentAxis />
				<VictoryStack colorScale={"warm"}>
					<VictoryBar
						data={data}
						x={"language"}
						y={"jobs"}
						labelComponent={
							<VictoryLabel
								y={270}
								verticalAnchor={"start"}
								angle={180}
							/>
						}
					/>
				</VictoryStack>
			</VictoryChart>
		) : null;

		return (
			<div>
				<h3>Here's the results of your search!</h3>
				{/* {this.checkIfDataNeeded(graphData)} */}
				<div style={{ height: "600px", width: "600px" }}>
					{chartDisplay}
				</div>
			</div>
		);
	}
}

export default Results;
