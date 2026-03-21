"use client";

import React, { JSX, useEffect, useState } from "react";
import { useKeycloak } from "../../auth/KeycloakProviderWrapper";
import PhotoUpload from "./PhotoUpload";
import PhotoAnalysisResult, { ImageDetectResult } from "./PhotoAnalysisResult";
import AuthModal from "./AuthModal";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080/api";

export default function PhotoAnalyzer(): JSX.Element {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ImageDetectResult | null>(null);
  const [analyzedImageUrl, setAnalyzedImageUrl] = useState<string | null>(null);
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

      const initialData = await response.json();

      if (initialData.success && initialData.taskId) {
        let taskCompleted = false;
        let attempts = 0;
        const maxAttempts = 30;

        while (!taskCompleted && attempts < maxAttempts) {
          await new Promise((resolve) => setTimeout(resolve, 2000));
          attempts++;

          const pollResponse = await fetch(`${API_BASE_URL}/image/detect/${initialData.taskId}`, { 
            headers 
          });
          
          if (!pollResponse.ok) {
            throw new Error(`HTTP ${pollResponse.status}: ${pollResponse.statusText}`);
          }

          const pollData = await pollResponse.json();

          if (pollData.success && pollData.predictions) {
            setResult(pollData as ImageDetectResult);
            taskCompleted = true;

            if (selectedFile) {
              setAnalyzedImageUrl((prev) => {
                if (prev) {
                  URL.revokeObjectURL(prev);
                }
                return URL.createObjectURL(selectedFile);
              });
            }
          } else if (!pollData.success && pollData.message === "Task not found.") {
            throw new Error("Task not found. It may have failed or been removed from the database.");
          }
        }

        if (!taskCompleted) {
          throw new Error("Analysis timed out. Please try again.");
        }
      } 
    } catch (err: any) {
      handleApiError(err, "Image analysis failed:");
    } finally {
      setLoading(false);
    }
  };

  // Cleanup object URL on unmount
  useEffect(() => {
    return () => {
      if (analyzedImageUrl) {
        URL.revokeObjectURL(analyzedImageUrl);
      }
    };
  }, [analyzedImageUrl]);

  return (
    <div className="photo-analyzer-layout">
      <PhotoUpload
        selectedFile={selectedFile}
        onFileChange={setSelectedFile}
        onAnalyze={handleAnalyze}
        loading={loading}
        error={error}
      />
      <PhotoAnalysisResult result={result} uploadedImageUrl={analyzedImageUrl} />
      <AuthModal 
        isOpen={isAuthModalOpen} 
        onClose={() => setIsAuthModalOpen(false)} 
      />
    </div>
  );
}
