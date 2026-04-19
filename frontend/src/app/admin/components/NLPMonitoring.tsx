'use client';

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useKeycloak } from '../../../auth/KeycloakProviderWrapper';
import GlassEffect from '../../components/GlassEffect';

interface ReportItem {
  report_id: string;
  created_at?: string;
}

const ITEMS_PER_PAGE = 10;

const NLPMonitoring: React.FC = () => {
  const { keycloak } = useKeycloak();
  const [reportList, setReportList] = useState<ReportItem[]>([]);
  const [selectedId, setSelectedId] = useState<string>('');
  const [fullReport, setFullReport] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedFailText, setSelectedFailText] = useState<string | null>(null);

  useEffect(() => {
    if (!keycloak?.token) return;
    
    axios.get(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api'}/admin/nlp/reports`, {
      headers: { Authorization: `Bearer ${keycloak.token}` }
    })
    .then(res => {
      setReportList(res.data);
      if (res.data.length > 0) setSelectedId(res.data[0].report_id);
    })
    .catch(err => console.error("Error fetching NLP reports list:", err));
  }, [keycloak?.token]);

  useEffect(() => {
    if (!selectedId || !keycloak?.token) return;
    
    setLoading(true);
    axios.get(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api'}/admin/nlp/reports/${selectedId}`, {
      headers: { Authorization: `Bearer ${keycloak.token}` }
    })
    .then(res => {
      setFullReport(res.data);
      setCurrentPage(1); 
    })
    .catch(err => console.error("Error fetching full NLP report:", err))
    .finally(() => setLoading(false));
  }, [selectedId, keycloak?.token]);


  const totalFails = fullReport?.fails?.length || 0;
  const totalPages = Math.ceil(totalFails / ITEMS_PER_PAGE);
  const paginatedFails = fullReport?.fails?.slice(
    (currentPage - 1) * ITEMS_PER_PAGE, 
    currentPage * ITEMS_PER_PAGE
  ) || [];

  return (
    <div className="space-y-6">
      <div className="flex flex-col md:flex-row md:items-center justify-between bg-white/5 p-4 rounded-2xl border border-white/10 gap-4">
        <h2 className="text-xl font-bold text-white tracking-tight">NLP Analysis Reports</h2>
        
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
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 relative">
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

          {fullReport.fails && fullReport.fails.length > 0 && (
            <div className="lg:col-span-2">
              <GlassEffect className="p-6 rounded-2xl">
                <h3 className="text-lg font-medium text-white mb-4">Model Failures ({totalFails})</h3>
                <div className="overflow-x-auto rounded-xl border border-white/10">
                  <table className="w-full text-left text-sm text-gray-400">
                    <thead className="bg-white/5 text-gray-200 uppercase text-xs">
                      <tr>
                        <th className="px-4 py-3 font-medium">Text Snippet (Click to view full)</th>
                        <th className="px-4 py-3 font-medium text-center w-32">True Label</th>
                        <th className="px-4 py-3 font-medium text-center w-32">Prediction</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5 bg-black/20">
                      {paginatedFails.map((fail: any, idx: number) => (
                        <tr key={idx} className="hover:bg-white/5 transition-colors">
                          <td 
                            className="px-4 py-3 max-w-md truncate cursor-pointer hover:text-blue-400 transition-colors" 
                            title="Click to view full text"
                            onClick={() => setSelectedFailText(fail.text)}
                          >
                            {fail.text}
                          </td>
                          <td className="px-4 py-3 text-center">
                             <span className="bg-gray-500/20 px-2 py-1 rounded text-xs border border-gray-500/20">{fail.true_label}</span>
                          </td>
                          <td className="px-4 py-3 text-center">
                             <span className="bg-red-500/20 text-red-400 px-2 py-1 rounded text-xs border border-red-500/20">{fail.pred_label}</span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>

                {totalPages > 1 && (
                  <div className="flex items-center justify-between mt-4 px-2 text-sm text-gray-400">
                    <button 
                      onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                      disabled={currentPage === 1}
                      className="px-3 py-1.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg disabled:opacity-30 transition-all cursor-pointer"
                    >
                      Previous
                    </button>
                    <span>Page {currentPage} of {totalPages}</span>
                    <button 
                      onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                      disabled={currentPage === totalPages}
                      className="px-3 py-1.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg disabled:opacity-30 transition-all cursor-pointer"
                    >
                      Next
                    </button>
                  </div>
                )}
              </GlassEffect>
            </div>
          )}
        </div>
      )}

      {selectedFailText && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
          <GlassEffect className="w-full max-w-3xl p-6 rounded-2xl relative max-h-[85vh] flex flex-col shadow-2xl border border-white/20">
            <button 
              onClick={() => setSelectedFailText(null)}
              className="absolute top-4 right-4 text-gray-400 hover:text-white bg-white/5 hover:bg-red-500/50 rounded-full w-8 h-8 flex items-center justify-center transition-all"
            >
              ✕
            </button>
            <h3 className="text-xl font-bold text-white mb-4 pr-8">Full Text Analysis</h3>
            <div className="overflow-y-auto pr-2 pb-2 text-gray-300 text-sm leading-relaxed whitespace-pre-wrap custom-scrollbar flex-1">
              {selectedFailText}
            </div>
          </GlassEffect>
        </div>
      )}

    </div>
  );
};

export default NLPMonitoring;