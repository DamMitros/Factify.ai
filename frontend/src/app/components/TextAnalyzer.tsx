"use client";

import React, { JSX, useState } from "react";
import TextAnalyzerOptions from "./TextAnalyzerOptions";
import TextAnalyzerResults from "./TextAnalyzerResults";
import ManipulationResults, { ManipulationResultData } from "./ManipulationResults";
import FindSourcesResults, { FindSourcesResultData } from "./FindSourcesResults";
import AuthModal from "./AuthModal";
import { api } from "../../lib/api";
import { useKeycloak } from "../../auth/KeycloakProviderWrapper";

export default function TextAnalyzer(): JSX.Element {
    const [text, setText] = useState("");
    const [file, setFile] = useState<File | null>(null);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [manipulationResult, setManipulationResult] = useState<ManipulationResultData | null>(null);
    const [findSourcesResult, setFindSourcesResult] = useState<FindSourcesResultData | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [activeOption, setActiveOption] = useState<number | null>(1);
    const [analysisKind, setAnalysisKind] = useState<"ai" | "manipulation" | "find_sources" | null>("ai");
    const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
    const { keycloak, authenticated } = useKeycloak();

    const handleApiError = (err: any, defaultMessage: string) => {
        if (err.message?.includes("401")) {
            setIsAuthModalOpen(true);
            return;
        }
        console.error(defaultMessage, err);
        setError(err.message || defaultMessage);
    };

    const handleAiAnalyze = async () => {
        if (!text.trim() && !file) {
            setError("Please enter some text or upload a file to analyze");
            return;
        }

        setLoading(true);
        setError(null);
        setResult(null);
        setManipulationResult(null);
        setFindSourcesResult(null);
        setAnalysisKind("ai");

        try {
            interface StartResponse { success: boolean; taskId?: string; message?: string; }
            interface StatusResponse { success: boolean; message?: string; data?: ManipulationResultData; }

            const payload = file ? new FormData() : { text };
            if (file && payload instanceof FormData) {
                payload.append("file", file);
            }

            const { data: start } = await api.post<StartResponse>(
                "/analysis/ai",
                payload,
                { requireAuth: authenticated }
            );

            if (!start.success || !start.taskId) {
                throw new Error(start.message || "Failed to start AI detection analysis");
            }

            const taskId = start.taskId;
            const pollIntervalMs = 2000;
            const maxAttempts = 30;

            const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

            for (let attempt = 0; attempt < maxAttempts; attempt++) {
                const { data: status } = await api.get<StatusResponse>(
                    `/analysis/ai/${taskId}`,
                    { requireAuth: authenticated }
                );

                if (status.success && status.data) {
                    setResult(status.data);
                    return;
                }

                if (!status.success && status.message && status.message !== "Task is not completed yet.") {
                    throw new Error(status.message);
                }

                await sleep(pollIntervalMs);
            }

            throw new Error("AI detection analysis timed out. Please try again.");
        } catch (err: any) {
            handleApiError(err, "AI detection analysis failed:");
        } finally {
            setLoading(false);
        }
    };

    const handleManipulationAnalyze = async () => {
        if (!text.trim() && !file) {
            setError("Please enter some text or upload a file to analyze");
            return;
        }

        setLoading(true);
        setError(null);
        setResult(null);
        setManipulationResult(null);
        setFindSourcesResult(null);
        setAnalysisKind("manipulation");

        try {
            interface StartResponse { success: boolean; taskId?: string; message?: string; }
            interface StatusResponse { success: boolean; message?: string; data?: ManipulationResultData; }

            const payload = file ? new FormData() : { text };
            if (file && payload instanceof FormData) {
                payload.append("file", file);
            }

            const { data: start } = await api.post<StartResponse>(
                "/analysis/manipulation",
                payload,
                { requireAuth: authenticated }
            );

            if (!start.success || !start.taskId) {
                throw new Error(start.message || "Failed to start manipulation analysis");
            }

            const taskId = start.taskId;
            const pollIntervalMs = 2000;
            const maxAttempts = 30;

            const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

            for (let attempt = 0; attempt < maxAttempts; attempt++) {
                const { data: status } = await api.get<StatusResponse>(
                    `/analysis/manipulation/${taskId}`,
                    { requireAuth: authenticated }
                );

                if (status.success && status.data) {
                    setManipulationResult(status.data);
                    return;
                }

                if (!status.success && status.message && status.message !== "Task is not completed yet.") {
                    throw new Error(status.message);
                }

                await sleep(pollIntervalMs);
            }

            throw new Error("Manipulation analysis timed out. Please try again.");
        } catch (err: any) {
            handleApiError(err, "Manipulation analysis failed:");
        } finally {
            setLoading(false);
        }
    };
    
    const handleFindSourcesAnalyze = async () => {
        if (!text.trim() && !file) {
            setError("Please enter some text or upload a file to analyze");
            return;
        }

        setLoading(true);
        setError(null);
        setResult(null);
        setManipulationResult(null);
        setFindSourcesResult(null);
        setAnalysisKind("find_sources");

        try {
            interface StartResponse { success: boolean; taskId?: string; message?: string; }
            interface StatusResponse { success: boolean; message?: string; data?: FindSourcesResultData; }

            const payload = file ? new FormData() : { text };
            if (file && payload instanceof FormData) {
                payload.append("file", file);
            }

            const { data: start } = await api.post<StartResponse>(
                "/analysis/find_sources",
                payload,
                { requireAuth: authenticated }
            );

            if (!start.success || !start.taskId) {
                throw new Error(start.message || "Failed to start source analysis");
            }

            const taskId = start.taskId;
            const pollIntervalMs = 2000;
            const maxAttempts = 30;

            const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

            for (let attempt = 0; attempt < maxAttempts; attempt++) {
                const { data: status } = await api.get<StatusResponse>(
                    `/analysis/find_sources/${taskId}`,
                    { requireAuth: authenticated }
                );

                if (status.success && status.data) {
                    setFindSourcesResult(status.data);
                    return;
                }

                if (!status.success && status.message && status.message !== "Task is not completed yet.") {
                    throw new Error(status.message);
                }

                await sleep(pollIntervalMs);
            }

            throw new Error("Source analysis timed out. Please try again.");
        } catch (err: any) {
            handleApiError(err, "Source analysis failed:");
        } finally {
            setLoading(false);
        }
    };

    const handleAnalyze = async () => {
        const mode = activeOption ?? 1;

        if (mode === 2) {
            await handleManipulationAnalyze();
        } else if (mode === 3) {
            await handleFindSourcesAnalyze();
        } else {
            await handleAiAnalyze();
        }
    };

    const handleOptionSelect = (id: number) => {
        setActiveOption(id);
        // Actual analysis is triggered by the main Analyze button
    };

    return (
        <div className="text-analyzer-layout">
            <section className="text-analyzer text-analyzer-input">
                <header className="text-analyzer-header">
                    <h1 className="text-analyzer-title">Analyze Text</h1>
                    <p className="text-analyzer-subtitle">
                        Paste any text or upload a file to assess its credibility with the Factify model.
                    </p>
                </header>

                <div className="text-analyzer-field">
                    {/* <label className="text-analyzer-label" htmlFor="text-input">
                        Text to analyze
                    </label> */}
                    <textarea
                        id="text-input"
                        className="text-analyzer-textarea"
                        value={text}
                        onChange={(e) => {
                            setText(e.target.value);
                            if (e.target.value.trim()) setFile(null);
                        }}
                        placeholder={file ? "File selected. Clear file to use text input." : "Paste the text you would like to analyze..."}
                        disabled={loading || !!file}
                    />
                    
                    <div className="text-analyzer-file-upload-container">
                        <div className="text-analyzer-file-info">
                            {file ? (
                                <span className="text-analyzer-file-name">Selected: {file.name}</span>
                            ) : (
                                <span className="text-analyzer-file-placeholder">Or upload a file (.txt, .md, .pdf, .docx)</span>
                            )}
                        </div>
                        <div className="text-analyzer-file-actions">
                            <input
                                id="file-upload"
                                type="file"
                                accept=".txt,.md,.pdf,.docx"
                                onChange={(e) => {
                                    const selectedFile = e.target.files?.[0] || null;
                                    setFile(selectedFile);
                                    if (selectedFile) setText("");
                                }}
                                disabled={loading}
                                style={{ display: 'none' }}
                            />
                            <button 
                                type="button" 
                                className="text-analyzer-file-button"
                                onClick={() => document.getElementById('file-upload')?.click()}
                                disabled={loading}
                            >
                                {file ? "Change File" : "Choose File"}
                            </button>
                            {file && (
                                <button 
                                    type="button" 
                                    className="text-analyzer-file-clear"
                                    onClick={() => setFile(null)}
                                    disabled={loading}
                                >
                                    Clear
                                </button>
                            )}
                        </div>
                    </div>
                </div>

                {error && (
                    <div className="text-analyzer-error">
                        Error: {error}
                    </div>
                )}

                <div className="text-analyzer-actions text-analyzer-actions-with-options">
                    <div className="text-analyzer-options-inline">
                        <TextAnalyzerOptions activeId={activeOption} onSelect={handleOptionSelect} />
                    </div>

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
            {analysisKind === "ai" && <TextAnalyzerResults result={result} />}
            {analysisKind === "manipulation" && <ManipulationResults result={manipulationResult} />}
            {analysisKind === "find_sources" && <FindSourcesResults result={findSourcesResult} />}

            <AuthModal 
                isOpen={isAuthModalOpen} 
                onClose={() => setIsAuthModalOpen(false)} 
            />
        </div>
    );
}
