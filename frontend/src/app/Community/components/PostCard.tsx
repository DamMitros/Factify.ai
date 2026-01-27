'use client';

import { useState } from 'react';
import { socialApi, Post, Comment } from '@/lib/api';
import GlassEffect from '../../components/GlassEffect';

export function PostCard({ 
    post, isAuthenticated, currentUserId, currentUsername, onDelete, onEdit }: { 
    post: Post; 
    isAuthenticated: boolean; 
    currentUserId?: string;
    currentUsername: string;
    onDelete: (id: string) => void;
    onEdit: (id: string, newContent: string) => void;
}) {
    const [likes, setLikes] = useState(post.likes);
    const [isLiked, setIsLiked] = useState(currentUserId ? post.likes.includes(currentUserId) : false);
    const [showComments, setShowComments] = useState(false);
    const [comments, setComments] = useState<Comment[]>([]);
    const [commentsLoading, setCommentsLoading] = useState(false);
    const [newComment, setNewComment] = useState('');
    const [commentsCount, setCommentsCount] = useState(post.comments_count);
    const [isEditing, setIsEditing] = useState(false);
    const [editContent, setEditContent] = useState(post.content);
    const [editingCommentId, setEditingCommentId] = useState<string | null>(null);
    const [editingCommentText, setEditingCommentText] = useState('');
    const [isAnalysisExpanded, setIsAnalysisExpanded] = useState(false);
    const isAuthor = currentUserId === post.user_id;

    const handleLike = async () => {
        if (!isAuthenticated) return;
        const previouslyLiked = isLiked;
        setIsLiked(!previouslyLiked);
        setLikes(prev => previouslyLiked ? prev.filter(id => id !== currentUserId) : [...prev, currentUserId!]);
        try {
            await socialApi.toggleLike(post._id);
        } catch (error) {
            setIsLiked(previouslyLiked);
            console.error('Like failed', error);
        }
    };

    const toggleComments = async () => {
        if (!showComments && comments.length === 0) {
            setCommentsLoading(true);
            try {
                const data = await socialApi.getComments(post._id);
                setComments(data);
            } catch (error) {
                console.error('Failed to load comments', error);
            } finally {
                setCommentsLoading(false);
            }
        }
        setShowComments(!showComments);
    };

    const handleAddComment = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!newComment.trim()) return;
        try {
            await socialApi.addComment(post._id, newComment);
            const addedComment: Comment = {
                _id: Date.now().toString(),
                post_id: post._id,
                user_id: currentUserId || 'me',
                username: currentUsername, 
                text: newComment,
                created_at: new Date().toISOString()
            };
            setComments([...comments, addedComment]);
            setCommentsCount(prev => prev + 1);
            setNewComment('');
        } catch (error) {
            console.error('Failed to add comment', error);
        }
    };

    const saveEdit = () => {
        if (editContent.trim() !== post.content) {
            onEdit(post._id, editContent);
        }
        setIsEditing(false);
    };

    const handleDeleteComment = async (commentId: string) => {
        const previousComments = [...comments];
        setComments(comments.filter(c => c._id !== commentId));
        setCommentsCount(prev => prev - 1);
        try {
            await socialApi.deleteComment(commentId);
        } catch (error) {
            console.error("Failed to delete comment", error);
            setComments(previousComments);
            setCommentsCount(prev => prev + 1);
        }
    };

    const startEditComment = (comment: Comment) => {
        setEditingCommentId(comment._id);
        setEditingCommentText(comment.text);
    };

    const saveCommentEdit = async () => {
        if (editingCommentId && editingCommentText.trim()) {
            const previousComments = [...comments];
            const commentIdToUpdate = editingCommentId;
            const newText = editingCommentText;
            setComments(comments.map(c => c._id === commentIdToUpdate ? { ...c, text: newText } : c));
            setEditingCommentId(null);
            try {
                await socialApi.updateComment(commentIdToUpdate, newText);
            } catch (error) {
                console.error("Failed to update comment", error);
                setComments(previousComments);
            }
        }
    };

    return (
        <GlassEffect className="p-6 rounded-2xl hover:bg-white/[0.07] transition-all duration-300 border border-white/5">
            <div className="flex justify-between items-start mb-4">
                <div className="flex flex-col">
                    <span className="font-bold text-white text-lg tracking-wide">{post.username}</span>
                    <span className="text-xs text-gray-400 font-medium">
                        {new Date(post.created_at).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                    </span>
                </div>
                {isAuthor && !isEditing && (
                    <div className="relative group/menu">
                        <button className="text-gray-500 hover:text-white p-1 rounded hover:bg-white/10 transition-colors">
                            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 8c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z"></path></svg>
                        </button>
                        <div className="absolute right-0 top-full mt-1 w-32 bg-[#1a1a1a] border border-white/10 rounded-lg shadow-xl opacity-0 invisible group-hover/menu:opacity-100 group-hover/menu:visible transition-all z-20 overflow-hidden py-1">
                            <button onClick={() => setIsEditing(true)} className="w-full text-left px-4 py-2 text-sm text-gray-300 hover:bg-white/10 hover:text-white transition-colors">Edit</button>
                            <button onClick={() => onDelete(post._id)} className="w-full text-left px-4 py-2 text-sm text-red-400 hover:bg-red-500/10 hover:text-red-300 transition-colors">Delete</button>
                        </div>
                    </div>
                )}
            </div>

            {isEditing ? (
                <div className="mb-4">
                    <textarea
                        value={editContent}
                        onChange={(e) => setEditContent(e.target.value)}
                        className="w-full bg-black/40 text-white rounded-lg p-3 border border-white/20 focus:border-purple-500 focus:ring-1 focus:ring-purple-500 outline-none resize-none min-h-[100px] text-base"
                    />
                    <div className="flex justify-end gap-2 mt-2">
                        <button onClick={() => { setIsEditing(false); setEditContent(post.content); }} className="px-3 py-1.5 text-sm text-gray-400 hover:text-white hover:bg-white/10 rounded transition-colors">Cancel</button>
                        <button onClick={saveEdit} className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white text-sm rounded-lg transition-colors disabled:opacity-50 font-medium">Save</button>
                    </div>
                </div>
            ) : (
                <div className="mb-5 text-gray-300 whitespace-pre-wrap leading-relaxed text-base">
                    {post.content}
                </div>
            )}

            {post.analysis_data && (
                <div className="mb-5 p-4 rounded-xl bg-gradient-to-r from-purple-900/10 to-blue-900/10 border border-purple-500/10 hover:border-purple-500/30 transition-colors group">
                    <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                            <div className={`w-2 h-2 rounded-full ${post.analysis_data.label?.includes("AI") ? "bg-red-500" : "bg-green-500"}`}></div>
                            <span className="text-sm font-bold text-gray-200">
                                {post.analysis_data.label || "Analysis Result"}
                            </span>
                            <span className="text-xs text-gray-500 border-l border-white/10 pl-2">
                                Confidence: <span className="text-gray-300 font-medium">{(post.analysis_data.score * 100).toFixed(0)}%</span>
                            </span>
                            {post.analysis_data.type && (
                                <span className="text-[10px] bg-white/5 text-gray-500 px-1.5 py-0.5 rounded border border-white/5 uppercase ml-1">
                                    {post.analysis_data.type}
                                </span>
                            )}
                        </div>
                        <svg className="w-4 h-4 text-gray-600 group-hover:text-purple-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" /></svg>
                    </div>
                    
                    <div className="relative flex flex-col sm:flex-row gap-4">
                        {post.analysis_data.type === 'image' && post.analysis_data.image_preview && (
                            <div className="flex-shrink-0 w-full sm:w-24 h-24 rounded-lg overflow-hidden border border-white/10 shadow-lg">
                                <a href={post.analysis_data.image_preview} target="_blank" rel="noopener noreferrer">
                                    <img src={post.analysis_data.image_preview} alt="Analysis thumbnail" className="w-full h-full object-cover hover:scale-110 transition-transform duration-300" />
                                </a>
                            </div>
                        )}
                        <div className="flex-1">
                            <p className={`text-sm text-gray-400 italic pl-4 border-l-2 border-purple-500/20 leading-relaxed ${isAnalysisExpanded ? '' : 'line-clamp-3'}`}>
                                "{post.analysis_data.full_text || post.analysis_data.text_preview}"
                            </p>

                            {(post.analysis_data.full_text && post.analysis_data.full_text.length > 150) && (
                                <button onClick={() => setIsAnalysisExpanded(!isAnalysisExpanded)} className="text-xs text-purple-400 hover:text-purple-300 mt-2 ml-4 font-medium flex items-center gap-1">
                                    {isAnalysisExpanded ? 'Show less' : 'Show more'}
                                    <svg className={`w-3 h-3 transition-transform ${isAnalysisExpanded ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" /></svg>
                                </button>
                            )}
                        </div>
                    </div>
                </div>
            )}

            <div className="flex items-center gap-6 pt-4 border-t border-white/5">
                <button onClick={handleLike} disabled={!isAuthenticated} className={`flex items-center gap-2 text-sm font-medium transition-all group ${isLiked ? 'text-pink-500' : 'text-gray-400 hover:text-pink-400'}`}>
                    <div className={`p-1.5 rounded-full ${isLiked ? 'bg-pink-500/10' : 'group-hover:bg-pink-500/10'} transition-colors`}>
                        <svg className={`w-5 h-5 ${isLiked ? 'fill-current' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" /></svg>
                    </div>
                    {likes.length}
                </button>
                <button onClick={toggleComments} className="flex items-center gap-2 text-sm font-medium text-gray-400 hover:text-blue-400 transition-colors group">
                    <div className="p-1.5 rounded-full group-hover:bg-blue-500/10 transition-colors">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" /></svg>
                    </div>
                    {commentsCount}
                </button>
            </div>

            {showComments && (
                <div className="mt-4 pt-4 border-t border-white/5 animate-in fade-in slide-in-from-top-2 duration-300">
                    {commentsLoading ? (
                        <div className="text-center text-sm text-gray-500 py-2">Loading comments...</div>
                    ) : (
                        <div className="space-y-4">
                            {comments.map((comment) => {
                                const isCommentAuthor = currentUserId === comment.user_id;
                                const isEditingThisComment = editingCommentId === comment._id;
                                return (
                                    <div key={comment._id} className="flex flex-col gap-1 text-sm group/comment bg-white/[0.03] p-3 rounded-xl border border-white/5 relative">
                                        <div className="flex justify-between items-baseline mb-1">
                                            <div className="flex gap-2 items-baseline">
                                                <span className="font-bold text-gray-300 text-xs">{comment.username}</span>
                                                <span className="text-[10px] text-gray-400 font-medium">
                                                    {new Date(comment.created_at).toLocaleString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                                                </span>
                                            </div>
                                            {isCommentAuthor && !isEditingThisComment && (
                                                <div className="opacity-0 group-hover/comment:opacity-100 transition-opacity flex gap-2">
                                                    <button onClick={() => startEditComment(comment)} className="text-gray-500 hover:text-white transition-colors" title="Edit">
                                                        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg>
                                                    </button>
                                                    <button onClick={() => handleDeleteComment(comment._id)} className="text-gray-500 hover:text-red-400 transition-colors" title="Delete">
                                                        <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                                                    </button>
                                                </div>
                                            )}
                                        </div>
                                        {isEditingThisComment ? (
                                            <div className="mt-1">
                                                <input type="text" value={editingCommentText} onChange={(e) => setEditingCommentText(e.target.value)} className="w-full bg-black/40 text-white text-sm rounded-lg px-3 py-2 border border-white/20 focus:border-purple-500/50 outline-none" autoFocus />
                                                <div className="flex justify-end gap-2 mt-2">
                                                    <button onClick={() => setEditingCommentId(null)} className="text-xs text-gray-400 hover:text-white px-2 py-1">Cancel</button>
                                                    <button onClick={saveCommentEdit} className="text-xs bg-white/10 hover:bg-white/20 text-white px-3 py-1 rounded transition-colors">Save</button>
                                                </div>
                                            </div>
                                        ) : (
                                            <p className="text-gray-400 leading-relaxed pl-1">{comment.text}</p>
                                        )}
                                    </div>
                                )
                            })}
                            {isAuthenticated && (
                                <form onSubmit={handleAddComment} className="flex gap-2 mt-4 pt-2">
                                    <input type="text" value={newComment} onChange={(e) => setNewComment(e.target.value)} placeholder="Write a comment..." className="flex-1 bg-black/40 text-white text-sm rounded-lg px-4 py-2.5 border border-white/10 focus:border-purple-500/50 outline-none transition-all placeholder-gray-600" />
                                    <button type="submit" disabled={!newComment.trim()} className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white text-sm rounded-lg transition-colors disabled:opacity-50 font-medium">Send</button>
                                </form>
                            )}
                        </div>
                    )}
                </div>
            )}
        </GlassEffect>
    );
}