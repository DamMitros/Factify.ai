'use client'
import { useKeycloak } from '../../auth/KeycloakProviderWrapper';
import { useEffect, useState } from 'react';
import { api } from '../../lib/api';

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

    useEffect(() => {
        if (!userId) return;

        const fetchPredictions = async () => {
            try {
                const { data } = await api.get(`/nlp/predictions/${userId}`, { 
                    requireAuth: true
                });
                console.log("Predictions data:", data);
                setPredictions(Array.isArray(data) ? data : []);
            } catch (err: any) {
                console.error("Failed to fetch predictions:", err);
                setError(err.message || "Failed to fetch predictions");
            } finally {
                setLoading(false);
            }
        };

        fetchPredictions();
    }, [userId]);

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

    if (loading) return <div className="analysis-history-loading">Loading...</div>;
    if (error) return <div className="analysis-history-error">Error: {error}</div>;

    return (
        <div className="analysis-history">
            <h2>Analysis History</h2>
            {predictions.length === 0 ? (
                <p className="analysis-history-empty">No analyses to display</p>
            ) : (
                <ul className="predictions-list">
                    {predictions.map((pred: any, index: number) => {
                        const itemId = pred.id || index;
                        const timestamp = pred.created_at || pred.timestamp;
                        const formattedDate = formatDate(timestamp);
                        const isExpanded = expandedItems.has(itemId);
                        const shouldShowMore = pred.text && pred.text.length > 100;
                        const displayText = isExpanded ? pred.text : truncateText(pred.text);
                        
                        return (
                            <li key={itemId} className="prediction-item">
                                {timestamp && (
                                    <div className="prediction-meta">
                                        <div className="prediction-timestamp">{formattedDate}</div>
                                    </div>
                                )}
                                
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

                                {pred.overall?.confidence !== null && pred.overall?.confidence !== undefined && (
                                    <div className="prediction-confidence">
                                        <span className="prediction-confidence-label">Model Confidence:</span>
                                        <span className="prediction-confidence-value">{(pred.overall.confidence * 100).toFixed(2)}%</span>
                                    </div>
                                )}

                                {pred.segments && pred.segments.length > 0 && (
                                    <details className="results-segments">
                                        <summary>
                                            View Segments ({pred.segments.length})
                                        </summary>
                                        <div className="segments-list">
                                            {pred.segments.map((seg: any, idx: number) => (
                                                <div key={idx} className="segment-item">
                                                    <p className="segment-title">Segment {seg.index + 1}:</p>
                                                    <p className="segment-probabilities">
                                                        AI: {(seg.prob_generated * 100).toFixed(2)}% | Human: {(seg.prob_human * 100).toFixed(2)}% | Confidence: {seg.confidence !== null && seg.confidence !== undefined ? (seg.confidence * 100).toFixed(2) : 'N/A'}%
                                                    </p>
                                                    <p className="segment-preview">{seg.text}</p>
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
        </div>
    );
}
