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
}

export default function PhotoAnalysisResult({ result }: PhotoAnalysisResultProps): JSX.Element | null {
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

        {result.image_preview && (
          <div style={{ marginTop: 24 }}>
            <p className="text-analyzer-label">Analyzed image</p>
            <div
              style={{
                borderRadius: 16,
                overflow: "hidden",
                border: "1px solid rgba(148, 163, 184, 0.4)",
                maxHeight: 320,
              }}
            >
              <img
                src={result.image_preview}
                alt={result.filename}
                style={{ width: "100%", height: "100%", objectFit: "cover" }}
              />
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
