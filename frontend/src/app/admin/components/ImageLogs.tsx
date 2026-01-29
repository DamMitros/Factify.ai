'use client';

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useKeycloak } from '../../../auth/KeycloakProviderWrapper';
import GlassEffect from '../../components/GlassEffect';

interface ImageLogEntry {
  _id: string;
  timestamp?: string;
  filename?: string;
  image_preview?: string;
  ai_probability?: number;
  user_id?: string;
  overall?: {
    label: string;
    confidence: number;
  };
}

const ImageLogs: React.FC = () => {
  const { keycloak } = useKeycloak();
  const [logs, setLogs] = useState<ImageLogEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchLogs = async () => {
      if (!keycloak?.token) return;
      try {
        const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api'}/admin/image/logs`, {
          headers: { Authorization: `Bearer ${keycloak.token}` },
        });
        setLogs(response.data);
      } catch (error) { 
        console.error("Error fetching image logs:", error); 
      } finally { 
        setLoading(false); 
      }
    };
    fetchLogs();
  }, [keycloak?.token]);

  if (loading) return <div className="p-12 text-center text-gray-500 animate-pulse">Loading image history...</div>;

  return (
    <GlassEffect className="p-0 overflow-hidden border-white/10">
      <div className="p-6 border-b border-white/10 flex justify-between items-center bg-white/5">
        <h2 className="text-xl font-bold text-white">Global Image Analysis History</h2>
        <span className="text-xs text-gray-400 font-mono">Last 50 analyses</span>
      </div>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-white/5">
          <thead className="bg-white/5">
            <tr>
              <th className="px-6 py-4 text-left text-[10px] font-bold text-gray-400 uppercase tracking-widest">Preview</th>
              <th className="px-6 py-4 text-left text-[10px] font-bold text-gray-400 uppercase tracking-widest">Date & Time</th>
              <th className="px-6 py-4 text-left text-[10px] font-bold text-gray-400 uppercase tracking-widest">User</th>
              <th className="px-6 py-4 text-left text-[10px] font-bold text-gray-400 uppercase tracking-widest">AI Result</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {logs.map((log) => {
              const label = log.overall?.label || (log.ai_probability && log.ai_probability > 50 ? 'AI' : 'REAL');
              const isAI = label === 'AI';
              
              return (
                <tr key={log._id} className="hover:bg-white/5 transition-colors group">
                  <td className="px-6 py-4">
                    <div className="relative w-12 h-12 rounded-lg overflow-hidden border border-white/10 bg-black/40 group-hover:border-white/30 transition-all">
                      {log.image_preview ? (
                        <>
                          <img src={log.image_preview} alt="Analysed" className="w-full h-full object-cover group-hover:scale-110 transition-transform" />
                          {/* <div className="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center pointer-events-none">
                             <img src={log.image_preview} alt="Zoom" className="hidden group-hover:block fixed z-[100] top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-80 h-80 object-contain rounded-2xl shadow-[0_0_50px_rgba(0,0,0,0.8)] border-4 border-white/20" />
                          </div> */}
                        </>
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-[10px] text-gray-600 font-bold uppercase tracking-tighter">None</div>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 text-[11px] text-gray-400 whitespace-nowrap font-mono">
                    {log.timestamp ? new Date(log.timestamp).toLocaleString() : '-'}
                  </td>
                  <td className="px-6 py-4 text-xs font-mono text-gray-500 truncate max-w-[120px]">
                    {log.user_id || 'Anonymous'}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-col gap-1">
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${isAI ? 'bg-red-500/20 text-red-400' : 'bg-green-500/20 text-green-400'}`}>
                          {label}
                        </span>
                        <span className="text-xs font-mono font-bold text-white/70">{(log.ai_probability || 0).toFixed(1)}%</span>
                      </div>
                      <div className="w-24 h-1 bg-white/5 rounded-full overflow-hidden">
                        <div 
                          className={`h-full transition-all duration-1000 ${isAI ? 'bg-red-500' : 'bg-green-500'}`} 
                          style={{ width: `${log.ai_probability || 0}%` }}
                        />
                      </div>
                    </div>
                  </td>
                </tr>
              );
            })}
            {logs.length === 0 && (
              <tr>
                <td colSpan={4} className="px-6 py-12 text-center text-gray-500 italic">No image analysis logs found.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </GlassEffect>
  );
};

export default ImageLogs;