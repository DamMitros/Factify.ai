'use client';

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useKeycloak } from '../../../auth/KeycloakProviderWrapper';

interface LogEntry {
  _id: string;
  timestamp?: string;
  text?: string;
  ai_probability?: number;
  user_id?: string;
  [key: string]: any;
}

const SystemLogs: React.FC = () => {
  const { keycloak } = useKeycloak();
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());

  useEffect(() => {
    const fetchLogs = async () => {
      if (!keycloak?.token) return;

      try {
        const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api'}/admin/logs`, {
          headers: {
            Authorization: `Bearer ${keycloak.token}`,
          },
        });
        setLogs(response.data);
      } catch (error) {
        console.error("Error fetching logs:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchLogs();
  }, [keycloak?.token]);

  const toggleExpanded = (id: string) => {
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

  if (loading) return <div>Loading logs...</div>;

  return (
    <div className="bg-white/40 dark:bg-black/40 backdrop-blur-sm shadow-sm rounded-lg overflow-hidden border border-white/20">
      <h2 className="text-xl font-bold p-4 border-b border-white/20 text-gray-900 dark:text-white">Global Analysis Text History</h2>
      <table className="min-w-full leading-normal">
        <thead>
          <tr>
            <th className="px-5 py-3 border-b border-gray-200 dark:border-gray-700 bg-gray-100/50 dark:bg-gray-800/50 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider">Timestamp</th>
            <th className="px-5 py-3 border-b border-gray-200 dark:border-gray-700 bg-gray-100/50 dark:bg-gray-800/50 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider">User ID</th> 
            {/* TO DO: tutaj by musiał być mail usera, może link do user management */}
            <th className="px-5 py-3 border-b border-gray-200 dark:border-gray-700 bg-gray-100/50 dark:bg-gray-800/50 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider">AI Probability</th>
            <th className="px-5 py-3 border-b border-gray-200 dark:border-gray-700 bg-gray-100/50 dark:bg-gray-800/50 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider">Text Snippet</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log) => {
            const isExpanded = expandedItems.has(log._id);
            const text = log.text || '';
            const displayText = isExpanded ? text : (text.length > 100 ? text.substring(0, 100) + '...' : text);

            return (
              <tr key={log._id}>
                <td className="px-5 py-5 border-b border-gray-200 dark:border-gray-700 bg-transparent text-sm">
                  <p className="text-gray-900 dark:text-gray-100 whitespace-no-wrap">
                    {log.timestamp ? new Date(log.timestamp).toLocaleString() : '-'}
                  </p>
                </td>
                <td className="px-5 py-5 border-b border-gray-200 dark:border-gray-700 bg-transparent text-sm">
                  <p className="text-gray-900 dark:text-gray-100 whitespace-no-wrap">
                    {log.user_id || 'Uknown User ID'}
                  </p>
                </td>
                <td className="px-5 py-5 border-b border-gray-200 dark:border-gray-700 bg-transparent text-sm">
                  <div className="flex items-center">
                    <div className="w-16 bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 mr-2">
                      <div className="bg-blue-600 h-2.5 rounded-full" style={{ width: `${Math.min(log.ai_probability || 0, 100)}%` }}></div>
                    </div>
                    <span className="text-gray-900 dark:text-gray-100">{log.ai_probability ? log.ai_probability.toFixed(2) : 0}%</span>
                  </div>
                </td>
                <td className="px-5 py-5 border-b border-gray-200 dark:border-gray-700 bg-transparent text-sm">
                  <p className="text-gray-900 dark:text-gray-100 break-words min-w-[200px]">
                    {displayText}
                  </p>
                  {text.length > 100 && (
                    <button onClick={() => toggleExpanded(log._id)} className="text-blue-500 hover:text-blue-400 text-xs mt-1">
                      {isExpanded ? 'Show less' : 'Show more'}
                    </button>
                  )}
                </td>
              </tr>
            );
          })}
          {logs.length === 0 && (
            <tr>
              <td colSpan={4} className="px-5 py-5 border-b border-gray-200 dark:border-gray-700 bg-transparent text-sm text-center text-gray-500 dark:text-gray-400">No analysis logs found.</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
};

export default SystemLogs;
