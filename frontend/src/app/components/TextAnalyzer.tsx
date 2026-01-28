"use client";

import React, { JSX, useState } from "react";
import TextAnalyzerOptions from "./TextAnalyzerOptions";
import TextAnalyzerResults from "./TextAnalyzerResults";
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
        <div className="text-analyzer-layout">
            <section className="text-analyzer text-analyzer-input">
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

                <TextAnalyzerOptions />
            </section>

            <TextAnalyzerResults result={result} />
        </div>
    );
}
