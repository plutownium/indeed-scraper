import React from "react";

import styled from "styled-components";

const divStyle = {
	display: "flex",
	alignItems: "center"
};

const pStyle = {
	margin: "5px"
};

const HiddenCheckbox = styled.input.attrs({ type: "checkbox" })`
	// Hide checkbox visually but remain accessible to screen readers.
	// Source: https://polished.js.org/docs/#hidevisually
	border: 0;
	clip: rect(0 0 0 0);
	clippath: inset(50%);
	height: 1px;
	margin: -1px;
	overflow: hidden;
	padding: 0;
	position: absolute;
	white-space: nowrap;
	width: 1px;
`;

const StyledCheckbox = styled.div`
	display: inline-block;
	width: 16px;
	height: 16px;
	background: ${props => (props.checked ? "salmon" : "papayawhip")};
	border-radius: 3px;
	transition: all 150ms;

	${HiddenCheckbox}:focus + & {
		box-shadow: 0 0 0 3px pink;
	}
`;

const CheckboxContainer = styled.div`
	display: inline-block;
	vertical-align: middle;
`;

const Icon = styled.svg`
	fill: none;
	stroke: white;
	stroke-width: 2px;
`;

// const checkbox = props => <input type="checkbox" {...props} />;

const Checkbox = ({ className, checked, ...props }, name) => (
	<div style={divStyle}>
		<CheckboxContainer className={className}>
			<HiddenCheckbox checked={checked} {...props} />
			<StyledCheckbox checked={checked}>
				<Icon viewBox="0 0 24 24">
					<polyline points="20 6 9 17 4 12" />
				</Icon>
			</StyledCheckbox>
		</CheckboxContainer>
		<p style={pStyle}>{props.value}</p>
	</div>
);

export default Checkbox;
