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

import "./Results.css";

import { Link } from "react-router-dom";

class Results extends Component {
	state = {
		// Each entry in "queries" is an object: {lang, loc, jobs, posts}
		queries: []
	};

	componentDidMount() {
		document.title = "Results";
	}

	getData(lang, loc, testMode = false) {
		// lang: the language aka .what to query
		// loc: the location aka .where to query

		if (testMode) {
			// use Test Mode to avoid dealing with the mySQL server errors
			const testValues = [
				{ lang: "vue", loc: "Vancouver", jobs: 134, posts: null },
				{
					lang: "angular",
					loc: "Vancouver",
					jobs: 344,
					posts: null
				},
				{ lang: "php", loc: "Vancouver", jobs: 378, posts: null }
			];
			this.setState({ queries: testValues });
		} else {
			// let postsToAdd = [];
			let queryData;
			console.log("getting json for " + lang + " at " + loc);
			let queryToAdd = null;

			axios
				 .get(`http://127.0.0.1:5000/lang/${lang}/loc/${loc}`)
				// .get(`http://165.227.78.120:5000/lang/${lang}/loc/${loc}`)
				.then(query => {
					console.log("query.data:");
					console.log(query.data);
					queryData = query.data;
					// for (let i = 0; i < query.data.length; i++) {
					// 	// console.log(posts.data[i]);
					// 	postsToAdd.push(query.data[i]);
					// }
					// console.log(postsToAdd[0]);
					// queryToAdd = {
					// 	lang: postsToAdd[0].language,
					// 	loc: postsToAdd[0].location,
					// 	jobs: postsToAdd[0].num_of_posts,
					// 	posts: postsToAdd
					// };
					queryToAdd = {
						lang: queryData.language,
						loc: queryData.location,
						jobs: queryData.num_of_posts,
						url: queryData.url
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
			for (let i = 0; i < queriesList.length; i++) {
				const lang = queriesList[i][0];
				const loc = queriesList[i][1];
				this.getData(lang, loc);
			}
		} else {
			for (let i = 0; i < this.state.queries.length; i++) {
				dataToDisplay += this.state.queries[i].lang;
			}
			return dataToDisplay;
		}
	}

	render() {
		let headline = "Here's the results of your search!";
		let chartedCity = "Loading...";

		const graphData = [];
		if (this.props.data) {
			for (let i = 0; i < this.props.data.values.length; i++) {
				// comes out as e.g. ["python", "Vancouver"] and ["php", "Vancouver"]
				const lang = this.props.data.values[i];
				const loc = this.props.data.location;
				const query = [lang, loc];
				graphData.push(query);
				chartedCity = loc;
			}
		} else {
			// If the user got to the Results page without supplying something to this.props.data, give a random result.
			const potentialLangs = [
				"vue",
				"angular",
				"react",
				"html",
				"css",
				"javascript",
				"python",
				"php",
				"mongodb",
				"sql"
			];
			const potentialCities = [
				"Vancouver",
				"Toronto",
				"Seattle",
				"New York"
			];
			const randomCityIndex = Math.floor(
				Math.random() * potentialCities.length
			);
			const cityToDisplay = potentialCities[randomCityIndex];

			const randInts = [];
			while (randInts.length < 3) {
				const r = Math.floor(Math.random() * potentialLangs.length);
				if (randInts.indexOf(r) === -1) randInts.push(r);
			}

			graphData.push([potentialLangs[randInts[0]], cityToDisplay]);
			graphData.push([potentialLangs[randInts[1]], cityToDisplay]);
			graphData.push([potentialLangs[randInts[2]], cityToDisplay]);

			headline =
				"No input data from homepage; here's a random query for you.";
		}
		this.checkIfDataNeeded(graphData);

		let data = [
			{ language: "Loading!", jobs: 50 },
			{ language: "Loading...", jobs: 90 },
			{ language: "Loading", jobs: 135 }
		];

		let urls = [];

		if (this.state.queries.length > 0) {
			data = [];
			for (let i = 0; i < this.state.queries.length; i++) {
				if (this.state.queries[i].lang === "cplusplus") {
					const dataObject = {
						language: "c++",
						jobs: this.state.queries[i].jobs
					};
					const url = <a href={this.state.queries[i].url}>C++</a>;
					data.push(dataObject);
					urls.push(url);
				} else if (this.state.queries[i].lang === "csharp") {
					const dataObject = {
						language: "c#",
						jobs: this.state.queries[i].jobs
					};
					const url = <a href={this.state.queries[i].url}>C#</a>;
					data.push(dataObject);
					urls.push(url);
				} else {
					const dataObject = {
						language: this.state.queries[i].lang,
						jobs: this.state.queries[i].jobs
					};
					const url = (
						<a href={this.state.queries[i].url}>
							{this.state.queries[i].lang}
						</a>
					);
					data.push(dataObject);
					urls.push(url);
				}
			}
			chartedCity = this.state.queries[0].loc;
		}

		let displayUrls = [];

		for (let i = 0; i < urls.length; i++) {
			displayUrls.push(urls[i]);
			displayUrls.push(<span>, </span>);
		}
		displayUrls.pop();

		const chartDisplay = data ? (
			<VictoryChart
				theme={VictoryTheme.material}
				domainPadding={20}
				height={200}
				width={data.length < 6 ? 200 : 400}
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
							fontSize: data.length < 4 ? 10 : 8,
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
				<div className="flex-container">
					<div id="headline-container">
						<h3>{headline}</h3>
					</div>
				</div>
				<h3>City: {chartedCity}</h3>
				<div className="flex-container">
					<div id="chart-container">{chartDisplay}</div>
				</div>
				<div>
					<h3>Click the links below to check the work yourself...</h3>
					<br />
					<div id="urls">{displayUrls}</div>
				</div>
				<div className="flex-container">
					<div id="home-button-container">
						<Link to="/">Back to Home</Link>
					</div>
				</div>
			</div>
		);
	}
}

export default Results;
