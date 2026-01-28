"use client";

import React, { JSX, useState } from "react";
import { useKeycloak } from "../../auth/KeycloakProviderWrapper";
import PhotoUpload from "./PhotoUpload";
import PhotoAnalysisResult, { ImageDetectResult } from "./PhotoAnalysisResult";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080/api";

export default function PhotoAnalyzer(): JSX.Element {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ImageDetectResult | null>(null);

  const { keycloak, authenticated } = useKeycloak();

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setError("Please select an image to analyze");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      const headers: HeadersInit = {};

      if (authenticated && keycloak?.token) {
        headers["Authorization"] = `Bearer ${keycloak.token}`;
      }

      const response = await fetch(`${API_BASE_URL}/image/detect`, {
        method: "POST",
        body: formData,
        headers,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = (await response.json()) as ImageDetectResult;
      setResult(data);
    } catch (err: any) {
      console.error("Image analysis failed:", err);
      setError(err.message || "Failed to analyze image");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="text-analyzer-layout">
      <PhotoUpload
        selectedFile={selectedFile}
        onFileChange={setSelectedFile}
        onAnalyze={handleAnalyze}
        loading={loading}
        error={error}
      />
      <PhotoAnalysisResult result={result} />
    </div>
  );
}
