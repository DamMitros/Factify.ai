'use client';

import { useKeycloak } from "../../auth/KeycloakProviderWrapper";
import { useEffect, useState } from "react";
import { useRouter } from 'next/navigation';
import axios from "axios";
import Bubbles from "../components/Bubbles";
import Overview from "./components/Overview";
import UserManagement from "./components/UserManagement";
import NLPMonitoring from "./components/NLPMonitoring";
import ImageMonitoring from "./components/ImageMonitoring";
import SystemLogs from "./components/SystemLogs";
import ImageLogs from "./components/ImageLogs";
import GlassEffect from "../components/GlassEffect";

interface Stats {
  users: number;
  text_analyses: number;
  image_analyses: number;
  status: string;
}

export default function AdminDashboard() {
  const { keycloak } = useKeycloak();
  const router = useRouter();
  const [stats, setStats] = useState<Stats | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'nlp' | 'image_ai' | 'logs' | 'image_logs'>('overview');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setError(null);
        const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api'}/admin/stats`, {
          headers: {
            Authorization: `Bearer ${keycloak.token}`,
          },
        });
        setStats(response.data);
      } catch (error) {
        console.error("Błąd pobierania statystyk:", error);
        setError("Failed to connect to the backend. Please check if the server is running.");
      }
    };

    if (keycloak?.token) {
      fetchStats();
    }
  }, [keycloak?.token]);

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-[#0a0a0a]">
        <GlassEffect className="p-8 text-center max-w-md">
          <h2 className="text-2xl font-bold text-red-500 mb-4">Connection Error</h2>
          <p className="text-gray-400 mb-6">{error}</p>
          <button onClick={() => window.location.reload()} className="bg-white/10 hover:bg-white/20 px-6 py-2 rounded-lg transition-colors">
            Retry
          </button>
        </GlassEffect>
      </div>
    );
  }

  const renderContent = () => {
    switch (activeTab) {
      case 'overview': return <Overview stats={stats} />;
      case 'users': return <UserManagement />;
      case 'nlp': return <NLPMonitoring />;
      case 'image_ai': return <ImageMonitoring />;
      case 'logs': return <SystemLogs />;
      case 'image_logs': return <ImageLogs />;
      default: return <Overview stats={stats} />;
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a0a] text-white relative overflow-hidden flex flex-col">
      <div className="fixed inset-0 blur-3xl opacity-40 pointer-events-none">
        <Bubbles />
      </div>

      <div className="relative z-10 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-12 flex flex-col gap-8">

        <div className="relative flex flex-col items-center justify-center mb-4">
            <button onClick={() => router.push("/")} className="absolute left-0 top-1/2 -translate-y-1/2 flex items-center gap-2 text-gray-400 hover:text-white transition-colors group px-4 py-2 rounded-lg hover:bg-white/5">
                <svg className="w-5 h-5 group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 19l-7-7 7-7" />
                </svg>
                <span className="hidden sm:inline">Back</span>
            </button>

            <div className="text-center">
                <h1 className="text-4xl font-bold text-white mb-3 tracking-tight">Admin Dashboard</h1>
            </div>
        </div>

        <div className="flex bg-white/5 backdrop-blur-md p-1.5 rounded-2xl border border-white/10 overflow-x-auto shrink-0 scrollbar-hide">
          {[
            { id: 'overview', label: 'Overview' },
            { id: 'users', label: 'Users' },
            { id: 'nlp', label: 'Text AI' },
            { id: 'image_ai', label: 'Image AI' },
            { id: 'logs', label: 'Text History' },
            { id: 'image_logs', label: 'Image History' }
          ].map((tab) => (
            <button key={tab.id} onClick={() => setActiveTab(tab.id as any)} className={`py-2 px-6 rounded-xl font-medium text-sm transition-all whitespace-nowrap ${activeTab === tab.id ? 'bg-white/10 text-white shadow-lg border border-white/5' : 'text-gray-400 hover:text-white hover:bg-white/5'}`}>
              {tab.label}
            </button>
          ))}
        </div>

        <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
          {renderContent()}
        </div>
      </div>
    </div>
  );
}