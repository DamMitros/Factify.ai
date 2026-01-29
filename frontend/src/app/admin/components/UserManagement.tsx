'use client';

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useKeycloak } from '../../../auth/KeycloakProviderWrapper';
import GlassEffect from '../../components/GlassEffect';

interface User {
  keycloakId: string;
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  enabled: boolean;
  createdAt?: string;
}

interface HistoryLog {
  _id: string;
  timestamp: string;
  content?: string;
  text?: string;
  result?: string;
  prediction?: string;
  label?: string;
  overall?: {
    label?: string;
    confidence?: number;
    prob_generated?: number;
    prob_human?: number;
  };
  ai_probability?: number;
}

const UserManagement: React.FC = () => {
  const { keycloak } = useKeycloak();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [history, setHistory] = useState<HistoryLog[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  const fetchUsers = async () => {
    if (!keycloak?.token) return;
    try {
      const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api'}/admin/users`, {
        headers: { Authorization: `Bearer ${keycloak.token}` }
      });
      setUsers(response.data);
    } catch (error) {
      console.error("Error fetching users:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [keycloak?.token]);

  const handleSync = async () => {
    setSyncing(true);
    try {
      await axios.post(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api'}/admin/users/sync`, {}, {
        headers: { Authorization: `Bearer ${keycloak.token}` }
      });
      await fetchUsers();
    } catch (error) {
      console.error("Sync failed:", error);
    } finally {
      setSyncing(false);
    }
  };

  const toggleBlockUser = async (user: User) => {
    try {
      setUsers(users.map(u => u.keycloakId === user.keycloakId ? { ...u, enabled: !u.enabled } : u));
      
      await axios.put(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api'}/admin/users/${user.keycloakId}/block`, 
        { enabled: !user.enabled },
        { headers: { Authorization: `Bearer ${keycloak.token}` } }
      );
    } catch (error) {
      console.error("Block/Unblock failed:", error);
      fetchUsers();
    }
  };

  const handleDeleteUser = async (email: string) => {
    if (!confirm(`Are you sure you want to delete user ${email}? This action cannot be undone.`)) return;

    try {
      setUsers(users.filter(u => u.email !== email));
      await axios.delete(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api'}/admin/users/${email}`, {
        headers: { Authorization: `Bearer ${keycloak.token}` }
      });
    } catch (error) {
      console.error("Delete user failed:", error);
      alert("Failed to delete user.");
      fetchUsers();
    }
  };

  const fetchUserHistory = async (user: User) => {
    setSelectedUser(user);
    setLoadingHistory(true);
    setHistory([]);
    try {
      const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api'}/admin/users/${user.keycloakId}/history`, {
        headers: { Authorization: `Bearer ${keycloak.token}` }
      });
      setHistory(response.data);
    } catch (error) {
      console.error("History fetch failed:", error);
    } finally {
      setLoadingHistory(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-white tracking-tight">Users</h2>
        <button onClick={handleSync} disabled={syncing} className={`px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-medium transition-all shadow-lg shadow-blue-900/20 flex items-center gap-2 ${syncing ? 'opacity-50 cursor-not-allowed' : ''}`}>
          {syncing ? (
             <svg className="animate-spin h-4 w-4 text-white" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
          ) : (
             <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
          )}
          Sync with Keycloak
        </button>
      </div>

      <GlassEffect className="rounded-2xl overflow-hidden border border-white/10">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-gray-400">
            <thead className="bg-white/5 text-gray-200 uppercase text-xs">
              <tr>
                <th className="px-6 py-4 font-medium tracking-wider">User</th>
                <th className="px-6 py-4 font-medium tracking-wider">Email</th>
                <th className="px-6 py-4 font-medium tracking-wider">Status</th>
                <th className="px-6 py-4 font-medium tracking-wider text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {loading ? (
                 <tr><td colSpan={4} className="px-6 py-8 text-center animate-pulse">Loading users...</td></tr>
              ) : users.map((user) => (
                <tr key={user.keycloakId} className="hover:bg-white/5 transition-colors group">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                        <div className="text-white font-medium">{user.username || 'No Username'}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4">{user.email}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium border ${
                      user.enabled 
                        ? 'bg-green-500/10 text-green-400 border-green-500/20' 
                        : 'bg-red-500/10 text-red-400 border-red-500/20'
                    }`}>
                      {user.enabled ? 'Active' : 'Blocked'}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right flex justify-end gap-2">
                    <button 
                        onClick={() => fetchUserHistory(user)}
                        title="View History"
                        className="p-2 rounded-lg bg-white/5 hover:bg-blue-500/20 text-gray-400 hover:text-blue-400 border border-transparent hover:border-blue-500/30 transition-all"
                    >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    </button>
                    <button 
                        onClick={() => toggleBlockUser(user)}
                        title={user.enabled ? 'Block User' : 'Unblock User'}
                        className={`p-2 rounded-lg border transition-all ${
                            user.enabled 
                            ? 'bg-white/5 hover:bg-yellow-500/20 text-gray-400 hover:text-yellow-400 border-transparent hover:border-yellow-500/30' 
                            : 'bg-green-500/10 hover:bg-green-500/20 text-green-400 border-green-500/20'
                        }`}
                    >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"></path></svg>
                    </button>
                    <button 
                        onClick={() => handleDeleteUser(user.email)}
                        title="Delete User"
                        className="p-2 rounded-lg bg-white/5 hover:bg-red-500/20 text-gray-400 hover:text-red-400 border border-transparent hover:border-red-500/30 transition-all"
                    >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </GlassEffect>

      {selectedUser && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setSelectedUser(null)}></div>
            <GlassEffect className="relative w-full max-w-2xl max-h-[80vh] flex flex-col rounded-2xl border border-white/20 shadow-2xl overflow-hidden bg-[#0a0a0a]">
                <div className="p-6 border-b border-white/10 flex justify-between items-center bg-white/5">
                    <h3 className="text-xl font-bold text-white">History: {selectedUser.username}</h3>
                    <button onClick={() => setSelectedUser(null)} className="text-gray-400 hover:text-white transition-colors">
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                    </button>
                </div>
                
                <div className="flex-1 overflow-y-auto p-0 custom-scrollbar">
                    {loadingHistory ? (
                        <div className="p-12 flex justify-center">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
                        </div>
                    ) : history.length === 0 ? (
                        <div className="p-12 text-center text-gray-500">No analysis history found for this user.</div>
                    ) : (
                        <table className="w-full text-left text-sm text-gray-400">
                            <thead className="bg-black/40 sticky top-0 backdrop-blur-md z-10">
                                <tr>
                                    <th className="px-6 py-3 font-medium text-xs uppercase tracking-wider text-gray-500">Time</th>
                                    <th className="px-6 py-3 font-medium text-xs uppercase tracking-wider text-gray-500">Snippet</th>
                                    <th className="px-6 py-3 font-medium text-xs uppercase tracking-wider text-right text-gray-500">Result</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-white/5">
                                {history.map((h) => {
                                    const displayText = h.text || h.content || '-';

                                    let resultRaw = h.overall?.label || h.label || h.result || h.prediction || 'Unknown';
                                    
                                    const resultStr = String(resultRaw);
                                    const resultLower = resultStr.toLowerCase();
                                    const isHuman = resultLower.includes('human') || resultLower.includes('real');
                                    const isAi = resultLower.includes('ai') || resultLower.includes('fake') || resultLower.includes('generated');
                                    const isUnknown = resultStr === 'Unknown';

                                    let confidenceDisplay = '';
                                    if (h.overall?.confidence) {
                                        confidenceDisplay = `${(h.overall.confidence * 100).toFixed(1)}%`;
                                    } else if (h.ai_probability !== undefined) {
                                        confidenceDisplay = `${h.ai_probability.toFixed(1)}%`;
                                    }
                                    
                                    return (
                                    <tr key={h._id} className="hover:bg-white/5 transition-colors">
                                        <td className="px-6 py-3 whitespace-nowrap text-xs font-mono">
                                            {h.timestamp ? new Date(h.timestamp).toLocaleDateString() + ' ' + new Date(h.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) : '-'}
                                        </td>
                                        <td className="px-6 py-3 text-gray-300">
                                            <div className="truncate max-w-[240px]" title={displayText}>
                                                {displayText}
                                            </div>
                                        </td>
                                        <td className="px-6 py-3 text-right">
                                            <div className="flex flex-col items-end gap-1">
                                                <span className={`inline-block px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                                                    isUnknown ? 'bg-gray-500/20 text-gray-400' :
                                                    isHuman
                                                    ? 'bg-green-500/20 text-green-400 border border-green-500/20' 
                                                    : 'bg-red-500/20 text-red-400 border border-red-500/20'
                                                }`}>
                                                    {resultStr}
                                                </span>
                                                {confidenceDisplay && (
                                                    <span className="text-[10px] text-gray-500 font-mono">{confidenceDisplay}</span>
                                                )}
                                            </div>
                                        </td>
                                    </tr>
                                )})}
                            </tbody>
                        </table>
                    )}
                </div>
            </GlassEffect>
        </div>
      )}
    </div>
  );
};

export default UserManagement;