import React, { JSX } from "react";

export interface ManipulationResultData {
  text: string;
  result: Record<string, Record<string, string[]>>;
  user_id: string;
}

const CATEGORY_DESCRIPTIONS: Record<string, string> = {
  "Loaded Language": "Emotionally charged words or phrases used to provoke a strong reaction instead of rational evaluation.",
  "False Dilemma": "Presenting only two extreme options while ignoring more nuanced or moderate possibilities.",
  "Appeal to Authority/Fear": "Using authority figures or fear-inducing scenarios to bypass critical thinking.",
  "Ad Hominem": "Attacking a person or group instead of addressing their arguments or actions.",
  "Framing Bias": "Presenting information in a way that hides or downplays inconvenient facts.",
  "Selection/Omission Bias": "Cherry-picking supporting information while omitting important counterarguments or context.",
  "Sensationalism": "Exaggerating impact, using hyperbole, or dramatizing events to trigger strong emotions.",
};

interface ManipulationResultsProps {
  result: ManipulationResultData | null;
}

export default function ManipulationResults({ result }: ManipulationResultsProps): JSX.Element | null {
  if (!result) return null;

  const categories = Object.entries(result.result || {});
  const totalFragments = categories.reduce(
    (sum, [, fragments]) => sum + Object.keys(fragments || {}).length,
    0
  );

  return (
    <section className="text-analyzer text-analyzer-results-card">
      <h3 className="text-analyzer-results-title">Manipulation Analysis</h3>
      <div className="text-analyzer-results">
        <div className="manipulation-overview">
          <p className="manipulation-overview-row">
            <span className="manipulation-overview-label">Original text:</span>
            <span className="manipulation-overview-value">{result.text}</span>
          </p>
          <p className="manipulation-overview-row">
            <span className="manipulation-overview-label">Detected categories:</span>
            <span className="manipulation-overview-value">
              {categories.length > 0 ? categories.map(([name]) => name).join(", ") : "None"}
            </span>
          </p>
          <p className="manipulation-overview-row">
            <span className="manipulation-overview-label">Total flagged fragments:</span>
            <span className="manipulation-overview-value">{totalFragments}</span>
          </p>
        </div>

        {!categories.length && (
          <p>No manipulation patterns were detected in this text.</p>
        )}

        {categories.length > 0 && (
          <details className="manipulation-details">
            <summary className="manipulation-details-summary">
              Show detailed manipulation breakdown
            </summary>

            {categories.map(([category, fragments]) => {
              const fragmentEntries = Object.entries(fragments || {});
              const description = CATEGORY_DESCRIPTIONS[category] || "";

              return (
                <div key={category} className="manipulation-category">
                  <h4 className="manipulation-category-title">{category}</h4>
                  {description && (
                    <p className="manipulation-category-description">{description}</p>
                  )}
                  {fragmentEntries.map(([fragment, reasons], idx) => (
                    <div key={fragment} className="manipulation-fragment">
                      <p className="manipulation-fragment-index">Fragment {idx + 1}</p>
                      <p className="manipulation-fragment-text">“{fragment}”</p>
                      <ul className="manipulation-reasons">
                        {reasons.map((reason, reasonIdx) => (
                          <li key={reasonIdx}>{reason}</li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              );
            })}
          </details>
        )}
      </div>
    </section>
  );
}
