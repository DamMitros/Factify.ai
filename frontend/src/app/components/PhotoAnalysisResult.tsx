import React, { JSX } from "react";

interface ImagePredictions {
  ai: number;
  real: number;
  [key: string]: number;
}

export interface ImageDetectResult {
  filename: string;
  predictions: ImagePredictions;
  is_ai: boolean;
  confidence: number;
  image_preview?: string;
}

interface PhotoAnalysisResultProps {
  result: ImageDetectResult | null;
  uploadedImageUrl?: string | null;
}

export default function PhotoAnalysisResult({ result, uploadedImageUrl }: PhotoAnalysisResultProps): JSX.Element | null {
  if (!result) return null;

  const label = result.is_ai ? "AI-generated image" : "Real image";
  const confidencePercent = (result.confidence * 100).toFixed(1);

  const aiPercent = (result.predictions.ai * 100).toFixed(1);
  const realPercent = (result.predictions.real * 100).toFixed(1);

  return (
    <section className="text-analyzer text-analyzer-results-card">
      <h3 className="text-analyzer-results-title">Analysis Results</h3>
      <div className="text-analyzer-results">
        <p>
          <strong>Result:</strong> {label}
        </p>
        <p>
          <strong>Confidence:</strong> {confidencePercent}%
        </p>
        <p>
          <strong>AI probability:</strong> {aiPercent}%
        </p>
        <p>
          <strong>Real probability:</strong> {realPercent}%
        </p>

        {(uploadedImageUrl || result.image_preview) && (
          <div style={{ marginTop: 24 }}>
            <p className="text-analyzer-label">Analyzed image</p>
            <div
              style={{
                borderRadius: 16,
                border: "1px solid rgba(148, 163, 184, 0.4)",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                maxWidth: "100%",
              }}
            >
              <img
                src={uploadedImageUrl || result.image_preview}
                alt={result.filename}
                style={{
                  display: "block",
                  maxWidth: "100%",
                  height: "auto",
                  objectFit: "contain",
                }}
              />
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
