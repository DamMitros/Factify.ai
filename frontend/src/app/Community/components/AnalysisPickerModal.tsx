'use client';

import { useState, useEffect, ReactNode } from 'react';
import { socialApi, AnalysisSummary } from '@/lib/api';
import GlassEffect from '../../components/GlassEffect';

export function AnalysisPickerModal({ 
    isOpen, onClose, onSelect }: { 
    isOpen: boolean; onClose: () => void; onSelect: (analysis: AnalysisSummary) => void;}) {

    const [analyses, setAnalyses] = useState<AnalysisSummary[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        if (isOpen) {
            setLoading(true);
            setError('');
            socialApi.getMyAnalyses()
                .then(data => {
                    setAnalyses(data);
                })
                .catch(err => {
                    console.error("Failed to load analyses", err);
                    setError('Failed to load analysis history');
                })
                .finally(() => setLoading(false));
        }
    }, [isOpen]);

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-in fade-in duration-200">
            <GlassEffect className="w-full max-w-2xl rounded-2xl border border-white/10 bg-[#0f0f0f] max-h-[80vh] flex flex-col shadow-2xl">
                
                <div className="px-6 py-3 border-b border-white/10 flex justify-between items-center bg-white/5">
                    <span className="text-[10px] font-bold text-gray-400 uppercase tracking-[0.2em]">Attach Prediction</span>
                    <button onClick={onClose} className="text-gray-500 hover:text-white transition-colors p-1.5 hover:bg-white/10 rounded-full">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" /></svg>
                    </button>
                </div>
                
                <div className="p-6 overflow-y-auto custom-scrollbar flex-1 bg-black/20">
                    {loading ? (
                        <div className="flex flex-col items-center justify-center py-20 gap-4">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
                            <span className="text-sm text-gray-500">Loading history...</span>
                        </div>
                    ) : error ? (
                        <div className="text-center py-20 text-red-400 flex flex-col items-center gap-3">
                            <svg className="w-10 h-10 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
                            <span className="text-base">{error}</span>
                        </div>
                    ) : analyses.length === 0 ? (
                        <div className="text-center py-20 text-gray-500 flex flex-col items-center gap-4">
                            <div className="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center text-gray-600">
                                <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                            </div>
                            <div className="flex flex-col gap-1">
                                <p className="text-lg font-medium text-gray-300">No analysis history found</p>
                                <p className="text-sm text-gray-500">Run an analysis first to share it with the community.</p>
                            </div>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 gap-3">
                            {analyses.map(analysis => (
                                <button key={analysis.id} onClick={() => onSelect(analysis)} className="w-full text-left p-5 rounded-xl bg-white/[0.03] hover:bg-white/[0.08] border border-white/5 hover:border-purple-500/30 transition-all group duration-200 relative overflow-hidden shadow-sm hover:shadow-md">
                                    <div className="flex justify-between items-start mb-3 relative z-10">
                                        <div className="flex items-center gap-3">
                                            <span className={`text-xs font-bold px-2.5 py-1 rounded-md border tracking-wide uppercase ${analysis.label === 'Unknown' ? 'bg-gray-500/10 text-gray-400 border-gray-500/20' : analysis.label.includes('AI') ? 'bg-red-500/10 text-red-300 border-red-500/20' : 'bg-green-500/10 text-green-300 border-green-500/20'}`}>
                                                {analysis.label}
                                            </span>
                                            {analysis.label !== 'Unknown' && analysis.score > 0 && (
                                                <span className="text-xs font-medium text-gray-500 flex items-center gap-1.5">
                                                    Confidence: <span className="text-white font-semibold">{(analysis.score * 100).toFixed(0)}%</span>
                                                </span>
                                            )}
                                            <span className="text-[10px] px-1.5 py-0.5 rounded bg-white/5 text-gray-400 border border-white/10 uppercase tracking-tighter">
                                                {analysis.type || 'text'}
                                            </span>
                                        </div>
                                        <span className="text-xs text-gray-500 font-mono bg-black/20 px-2 py-1 rounded">
                                            {analysis.created_at ? new Date(analysis.created_at).toLocaleDateString() : ''}
                                        </span>
                                    </div>
                                    <div className="flex gap-4 relative z-10">
                                        {analysis.type === 'image' && analysis.image_preview && (
                                            <div className="flex-shrink-0 w-16 h-16 rounded-lg overflow-hidden border border-white/10">
                                                <img src={analysis.image_preview} alt="preview" className="w-full h-full object-cover" />
                                            </div>
                                        )}
                                        <p className="text-sm text-gray-300 line-clamp-2 leading-relaxed font-light pl-1 border-l-2 border-white/10 group-hover:border-purple-500/50 transition-colors flex-1">
                                            "{analysis.text_preview}"
                                        </p>
                                    </div>
                                    
                                    <div className="absolute inset-0 bg-gradient-to-r from-purple-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
                                </button>
                            ))}
                        </div>
                    )}
                </div>
            </GlassEffect>
        </div>
    );
}