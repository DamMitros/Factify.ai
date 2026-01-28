import React, { JSX } from "react";

interface Segment {
  index: number;
  prob_generated: number;
  prob_human: number;
  text: string;
}

interface TextAnalyzerResultsProps {
  result: {
    ai_probability: number;
    human_probability: number;
    segments?: Segment[];
  } | null;
}

export default function TextAnalyzerResults({ result }: TextAnalyzerResultsProps): JSX.Element | null {
  if (!result) return null;

  const segments = result.segments ?? [];

  const highlightedContent = segments.length
    ? segments.map((seg, idx) => {
        const isAi = seg.prob_generated >= 0.8;
        return (
          <span
            key={idx}
            className={isAi ? "highlighted-segment-ai" : undefined}
          >
            {seg.text}
          </span>
        );
      })
    : null;

  return (
    <section className="text-analyzer text-analyzer-results-card">
      <h3 className="text-analyzer-results-title">Analysis Results</h3>
      <div className="text-analyzer-results">
        <p><strong>AI Probability:</strong> {result.ai_probability}%</p>
        <p><strong>Human Probability:</strong> {result.human_probability}%</p>

        {highlightedContent && (
          <div className="highlighted-text-block">
            <p className="highlighted-text-label">Highlighted text</p>
            <p className="highlighted-text-body">
              {highlightedContent}
            </p>
          </div>
        )}

        {result.segments && (
          <details className="results-segments">
            <summary>
              View Segments ({result.segments.length})
            </summary>
            <div className="segments-list">
              {result.segments.map((seg, idx) => (
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
    </section>
  );
}
