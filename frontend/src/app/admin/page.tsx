'use client';

import { useKeycloak } from "../../auth/KeycloakProviderWrapper";
import { useEffect, useState } from "react";
import axios from "axios";
import Link from "next/link";
import Overview from "./components/Overview";
import UserManagement from "./components/UserManagement";
import NLPMonitoring from "./components/NLPMonitoring";
import SystemLogs from "./components/SystemLogs";
import { BackButton } from "../components/BackButton";

interface Stats {
  users: number;
  text_analyses: number;
  image_analyses: number;
  status: string;
}

export default function AdminDashboard() {
  const { keycloak } = useKeycloak();
  const [stats, setStats] = useState<Stats | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'nlp' | 'logs' | 'image_logs'>('overview');
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
      <div className="flex items-center justify-center h-screen bg-gray-100">
        <div className="bg-white p-8 rounded-lg shadow-md text-center">
          <h2 className="text-2xl font-bold text-red-600 mb-4">Connection Error</h2>
          <p className="text-gray-700 mb-4">{error}</p>
          <button onClick={() => window.location.reload()} className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
            Retry
          </button>
        </div>
      </div>
    );
  }

  const renderContent = () => {
    switch (activeTab) {
      case 'overview':
        return <Overview stats={stats} />;
      case 'users':
        return <UserManagement />;
      case 'nlp':
        return <NLPMonitoring />;
      case 'logs':
        return <SystemLogs />;
      case 'image_logs':
        return (
          <div className="bg-white shadow-md rounded-lg p-6 text-center">
            <h2 className="text-xl font-semibold text-gray-700">Global Analysis Image History</h2>
            <p className="text-gray-500 mt-2">Coming soon...</p>
          </div>
        );
      default:
        return <Overview stats={stats} />;
    }
  };

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        <BackButton />
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-white drop-shadow-md">Admin Dashboard</h1>
          <Link href="/" className="px-4 py-2 bg-white/20 hover:bg-white/30 text-white rounded-lg backdrop-blur-sm transition-colors flex items-center gap-2 font-medium border border-white/10">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
            Back to Home
          </Link>
        </div>
        
        <div className="flex space-x-4 mb-8 border-b border-white/30 overflow-x-auto pb-2">
          <button onClick={() => setActiveTab('overview')} className={`py-2 px-4 font-medium text-sm focus:outline-none whitespace-nowrap rounded-t-lg transition-colors ${activeTab === 'overview' ? 'bg-white/20 text-white border-b-2 border-blue-400' : 'text-white/70 hover:text-white hover:bg-white/10'}`}>
            Overview
          </button>
          <button onClick={() => setActiveTab('users')} className={`py-2 px-4 font-medium text-sm focus:outline-none whitespace-nowrap rounded-t-lg transition-colors ${activeTab === 'users'? 'bg-white/20 text-white border-b-2 border-blue-400' : 'text-white/70 hover:text-white hover:bg-white/10'}`}>
            User Management
          </button>
          <button onClick={() => setActiveTab('nlp')} className={`py-2 px-4 font-medium text-sm focus:outline-none whitespace-nowrap rounded-t-lg transition-colors ${activeTab === 'nlp' ? 'bg-white/20 text-white border-b-2 border-blue-400' : 'text-white/70 hover:text-white hover:bg-white/10'}`}>
            NLP-AI (Data and Tests)
          </button>
          <button onClick={() => setActiveTab('logs')} className={`py-2 px-4 font-medium text-sm focus:outline-none whitespace-nowrap rounded-t-lg transition-colors ${activeTab === 'logs' ? 'bg-white/20 text-white border-b-2 border-blue-400' : 'text-white/70 hover:text-white hover:bg-white/10'}`}>
            Global Analysis Text History
          </button>
          <button onClick={() => setActiveTab('image_logs')} className={`py-2 px-4 font-medium text-sm focus:outline-none whitespace-nowrap rounded-t-lg transition-colors ${activeTab === 'image_logs' ? 'bg-white/20 text-white border-b-2 border-blue-400' : 'text-white/70 hover:text-white hover:bg-white/10'}`}>
            Global Analysis Image History
          </button>
        </div>

        <div className="bg-white/80 dark:bg-black/60 backdrop-blur-md shadow-xl rounded-xl border border-white/20 p-6">
          {renderContent()}
        </div>
      </div>
    </div>
  );
}