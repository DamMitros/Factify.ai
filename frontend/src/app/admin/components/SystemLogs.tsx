'use client';

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useKeycloak } from '../../../auth/KeycloakProviderWrapper';
import GlassEffect from '../../components/GlassEffect';

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
          headers: { Authorization: `Bearer ${keycloak.token}` },
        });
        setLogs(response.data);
      } catch (e) { console.error(e); } finally { setLoading(false); }
    };
    fetchLogs();
  }, [keycloak?.token]);

  const toggleExpanded = (id: string) => {
    setExpandedItems(prev => {
      const newSet = new Set(prev);
      if (newSet.has(id)) newSet.delete(id);
      else newSet.add(id);
      return newSet;
    });
  };

  if (loading) return <div className="p-12 text-center text-gray-500">Retrieving system logs...</div>;

  return (
    <GlassEffect className="p-0 overflow-hidden border-white/10">
      <div className="p-6 border-b border-white/10 flex justify-between items-center bg-white/5">
        <h2 className="text-xl font-bold text-white">Global Analysis Text History</h2>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-white/5">
          <thead className="bg-white/5">
            <tr>
              <th className="px-6 py-4 text-left text-[10px] font-bold text-gray-400 uppercase tracking-widest">User ID</th>
              <th className="px-6 py-4 text-left text-[10px] font-bold text-gray-400 uppercase tracking-widest">AI Result</th>
              <th className="px-6 py-4 text-left text-[10px] font-bold text-gray-400 uppercase tracking-widest">Analysed Text</th>
              <th className="px-6 py-4 text-left text-[10px] font-bold text-gray-400 uppercase tracking-widest">Timestamp</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {logs.map((log) => {
              const isExpanded = expandedItems.has(log._id);
              const text = log.text || '';
              const displayText = isExpanded ? text : (text.length > 80 ? text.substring(0, 80) + '...' : text);

              return (
                <tr key={log._id} className="hover:bg-white/5 transition-colors">
                  <td className="px-6 py-4 text-xs font-mono text-gray-500 truncate max-w-[120px]">
                    {log.user_id || 'Uknown'}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-1 bg-white/5 rounded-full overflow-hidden">
                        <div className="h-full bg-blue-500" style={{ width: `${log.ai_probability || 0}%` }} />
                      </div>
                      <span className="text-xs font-mono">{(log.ai_probability || 0).toFixed(1)}%</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <p className="text-xs text-gray-300 leading-relaxed max-w-xs">{displayText}</p>
                    {text.length > 80 && (
                      <button onClick={() => toggleExpanded(log._id)} className="text-blue-500 text-[10px] mt-1 hover:underline">
                        {isExpanded ? 'Show less' : 'Show more'}
                      </button>
                    )}
                  </td>
                  <td className="px-6 py-4 text-[10px] text-gray-500 whitespace-nowrap">
                    {log.timestamp ? new Date(log.timestamp).toLocaleString() : '-'}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </GlassEffect>
  );
};

export default SystemLogs;