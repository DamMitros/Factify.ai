import React, { JSX } from "react";

export interface FindSourcesResultItem {
  citation: string;
  status: string;
  category: string;
  analysis: string;
  sources: string[];
}

export interface FindSourcesResultData {
  text: string;
  result: FindSourcesResultItem[];
  user_id: string;
}

interface FindSourcesResultsProps {
  result: FindSourcesResultData | null;
}

const STATUS_COLORS: Record<string, string> = {
    "Verified": "#28a745",
    "Misleading": "#ffc107",
    "False": "#dc3545",
    "Unverified": "#6c757d"
};

export default function FindSourcesResults({ result }: FindSourcesResultsProps): JSX.Element | null {
  if (!result) return null;

  return (
    <section className="text-analyzer text-analyzer-results-card">
      <h3 className="text-analyzer-results-title">Source Analysis</h3>
      <div className="text-analyzer-results">
        <div className="manipulation-overview">
          <p className="manipulation-overview-row">
            <span className="manipulation-overview-label">Original text:</span>
            <span className="manipulation-overview-value">{result.text}</span>
          </p>
          <p className="manipulation-overview-row">
            <span className="manipulation-overview-label">Fragments analyzed:</span>
            <span className="manipulation-overview-value">{result.result?.length || 0}</span>
          </p>
        </div>

        {!result.result?.length && (
          <p>No sources were found for this text.</p>
        )}

        {result.result?.length > 0 && (
          <div className="find-sources-details">
            {result.result.map((item, idx) => (
              <div key={idx} className="manipulation-category" style={{ borderLeft: `4px solid ${STATUS_COLORS[item.status] || "#ccc"}`, paddingLeft: "1rem", marginBottom: "1.5rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <h4 className="manipulation-category-title" style={{ margin: 0 }}>{item.category}</h4>
                    <span style={{ 
                        backgroundColor: STATUS_COLORS[item.status] || "#ccc", 
                        color: "white", 
                        padding: "2px 8px", 
                        borderRadius: "4px",
                        fontSize: "0.8rem",
                        fontWeight: "bold"
                    }}>
                        {item.status}
                    </span>
                </div>
                
                <p className="manipulation-fragment-text" style={{ marginTop: "0.5rem" }}>“{item.citation}”</p>
                
                <p className="manipulation-category-description" style={{ fontStyle: "italic" }}>{item.analysis}</p>
                
                {item.sources?.length > 0 && (
                  <div className="sources-list" style={{ marginTop: "0.5rem" }}>
                    <p style={{ fontWeight: "bold", fontSize: "0.9rem", marginBottom: "0.2rem" }}>Sources:</p>
                    <ul className="manipulation-reasons">
                      {item.sources.map((source, sIdx) => (
                        <li key={sIdx}>
                          <a href={source} target="_blank" rel="noopener noreferrer" style={{ wordBreak: "break-all" }}>
                            {source}
                          </a>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
