'use client';

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useKeycloak } from '../../../auth/KeycloakProviderWrapper';

interface User {
  keycloakId?: string;
  email: string;
  firstName?: string;
  lastName?: string;
  username?: string;
  enabled?: boolean;
}

interface HistoryItem {
  _id: string;
  text: string;
  ai_probability: number;
  timestamp: string;
}

const UserManagement: React.FC = () => {
  const { keycloak } = useKeycloak();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);
  const [selectedUserHistory, setSelectedUserHistory] = useState<{ user: User, history: HistoryItem[] } | null>(null);
  const [expandedHistoryItems, setExpandedHistoryItems] = useState<Set<string>>(new Set());

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api'}/admin/users`, {
        headers: {
          Authorization: `Bearer ${keycloak.token}`,
        },
      });
      setUsers(response.data);
    } catch (error) {
      console.error("Error fetching users:", error);
      setMessage({ type: 'error', text: 'Failed to fetch users' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (keycloak?.token) {
      fetchUsers();
    }
  }, [keycloak?.token]);

  const toggleHistoryItem = (id: string) => {
    setExpandedHistoryItems(prev => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      return newSet;
    });
  };

  const handleDelete = async (email: string) => {
    if (!confirm(`Are you sure you want to delete user ${email}?`)) return;

    try {
      await axios.delete(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api'}/admin/users/${email}`, {
        headers: {
          Authorization: `Bearer ${keycloak.token}`,
        },
      });
      setUsers(users.filter(u => u.email !== email));
      setMessage({ type: 'success', text: 'User deleted successfully' });
    } catch (error) {
      console.error("Error deleting user:", error);
      setMessage({ type: 'error', text: 'Failed to delete user' });
    }
  };

  const handleBlockToggle = async (user: User) => {
    if (!user.keycloakId) return;
    const newStatus = !user.enabled;
    const action = newStatus ? 'unblock' : 'block';
    
    if (!confirm(`Are you sure you want to ${action} user ${user.email}?`)) return;

    try {
      await axios.put(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api'}/admin/users/${user.keycloakId}/block`, 
        { enabled: newStatus },
        {
          headers: {
            Authorization: `Bearer ${keycloak.token}`,
          },
        }
      );
      
      setUsers(users.map(u => u.keycloakId === user.keycloakId ? { ...u, enabled: newStatus } : u));
      setMessage({ type: 'success', text: `User ${action}ed successfully` });
    } catch (error) {
      console.error(`Error ${action}ing user:`, error);
      setMessage({ type: 'error', text: `Failed to ${action} user` });
    }
  };

  const handleViewHistory = async (user: User) => {
    if (!user.keycloakId) return;
    try {
      const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api'}/admin/users/${user.keycloakId}/history`, {
        headers: {
          Authorization: `Bearer ${keycloak.token}`,
        },
      });
      setSelectedUserHistory({ user, history: response.data });
    } catch (error) {
      console.error("Error fetching history:", error);
      setMessage({ type: 'error', text: 'Failed to fetch user history' });
    }
  };

  const handleSync = async () => {
    try {
      setLoading(true);
      setMessage(null);
      const response = await axios.post(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api'}/admin/users/sync`, {}, {
        headers: {
          Authorization: `Bearer ${keycloak.token}`,
        },
      });
      await fetchUsers();
      setMessage({ type: 'success', text: response.data.message || 'Users synced successfully' });
    } catch (error) {
      console.error("Error syncing users:", error);
      setMessage({ type: 'error', text: 'Failed to sync users with Keycloak' });
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading users...</div>;

  return (
    <>
      {selectedUserHistory && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[9999] flex items-center justify-center p-4">
          <div className="relative w-full max-w-6xl max-h-[90vh] flex flex-col bg-white/95 dark:bg-gray-900/95 backdrop-blur-md rounded-xl shadow-2xl border border-white/20 overflow-hidden">
            <div className="flex justify-between items-center p-6 border-b border-gray-200 dark:border-gray-700 shrink-0">
              <h3 className="text-xl font-bold text-gray-900 dark:text-white">History for {selectedUserHistory.user.email}</h3>
              <button onClick={() => setSelectedUserHistory(null)} className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
                </svg>
              </button>
            </div>
            
            <div className="p-6 overflow-y-auto overflow-x-auto flex-grow">
              {selectedUserHistory.history.length > 0 ? (
                <table className="min-w-full leading-normal">
                  <thead>
                    <tr>
                      <th className="px-5 py-3 border-b border-gray-200 dark:border-gray-700 bg-gray-100/50 dark:bg-gray-800/50 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider whitespace-nowrap">Date</th>
                      <th className="px-5 py-3 border-b border-gray-200 dark:border-gray-700 bg-gray-100/50 dark:bg-gray-800/50 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider whitespace-nowrap">AI Prob</th>
                      <th className="px-5 py-3 border-b border-gray-200 dark:border-gray-700 bg-gray-100/50 dark:bg-gray-800/50 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider">Text Snippet</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedUserHistory.history.map((item) => {
                      const isExpanded = expandedHistoryItems.has(item._id);
                      const text = item.text || '';
                      const displayText = isExpanded ? text : (text.length > 100 ? text.substring(0, 100) + '...' : text);
                      
                      return (
                        <tr key={item._id}>
                          <td className="px-5 py-5 border-b border-gray-200 dark:border-gray-700 bg-transparent text-sm align-top text-gray-900 dark:text-gray-100 whitespace-nowrap">
                            {new Date(item.timestamp).toLocaleString()}
                          </td>
                          <td className="px-5 py-5 border-b border-gray-200 dark:border-gray-700 bg-transparent text-sm align-top text-gray-900 dark:text-gray-100 whitespace-nowrap">
                            <div className="flex items-center">
                              <div className="w-16 bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 mr-2">
                                <div 
                                  className="bg-blue-600 h-2.5 rounded-full" 
                                  style={{ width: `${Math.min(item.ai_probability || 0, 100)}%` }}
                                ></div>
                              </div>
                              <span>{item.ai_probability ? item.ai_probability.toFixed(2) : 0}%</span>
                            </div>
                          </td>
                          <td className="px-5 py-5 border-b border-gray-200 dark:border-gray-700 bg-transparent text-sm text-gray-900 dark:text-gray-100 min-w-[300px]">
                            <p className="break-words">
                              {displayText}
                            </p>
                            {text.length > 100 && (
                              <button onClick={() => toggleHistoryItem(item._id)} className="text-blue-500 hover:text-blue-400 text-xs mt-1 font-medium">
                                {isExpanded ? 'Show less' : 'Show more'}
                              </button>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              ) : (
                <p className="text-gray-500 dark:text-gray-400 text-center py-8">No history found for this user.</p>
              )}
            </div>

            <div className="p-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-800/50 shrink-0 flex justify-end">
              <button onClick={() => setSelectedUserHistory(null)} className="px-6 py-2 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-800 dark:text-white rounded-lg transition-colors font-medium">
                Close
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="bg-white/40 dark:bg-black/40 backdrop-blur-sm shadow-sm rounded-lg overflow-hidden relative border border-white/20">
        <div className="p-4 flex justify-between items-center border-b border-white/20">
        <div>
          {message && (
            <div className={`px-4 py-2 rounded ${message.type === 'success' ? 'bg-green-100/80 text-green-800' : 'bg-red-100/80 text-red-800'}`}>{message.text}</div>
          )}
        </div>
        <div className="flex space-x-2">
          <button onClick={handleSync} className="bg-green-500/90 hover:bg-green-600 text-white font-bold py-2 px-4 rounded shadow-lg backdrop-blur-sm transition-all">
            Sync with Keycloak
          </button>
        </div>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full leading-normal">
          <thead>
            <tr>
              <th className="px-5 py-3 border-b border-gray-200 dark:border-gray-700 bg-gray-100/50 dark:bg-gray-800/50 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider">Email</th>
              <th className="px-5 py-3 border-b border-gray-200 dark:border-gray-700 bg-gray-100/50 dark:bg-gray-800/50 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider">Username</th>
              <th className="px-5 py-3 border-b border-gray-200 dark:border-gray-700 bg-gray-100/50 dark:bg-gray-800/50 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider">Status</th>
              <th className="px-5 py-3 border-b border-gray-200 dark:border-gray-700 bg-gray-100/50 dark:bg-gray-800/50 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.email}>
                <td className="px-5 py-5 border-b border-gray-200 dark:border-gray-700 bg-transparent text-sm">
                  <p className="text-gray-900 dark:text-gray-100 whitespace-no-wrap">{user.email}</p>
                </td>
                <td className="px-5 py-5 border-b border-gray-200 dark:border-gray-700 bg-transparent text-sm">
                  <p className="text-gray-900 dark:text-gray-100 whitespace-no-wrap">{user.username || '-'}</p>
                </td>
                <td className="px-5 py-5 border-b border-gray-200 dark:border-gray-700 bg-transparent text-sm">
                  <span className={`relative inline-block px-3 py-1 font-semibold leading-tight ${user.enabled !== false ? 'text-green-900' : 'text-red-900'}`}>
                    <span aria-hidden className={`absolute inset-0 opacity-50 rounded-full ${user.enabled !== false ? 'bg-green-200' : 'bg-red-200'}`}></span>
                    <span className="relative">{user.enabled !== false ? 'Active' : 'Blocked'}</span>
                  </span>
                </td>
                <td className="px-5 py-5 border-b border-gray-200 dark:border-gray-700 bg-transparent text-sm space-x-2">
                  <button onClick={() => handleViewHistory(user)} className="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300">
                    History
                  </button>
                  <button onClick={() => handleBlockToggle(user)} className={`${user.enabled !== false ? 'text-yellow-600 hover:text-yellow-800 dark:text-yellow-400 dark:hover:text-yellow-300' : 'text-green-600 hover:text-green-800 dark:text-green-400 dark:hover:text-green-300'}`}>
                    {user.enabled !== false ? 'Block' : 'Unblock'}
                  </button>
                  <button onClick={() => handleDelete(user.email)} className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300">
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      </div>
    </>
  );
};

export default UserManagement;
