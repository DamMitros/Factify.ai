"use client";

import React, { useState } from "react";
import TextAnalyzerOptions from "./TextAnalyzerOptions";

export default function TextAnalyzer(): JSX.Element {
	const [text, setText] = useState("");

	return (
		<>
			<section className="text-analyzer">
				<header className="text-analyzer-header">
					<h1 className="text-analyzer-title">Analyze Text</h1>
					<p className="text-analyzer-subtitle">
						Paste any text to assess its credibility with the Factify model.
					</p>
				</header>

				<div className="text-analyzer-field">
					<label className="text-analyzer-label" htmlFor="text-input">
						Text to analyze
					</label>
					<textarea
						id="text-input"
						className="text-analyzer-textarea"
						value={text}
						onChange={(event) => setText(event.target.value)}
						placeholder="Paste the text you would like to analyze..."
					/>
				</div>

				<div className="text-analyzer-actions">
					<button type="button" className="text-analyzer-submit">
						Analyze Text
					</button>
				</div>
			</section>

			<TextAnalyzerOptions />
		</>
	);
}
