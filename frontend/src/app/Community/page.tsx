'use client';

import { useState, useEffect } from 'react';
import keycloak from '../../auth/keycloak';
import { socialApi, Post, AnalysisSummary } from '@/lib/api';
import Bubbles from '../components/Bubbles';
import { AnalysisPickerModal } from './components/AnalysisPickerModal';
import { PostCard } from './components/PostCard';
import { CreatePostForm } from './components/CreatePostForm';
import GlassEffect from '../components/GlassEffect';
import { BackButton } from '../components/BackButton';

export default function CommunityPage() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [username, setUsername] = useState<string>('Guest');
  const [userId, setUserId] = useState<string | undefined>(undefined);
  const [posts, setPosts] = useState<Post[]>([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedAnalysis, setSelectedAnalysis] = useState<AnalysisSummary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setIsAuthenticated(!!keycloak.authenticated);
    if (keycloak.authenticated && keycloak.tokenParsed) {
      setUsername(keycloak.tokenParsed.preferred_username || 'User');
      setUserId(keycloak.subject);
    }
  }, []);

  const fetchFeed = async () => {
    try {
      const data = await socialApi.getFeed();
      setPosts(data);
    } catch (error) {
      console.error('Failed to fetch feed:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFeed();
  }, []);

  const handleCreatePost = async (content: string) => {
    try {
      await socialApi.createPost(content, selectedAnalysis?.id, selectedAnalysis?.type || 'text');
      setSelectedAnalysis(null);
      await fetchFeed();
    } catch (error) {
      console.error('Failed to create post:', error);
    }
  };

  const handleDeletePost = async (postId: string) => {
      const previousPosts = [...posts];
      setPosts(posts.filter(p => p._id !== postId));
      try {
        await socialApi.deletePost(postId);
      } catch (error) {
        console.error("Failed to delete post:", error);
        setPosts(previousPosts);
      }
  };

  const handleEditPost = async (postId: string, newContent: string) => {
      const previousPosts = [...posts];
      setPosts(posts.map(p => p._id === postId ? { ...p, content: newContent } : p));
      try {
        await socialApi.updatePost(postId, newContent);
      } catch (error) {
        console.error("Failed to update post:", error);
        setPosts(previousPosts);
      }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white relative overflow-hidden flex flex-col">
       <div className="blur-xl fixed"><Bubbles /> </div>
       <AnalysisPickerModal 
            isOpen={isModalOpen} 
            onClose={() => setIsModalOpen(false)} 
            onSelect={(analysis) => {
                setSelectedAnalysis(analysis);
                setIsModalOpen(false);
            }}
       />
       
        <BackButton />

      <div className="relative z-10 w-full max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-12 flex flex-col gap-8">
        
        <div className="relative flex flex-col items-center justify-center mb-4">
            <div className="text-center">
                <h1 className="text-4xl font-bold text-white mb-3 tracking-tight">Factify Community</h1>
                <p className="text-gray-400 text-sm max-w-lg mx-auto leading-relaxed">Join the discussion about AI content detection. Share results and verify information.</p>
            </div>
        </div>

        {isAuthenticated ? (
            <CreatePostForm 
                username={username}
                selectedAnalysis={selectedAnalysis}
                onOpenAnalysisModal={() => setIsModalOpen(true)}
                onRemoveAnalysis={() => setSelectedAnalysis(null)}
                onSubmit={handleCreatePost}
            />
        ) : (
            <GlassEffect className="p-8 rounded-2xl text-center border-dashed border-white/20 flex flex-col items-center justify-center gap-4">
                <p className="text-gray-300 text-lg">Log in to join the discussion and share your predictions.</p>
            </GlassEffect>
        )}

        <div className="space-y-6">
        {loading ? (
            <div className="flex justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
            </div>
        ) : posts.length === 0 ? (
            <div className="text-center py-10 text-gray-500 bg-white/5 rounded-2xl border border-white/5">No posts yet. Be the first one to share!</div>
        ) : (
            posts.map((post) => (
            <PostCard 
                key={post._id} 
                post={post} 
                isAuthenticated={isAuthenticated} 
                currentUserId={userId} 
                currentUsername={username}
                onDelete={handleDeletePost}
                onEdit={handleEditPost}
            />
            ))
        )}
        </div>
      </div>
    </div>
  );
}
