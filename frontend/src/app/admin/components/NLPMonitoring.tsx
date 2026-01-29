'use client';

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useKeycloak } from '../../../auth/KeycloakProviderWrapper';
import GlassEffect from '../../components/GlassEffect';

interface Metrics {
  accuracy?: number;
  f1_score?: number;
  loss?: number;
  [key: string]: any;
}

interface Failure {
  text?: string;
  true_label?: number | string;
  pred_label?: number | string;
  [key: string]: any;
}

const NLPMonitoring: React.FC = () => {
  const { keycloak } = useKeycloak();
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [confusionMatrixUrl, setConfusionMatrixUrl] = useState<string | null>(null);
  const [failures, setFailures] = useState<Failure[]>([]);
  const [loading, setLoading] = useState(true);
  const [reports, setReports] = useState<string[]>([]);
  const [selectedReport, setSelectedReport] = useState<string>('');
  const [expandedFailures, setExpandedFailures] = useState<Set<number>>(new Set());

  useEffect(() => {
    const fetchReports = async () => {
      if (!keycloak?.token) return;
      try {
        const response = await axios.get(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api'}/admin/nlp/reports`, {
          headers: { Authorization: `Bearer ${keycloak.token}` }
        });
        setReports(response.data);
        if (response.data.length > 0) {
            const defaultReport = response.data.includes('mc_dropout_train_0.2') 
            ? 'mc_dropout_train_0.2' 
            : response.data[0];
            setSelectedReport(defaultReport);
        }
      } catch (error) {
        console.error("Error fetching reports:", error);
      }
    };
    fetchReports();
  }, [keycloak?.token]);

  useEffect(() => {
    const fetchData = async () => {
      if (!keycloak?.token || !selectedReport) return;
      setLoading(true);
      const headers = { Authorization: `Bearer ${keycloak.token}` };
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api';

      try {
        const [metricsRes, failuresRes, matrixRes] = await Promise.allSettled([
          axios.get(`${baseUrl}/admin/nlp/metrics?report_id=${selectedReport}`, { headers }),
          axios.get(`${baseUrl}/admin/nlp/failures?report_id=${selectedReport}`, { headers }),
          axios.get(`${baseUrl}/admin/nlp/confusion_matrix?report_id=${selectedReport}`, { headers, responseType: 'blob' })
        ]);

        if (metricsRes.status === 'fulfilled') setMetrics(metricsRes.value.data);
        if (failuresRes.status === 'fulfilled') setFailures(failuresRes.value.data);
        if (matrixRes.status === 'fulfilled') {
          setConfusionMatrixUrl(URL.createObjectURL(matrixRes.value.data));
        }
      } catch (error) {
        console.error("Error fetching NLP data:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [keycloak?.token, selectedReport]);

  const toggleFailureExpand = (idx: number) => {
    setExpandedFailures(prev => {
      const newSet = new Set(prev);
      if (newSet.has(idx)) newSet.delete(idx);
      else newSet.add(idx);
      return newSet;
    });
  };

  if (loading && !metrics) return <div className="text-center text-gray-400 p-8 animate-pulse">Loading NLP data...</div>;

  return (
    <div className="space-y-6">
      <GlassEffect className="p-4 rounded-2xl flex items-center gap-4">
        <label htmlFor="report-select" className="text-sm font-medium text-gray-300 whitespace-nowrap">
            Active Model Report:
        </label>
        <select
          id="report-select"
          value={selectedReport}
          onChange={(e) => setSelectedReport(e.target.value)}
          className="flex-1 max-w-md px-4 py-2 bg-black/40 text-white border border-white/20 rounded-lg focus:outline-none focus:border-blue-500/50 text-sm transition-colors cursor-pointer"
        >
          {reports.map((report) => (
            <option key={report} value={report}>{report}</option>
          ))}
        </select>
      </GlassEffect>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <GlassEffect className="p-6 rounded-2xl flex flex-col">
            <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-blue-500"></span>
                Performance Metrics
            </h3>
            
            <div className="space-y-4 flex-1">
                {metrics && Object.entries(metrics).map(([key, value]) => {
                if (typeof value === 'object' && value !== null) {
                    return (
                    <div key={key} className="p-4 rounded-xl bg-white/5 border border-white/5">
                        <h4 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3 border-b border-white/10 pb-2">
                            {key.replace(/_/g, ' ')}
                        </h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {Object.entries(value).map(([subKey, subValue]) => {
                                if (typeof subValue === 'object' && subValue !== null) {
                                    return (
                                        <div key={subKey} className="col-span-full">
                                            <h5 className="text-[10px] font-bold text-gray-500 uppercase mb-2">{subKey}</h5>
                                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                                                {Object.entries(subValue).map(([deepKey, deepValue]) => (
                                                    <div key={deepKey} className="bg-black/20 p-2 rounded text-center">
                                                        <div className="text-[10px] text-gray-500 uppercase">{deepKey}</div>
                                                        <div className="font-mono text-sm text-white font-bold">
                                                            {typeof deepValue === 'number' ? deepValue.toFixed(3) : String(deepValue)}
                                                        </div>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    );
                                }
                                return (
                                    <div key={subKey} className="flex justify-between items-center bg-black/20 p-2 rounded">
                                        <span className="text-xs text-gray-500 uppercase">{subKey}</span>
                                        <span className="font-mono text-sm text-white font-bold">
                                            {typeof subValue === 'number' ? subValue.toFixed(4) : String(subValue)}
                                        </span>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                    );
                }

                return (
                    <div key={key} className="flex justify-between items-center p-3 rounded-lg bg-blue-500/5 border border-blue-500/10 hover:bg-blue-500/10 transition-colors">
                        <span className="text-gray-300 uppercase text-xs font-bold tracking-wider">{key.replace(/_/g, ' ')}</span>
                        <span className="text-blue-300 font-mono font-bold text-lg">
                            {typeof value === 'number' ? value.toFixed(4) : String(value)}
                        </span>
                    </div>
                );
                })}
            </div>
        </GlassEffect>

        <GlassEffect className="p-6 rounded-2xl flex flex-col border-t-4 border-t-purple-500">
            <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                Confusion Matrix
            </h3>
            <div className="flex-1 flex items-center justify-center p-4 bg-black/20 rounded-xl border border-white/5 min-h-[300px]">
                {confusionMatrixUrl ? (
                    <img src={confusionMatrixUrl} alt="Confusion Matrix" className="max-w-full h-auto rounded shadow-lg" />
                ) : (
                    <div className="text-gray-500 italic flex flex-col items-center gap-2">
                         <svg className="w-8 h-8 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                        <span>No confusion matrix available</span>
                    </div>
                )}
            </div>
        </GlassEffect>
      </div>

      <GlassEffect className="p-6 rounded-2xl overflow-hidden border-t-4 border-t-red-500">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 gap-4">
                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                    Prediction Failures
                </h3>
                <div className="flex gap-2 text-xs">
                     <span className="px-2 py-1 bg-green-500/10 text-green-400 border border-green-500/20 rounded">True Label</span>
                     <span className="px-2 py-1 bg-red-500/10 text-red-400 border border-red-500/20 rounded">Predicted</span>
                </div>
            </div>
            
            <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                    <thead className="bg-white/5 border-b border-white/10">
                        <tr>
                            <th className="p-4 text-xs font-bold text-gray-400 uppercase tracking-widest w-24">True</th>
                            <th className="p-4 text-xs font-bold text-gray-400 uppercase tracking-widest w-24">Pred</th>
                            <th className="p-4 text-xs font-bold text-gray-400 uppercase tracking-widest">Content snippet</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5 text-sm">
                    {failures.slice(0, 50).map((fail, idx) => {
                        const isExpanded = expandedFailures.has(idx);
                        const text = fail.text || fail.content || '-';
                        const displayText = isExpanded ? text : (text.length > 120 ? text.substring(0, 120) + '...' : text);
                        
                        return (
                        <tr key={idx} className="hover:bg-white/5 group transition-colors">
                            <td className="p-4 align-top">
                                <span className="inline-flex items-center justify-center px-2 py-1 rounded bg-green-500/10 text-green-400 text-xs font-bold border border-green-500/20 min-w-[30px]">
                                    {fail.true_label}
                                </span>
                            </td>
                            <td className="p-4 align-top">
                                <span className="inline-flex items-center justify-center px-2 py-1 rounded bg-red-500/10 text-red-400 text-xs font-bold border border-red-500/20 min-w-[30px]">
                                    {fail.pred_label}
                                </span>
                            </td>
                            <td className="p-4 text-gray-300 align-top">
                                <p className="leading-relaxed text-gray-300/90 font-light break-words">
                                    {displayText}
                                </p>
                                {text.length > 120 && (
                                    <button 
                                        onClick={() => toggleFailureExpand(idx)} 
                                        className="mt-2 text-blue-400 hover:text-blue-300 text-xs font-medium transition-colors flex items-center gap-1 opacity-60 hover:opacity-100"
                                    >
                                        {isExpanded ? 'Collapse' : 'Show full text'}
                                        <svg className={`w-3 h-3 transition-transform ${isExpanded ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
                                    </button>
                                )}
                            </td>
                        </tr>
                        );
                    })}
                    {failures.length === 0 && (
                        <tr>
                            <td colSpan={3} className="p-8 text-center text-gray-500 italic">No failures recorded or data unavailable.</td>
                        </tr>
                    )}
                    </tbody>
                </table>
            </div>
      </GlassEffect>
    </div>
  );
};

export default NLPMonitoring;