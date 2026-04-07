'use client';

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useKeycloak } from '../../../auth/KeycloakProviderWrapper';
import GlassEffect from '../../components/GlassEffect';

interface ReportItem {
  report_id: string;
  created_at?: string;
}

const ImageMonitoring: React.FC = () => {
  const { keycloak } = useKeycloak();
  const [reportList, setReportList] = useState<ReportItem[]>([]);
  const [selectedId, setSelectedId] = useState<string>('');
  const [fullReport, setFullReport] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!keycloak?.token) return;
    
    axios.get(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api'}/admin/image/reports`, {
      headers: { Authorization: `Bearer ${keycloak.token}` }
    })
    .then(res => {
      setReportList(res.data);
      if (res.data.length > 0) setSelectedId(res.data[0].report_id);
    })
    .catch(err => console.error("Error fetching Image reports list:", err));
  }, [keycloak?.token]);

  useEffect(() => {
    if (!selectedId || !keycloak?.token) return;
    
    setLoading(true);
    axios.get(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api'}/admin/image/reports/${selectedId}`, {
      headers: { Authorization: `Bearer ${keycloak.token}` }
    })
    .then(res => setFullReport(res.data))
    .catch(err => console.error("Error fetching full Image report:", err))
    .finally(() => setLoading(false));
  }, [selectedId, keycloak?.token]);

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between bg-white/5 p-4 rounded-2xl border border-white/10 gap-4">
        <h2 className="text-xl font-bold text-white tracking-tight">Image Analysis Reports</h2>
        
        {reportList.length > 0 ? (
          <select 
            value={selectedId} 
            onChange={(e) => setSelectedId(e.target.value)}
            className="bg-black/60 border border-white/20 text-white rounded-xl px-4 py-2.5 outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all text-sm min-w-[250px] shadow-xl backdrop-blur-md appearance-none"
          >
            {reportList.map(r => (
              <option key={r.report_id} value={r.report_id}>
                {r.report_id} {r.created_at ? `(${new Date(r.created_at).toLocaleDateString()})` : ''}
              </option>
            ))}
          </select>
        ) : (
          <div className="text-sm text-gray-400">No reports found in DB.</div>
        )}
      </div>

      {loading && (
        <div className="p-12 flex justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
        </div>
      )}

      {!loading && fullReport && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {fullReport.confusion_matrix_base64 && (
            <GlassEffect className="p-6 rounded-2xl">
              <h3 className="text-lg font-medium text-white mb-4">Confusion Matrix</h3>
              <div className="bg-white/5 rounded-xl border border-white/10 p-2 overflow-hidden flex justify-center">
                {fullReport.confusion_matrix_base64.includes("Image has not been") ? (
                  <p className="text-gray-400 p-8 text-center">{fullReport.confusion_matrix_base64}</p>
                ) : (
                  <img 
                    src={`data:image/png;base64,${fullReport.confusion_matrix_base64}`} 
                    alt={`Confusion Matrix for ${fullReport.report_id}`}
                    className="max-w-full rounded-lg"
                  />
                )}
              </div>
            </GlassEffect>
          )}

          <GlassEffect className="p-6 rounded-2xl flex flex-col h-full">
            <h3 className="text-lg font-medium text-white mb-4">Metrics</h3>
            <div className="bg-black/40 rounded-xl border border-white/10 p-4 flex-1 overflow-auto max-h-[400px] custom-scrollbar">
              <pre className="text-xs text-blue-300/80 font-mono">
                {JSON.stringify(fullReport.metrics, null, 2)}
              </pre>
            </div>
          </GlassEffect>
        </div>
      )}
    </div>
  );
};

export default ImageMonitoring;