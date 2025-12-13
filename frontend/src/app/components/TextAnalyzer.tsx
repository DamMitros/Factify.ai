"use client";

import React, { JSX, useState } from "react";
import TextAnalyzerOptions from "./TextAnalyzerOptions";
import { api } from "../../lib/api";
import { useKeycloak } from "../../auth/KeycloakProviderWrapper";

export default function TextAnalyzer(): JSX.Element {
    const [text, setText] = useState("");
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [error, setError] = useState<string | null>(null);
    const { keycloak, authenticated } = useKeycloak();

    const handleAnalyze = async () => {
        if (!text.trim()) {
            setError("Please enter some text to analyze");
            return;
        }

        setLoading(true);
        setError(null);
        setResult(null);

        try {
            const userId = authenticated && keycloak?.tokenParsed?.sub 
                ? keycloak.tokenParsed.sub 
                : undefined;

            const { data } = await api.post('/nlp/predict', {
                text: text,
                detailed: true,
            }, { requireAuth: authenticated });

            setResult(data);
        } catch (err: any) {
            console.error("Analysis failed:", err);
            setError(err.message || "Failed to analyze text");
        } finally {
            setLoading(false);
        }
    };

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
                        onChange={(e) => setText(e.target.value)}
                        placeholder="Paste the text you would like to analyze..."
                        disabled={loading}
                    />
                </div>

                {error && (
                    <div className="text-analyzer-error">
                        Error: {error}
                    </div>
                )}

                {result && (
                    <div className="text-analyzer-results">
                        <h3>Analysis Results:</h3>
                        <p><strong>AI Probability:</strong> {result.ai_probability}%</p>
                        <p><strong>Human Probability:</strong> {result.human_probability}%</p>
                        
                        {result.segments && (
                            <details className="results-segments">
                                <summary>
                                    View Segments ({result.segments.length})
                                </summary>
                                <div className="segments-list">
                                    {result.segments.map((seg: any, idx: number) => (
                                        <div key={idx} className="segment-item">
                                            <p className="segment-title">Segment {seg.index + 1}:</p>
                                            <p className="segment-probabilities">
                                                AI: {(seg.prob_generated * 100).toFixed(2)}% | Human: {(seg.prob_human * 100).toFixed(2)}%
                                            </p>
                                            <p className="segment-preview">{seg.text.substring(0, 100)}...</p>
                                        </div>
                                    ))}
                                </div>
                            </details>
                        )}
                    </div>
                )}

                <div className="text-analyzer-actions">
                    <button 
                        type="button" 
                        className="text-analyzer-submit"
                        onClick={handleAnalyze}
                        disabled={loading}
                    >
                        {loading ? "Analyzing..." : "Analyze Text"}
                    </button>
                </div>
            </section>

            <TextAnalyzerOptions />
        </>
    );
}
