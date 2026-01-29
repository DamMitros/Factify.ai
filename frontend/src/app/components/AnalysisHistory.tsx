'use client'
import { useKeycloak } from '../../auth/KeycloakProviderWrapper';
import { useEffect, useState } from 'react';
import { api } from '../../lib/api';
import AuthModal from './AuthModal';

const formatDate = (dateString: string | Date | undefined) => {
    if (!dateString) return '';

    const date = new Date(dateString);

    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');

    return `${day}.${month}.${year} ${hours}:${minutes}`;
};

const truncateText = (text: string | undefined, maxLength: number = 450) => {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
};

export default function AnalysisHistory() {
    const { keycloak } = useKeycloak();
    const userId = keycloak?.tokenParsed?.sub;
    const [predictions, setPredictions] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [expandedItems, setExpandedItems] = useState<Set<string | number>>(new Set());
    const [activeTab, setActiveTab] = useState<'text' | 'image' | 'manipulation' | 'find_sources'>('text');
    const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);

    const handleApiError = (err: any, defaultMessage: string) => {
        if (err.message?.includes("401")) {
            setIsAuthModalOpen(true);
            return;
        }
        console.error(defaultMessage, err);
        setError(err.message || defaultMessage);
    };

    useEffect(() => {
        if (!userId) return;

        const fetchPredictions = async () => {
            setLoading(true);
            setError(null);
            try {
                let endpoint: string;
                if (activeTab === 'text') {
                    endpoint = `/analysis/ai/predictions`;
                } else if (activeTab === 'image') {
                    endpoint = `/image/predictions`;
                } else if (activeTab === 'manipulation') {
                    endpoint = `/analysis/manipulation/predictions`;
                } else {
                    endpoint = `/analysis/find_sources/predictions`;
                }

                const { data } = await api.get(endpoint, {
                    requireAuth: true
                });
                console.log(`${activeTab} Predictions data:`, data);
                setPredictions(Array.isArray(data) ? data : []);
            } catch (err: any) {
                handleApiError(err, `Failed to fetch ${activeTab} predictions:`);
            } finally {
                setLoading(false);
            }
        };

        fetchPredictions();
    }, [userId, activeTab]);

    const toggleExpanded = (id: string | number) => {
        setExpandedItems(prev => {
            const newSet = new Set(prev);
            if (newSet.has(id)) {
                newSet.delete(id);
            } else {
                newSet.add(id);
            }
            return newSet;
        });
    };

    const handleTabChange = (tab: 'text' | 'image' | 'manipulation' | 'find_sources') => {
        setActiveTab(tab);
        setPredictions([]);
        setLoading(true);
    };

    return (
        <div className="analysis-history">
            <div className="history-header">
                <h2>Analysis History</h2>
                <div className="history-tabs">
                    <button
                        className={`history-tab ${activeTab === 'text' ? 'active' : ''}`}
                        onClick={() => handleTabChange('text')}
                    >
                        Text Analysis
                    </button>
                    <button
                        className={`history-tab ${activeTab === 'image' ? 'active' : ''}`}
                        onClick={() => handleTabChange('image')}
                    >
                        Photo Analysis
                    </button>
                    <button
                        className={`history-tab ${activeTab === 'manipulation' ? 'active' : ''}`}
                        onClick={() => handleTabChange('manipulation')}
                    >
                        Manipulation Analysis
                    </button>
                    <button
                        className={`history-tab ${activeTab === 'find_sources' ? 'active' : ''}`}
                        onClick={() => handleTabChange('find_sources')}
                    >
                        Source Analysis
                    </button>
                </div>
            </div>

            {loading ? (
                <div className="analysis-history-loading">Loading...</div>
            ) : error ? (
                <div className="analysis-history-error">Error: {error}</div>
            ) : predictions.length === 0 ? (
                <p className="analysis-history-empty">No analyses to display</p>
            ) : (
                <ul className="predictions-list">
                    {predictions.map((pred: any, index: number) => {
                        const itemId = pred.id || index;
                        const timestamp = pred.created_at || pred.timestamp;
                        const formattedDate = formatDate(timestamp);
                        const isExpanded = expandedItems.has(itemId);

                        const isImage = activeTab === 'image' || pred.type === 'image';
                        const isManipulation = activeTab === 'manipulation' && (pred.type === 'manipulation' || (!Array.isArray(pred.result) && pred.result && Object.keys(pred.result).length > 0 && typeof Object.values(pred.result)[0] === 'object'));
                        const isFindSources = activeTab === 'find_sources' && (pred.type === 'find_sources' || Array.isArray(pred.result));
                        const shouldShowMore = !isImage && pred.text && pred.text.length > 100;
                        const displayText = !isImage ? (isExpanded ? pred.text : truncateText(pred.text)) : null;
                        
                        const manipulationEntries = isManipulation && pred.result && !Array.isArray(pred.result)
                            ? Object.entries(pred.result as Record<string, Record<string, string[]>>)
                            : [];
                        
                        const findSourcesEntries = isFindSources && Array.isArray(pred.result)
                            ? pred.result
                            : [];

                        return (
                            <li key={itemId} className="prediction-item">
                                {timestamp && (
                                    <div className="prediction-meta">
                                        <div className="prediction-timestamp">{formattedDate}</div>
                                    </div>
                                )}

                                {isImage ? (
                                    <div className="prediction-image-container">
                                        <div className="prediction-text-label">Analyzed Image:</div>
                                        {pred.image_preview && (
                                            <a href={pred.image_preview} target="_blank" rel="noopener noreferrer">
                                                <img
                                                    src={pred.image_preview}
                                                    alt={pred.filename || "Analyzed image"}
                                                    className="prediction-thumbnail"
                                                />
                                            </a>
                                        )}
                                        <p className="prediction-filename">{pred.filename}</p>
                                    </div>
                                ) : (
                                    <>
                                        <div className="prediction-text-label">Analyzed Text:</div>
                                        <p className="prediction-text">{displayText}</p>

                                        {shouldShowMore && (
                                            <button
                                                className="see-more-button"
                                                onClick={() => toggleExpanded(itemId)}
                                            >
                                                {isExpanded ? 'Show less' : 'See more'}
                                            </button>
                                        )}
                                    </>
                                )}

                                {!isManipulation && !isFindSources && (
                                    <div className="prediction-probability">
                                        <span className="prediction-probability-label">AI Probability:</span>
                                        <div className="probability-bar">
                                            <div
                                                className="probability-bar-fill"
                                                style={{ width: `${Math.min(pred.ai_probability || 0, 100)}%` }}
                                            />
                                        </div>
                                        <span className="probability-value">{pred.ai_probability || 0}%</span>
                                    </div>
                                )}

                                {!isManipulation && !isFindSources && pred.overall?.confidence !== null && pred.overall?.confidence !== undefined && (
                                    <div className="prediction-confidence">
                                        <span className="prediction-confidence-label">Model Confidence:</span>
                                        <span className="prediction-confidence-value">{(pred.overall.confidence * 100).toFixed(2)}%</span>
                                    </div>
                                )}

                                {!isImage && !isManipulation && !isFindSources && pred.segments && pred.segments.length > 0 && (
                                    <details className="results-segments">
                                        <summary>
                                            View Segments ({pred.segments.length})
                                        </summary>
                                        <div className="segments-list">
                                            {pred.segments.map((seg: any, idx: number) => {
                                                const isAiSegment = seg.prob_generated >= 0.8;
                                                return (
                                                    <div
                                                        key={idx}
                                                        className={isAiSegment ? "segment-item segment-item-ai" : "segment-item"}
                                                    >
                                                        <p className="segment-title">Segment {seg.index + 1}:</p>
                                                        <p className="segment-probabilities">
                                                            AI: {(seg.prob_generated * 100).toFixed(2)}% | Human: {(seg.prob_human * 100).toFixed(2)}% | Confidence: {seg.confidence !== null && seg.confidence !== undefined ? (seg.confidence * 100).toFixed(2) : 'N/A'}%
                                                        </p>
                                                        <p className="segment-preview">{seg.text}</p>
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    </details>
                                )}

                                {isManipulation && manipulationEntries.length > 0 && (
                                    <details className="manipulation-details">
                                        <summary className="manipulation-details-summary">
                                            Show manipulation details
                                        </summary>

                                        <div className="manipulation-history-details">
                                            {manipulationEntries.map(([category, fragments]) => {
                                                const fragmentEntries = Object.entries(fragments || {});

                                                return (
                                                    <div key={category} className="manipulation-category">
                                                        <h4 className="manipulation-category-title">{category}</h4>
                                                        {fragmentEntries.map(([fragment, reasons], idx) => (
                                                            <div key={fragment} className="manipulation-fragment">
                                                                <p className="manipulation-fragment-index">Fragment {idx + 1}</p>
                                                                <p className="manipulation-fragment-text">“{fragment}”</p>
                                                                <ul className="manipulation-reasons">
                                                                    {Array.isArray(reasons) && reasons.map((reason, reasonIdx) => (
                                                                        <li key={reasonIdx}>{reason}</li>
                                                                    ))}
                                                                </ul>
                                                            </div>
                                                        ))}
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    </details>
                                )}

                                {isFindSources && findSourcesEntries.length > 0 && (
                                    <details className="manipulation-details">
                                        <summary className="manipulation-details-summary">
                                            Show source details
                                        </summary>

                                        <div className="manipulation-history-details">
                                            {findSourcesEntries.map((item: any, idx: number) => (
                                                <div key={idx} className="manipulation-category">
                                                    <div style={{ display: "flex", justifyContent: "space-between" }}>
                                                        <h4 className="manipulation-category-title">{item.category}</h4>
                                                        <span style={{ fontWeight: "bold" }}>{item.status}</span>
                                                    </div>
                                                    <p className="manipulation-fragment-text" style={{ marginTop: "0.5rem" }}>“{item.citation}”</p>
                                                    <p className="manipulation-category-description" style={{ fontStyle: "italic" }}>{item.analysis}</p>
                                                    {item.sources?.length > 0 && (
                                                        <ul className="manipulation-reasons">
                                                            {item.sources.map((source: string, sIdx: number) => (
                                                                <li key={sIdx}>
                                                                    <a href={source} target="_blank" rel="noopener noreferrer" style={{ wordBreak: "break-all" }}>
                                                                        {source}
                                                                    </a>
                                                                </li>
                                                            ))}
                                                        </ul>
                                                    )}
                                                </div>
                                            ))}
                                        </div>
                                    </details>
                                )}
                            </li>
                        );
                    })}
                </ul>
            )}
            <AuthModal 
                isOpen={isAuthModalOpen} 
                onClose={() => setIsAuthModalOpen(false)} 
            />
        </div>
    );
}
