'use client';

import { useState } from 'react';
import { AnalysisSummary } from '@/lib/api';
import GlassEffect from '../../components/GlassEffect';

export function CreatePostForm({ 
    username, selectedAnalysis, onOpenAnalysisModal, onRemoveAnalysis,onSubmit }: { 
    username: string;
    selectedAnalysis: AnalysisSummary | null;
    onOpenAnalysisModal: () => void;
    onRemoveAnalysis: () => void;
    onSubmit: (content: string) => Promise<void>;
}) {
    const [newPostContent, setNewPostContent] = useState('');
    const [submitting, setSubmitting] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newPostContent.trim()) return;

        setSubmitting(true);
        try {
            await onSubmit(newPostContent);
            setNewPostContent('');
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <GlassEffect className="p-6 rounded-2xl border-t border-white/10 relative overflow-hidden group">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-purple-500 to-blue-500 opacity-0 group-focus-within:opacity-100 transition-opacity" />
            
            <form onSubmit={handleSubmit}>
                <div className="flex flex-col gap-4">
                    <div className="flex justify-between items-center mb-1">
                        <span className="text-sm font-medium text-gray-300">Create a new post as <span className="text-white font-bold">{username}</span></span>
                    </div>
                    <textarea
                        value={newPostContent}
                        onChange={(e) => setNewPostContent(e.target.value)}
                        placeholder="Share your prediction or thoughts..."
                        className="w-full bg-black/20 text-white rounded-xl p-4 border border-white/5 focus:border-purple-500/30 focus:bg-black/40 outline-none transition-all resize-none min-h-[100px] placeholder-gray-500"
                    />
                    
                    {selectedAnalysis && (
                        <div className="flex items-center justify-between p-3 bg-purple-500/10 border border-purple-500/30 rounded-lg animate-in slide-in-from-top-2">
                            <div className="flex items-center gap-3 overflow-hidden">
                                {selectedAnalysis.type === 'image' && selectedAnalysis.image_preview ? (
                                    <div className="w-12 h-12 rounded-md overflow-hidden border border-purple-500/20 shrink-0">
                                        <img src={selectedAnalysis.image_preview} alt="Analysis thumbnail" className="w-full h-full object-cover" />
                                    </div>
                                ) : (
                                    <div className="p-2 bg-purple-500/20 rounded-md shrink-0">
                                        <svg className="w-5 h-5 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
                                    </div>
                                )}
                                <div className="truncate">
                                    <p className="text-sm font-bold text-purple-200">Attached Analysis</p>
                                    <p className="text-xs text-purple-300/70 truncate">{selectedAnalysis.text_preview}</p>
                                </div>
                            </div>
                            <button type="button" onClick={onRemoveAnalysis} className="p-1 hover:bg-white/10 rounded-full text-purple-300">
                                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" /></svg>
                            </button>
                        </div>
                    )}

                    <div className="flex justify-between items-center pt-2">
                        <button type="button" onClick={onOpenAnalysisModal} className={`flex items-center gap-2 text-sm px-3 py-1.5 rounded-lg border border-dashed border-gray-600 text-gray-400 hover:text-purple-300 hover:border-purple-500/50 transition-colors ${selectedAnalysis ? 'hidden' : ''}`}>
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                            Attach Prediction
                        </button>

                        <button type="submit" disabled={submitting || !newPostContent.trim()} className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white text-sm rounded-lg transition-colors disabled:opacity-50 font-medium ml-auto">
                            {submitting ? 'Posting...' : 'Post'}
                        </button>
                    </div>
                </div>
            </form>
        </GlassEffect>
    );
}