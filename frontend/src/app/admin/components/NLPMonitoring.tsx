'use client';

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useKeycloak } from '../../../auth/KeycloakProviderWrapper';

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
          const url = URL.createObjectURL(matrixRes.value.data);
          setConfusionMatrixUrl(url);
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
      if (newSet.has(idx)) {
        newSet.delete(idx);
      } else {
        newSet.add(idx);
      }
      return newSet;
    });
  };

  if (loading && !metrics) return <div>Loading NLP data...</div>;

  return (
    <div className="space-y-8">
      <div className="bg-white/40 dark:bg-black/40 backdrop-blur-sm p-6 rounded-lg shadow-sm border border-white/20">
        <label htmlFor="report-select" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Select Model Report:</label>
        <select
          id="report-select"
          value={selectedReport}
          onChange={(e) => setSelectedReport(e.target.value)}
          className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md bg-white/50 dark:bg-black/50 text-gray-900 dark:text-white"
        >
          {reports.map((report) => (
            <option key={report} value={report}>{report}</option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {metrics && Object.entries(metrics).map(([key, value]) => {
          if (typeof value === 'object' && value !== null) {
             return (
               <div key={key} className="bg-white/40 dark:bg-black/40 backdrop-blur-sm p-6 rounded-lg shadow-sm border border-white/20">
                 <h3 className="text-gray-500 dark:text-gray-400 text-sm font-medium uppercase mb-4 border-b border-white/20 pb-2">{key.replace(/_/g, ' ')}</h3>
                 <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                   {Object.entries(value).map(([subKey, subValue]) => {
                     if (typeof subValue === 'object' && subValue !== null) {
                        return (
                          <div key={subKey} className="col-span-full mt-2">
                             <h4 className="text-xs font-bold text-gray-600 dark:text-gray-300 uppercase mb-2">{subKey}</h4>
                             <div className="grid grid-cols-2 md:grid-cols-4 gap-2 bg-gray-50/50 dark:bg-gray-800/50 p-3 rounded">
                               {Object.entries(subValue).map(([deepKey, deepValue]) => (
                                 <div key={deepKey}>
                                   <span className="text-xs text-gray-400 uppercase block">{deepKey}</span>
                                   <span className="font-mono text-sm text-gray-900 dark:text-gray-100">
                                     {typeof deepValue === 'number' ? deepValue.toFixed(4) : String(deepValue)}
                                   </span>
                                 </div>
                               ))}
                             </div>
                          </div>
                        );
                     }
                     return (
                       <div key={subKey}>
                         <span className="text-xs text-gray-400 uppercase block">{subKey}</span>
                         <span className="font-bold text-gray-800 dark:text-gray-200">
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
            <div key={key} className="bg-white/40 dark:bg-black/40 backdrop-blur-sm p-6 rounded-lg shadow-sm border border-white/20">
              <h3 className="text-gray-500 dark:text-gray-400 text-sm font-medium uppercase">{key.replace(/_/g, ' ')}</h3>
              <p className="text-2xl font-bold text-gray-800 dark:text-gray-200">
                {typeof value === 'number' ? value.toFixed(4) : String(value)}
              </p>
            </div>
          );
        })}
      </div>

      <div className="bg-white/40 dark:bg-black/40 backdrop-blur-sm p-6 rounded-lg shadow-sm border border-white/20">
        <h3 className="text-lg font-semibold mb-4 text-gray-900 dark:text-white">Confusion Matrix</h3>
        <div className="flex justify-center">
          {confusionMatrixUrl ? (
            <img src={confusionMatrixUrl} alt="Confusion Matrix" className="max-w-full h-auto rounded shadow-lg" />
          ) : (
            <p className="text-gray-500 dark:text-gray-400">No confusion matrix available</p>
          )}
        </div>
      </div>

      <div className="bg-white/40 dark:bg-black/40 backdrop-blur-sm p-6 rounded-lg shadow-sm border border-white/20">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Failure Analysis</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400 italic">Note: Label 1 indicates AI, Label 0 indicates Human</p>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full leading-normal">
            <thead>
              <tr>
                <th className="px-5 py-3 border-b border-gray-200 dark:border-gray-700 bg-gray-100/50 dark:bg-gray-800/50 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider">True Label</th>
                <th className="px-5 py-3 border-b border-gray-200 dark:border-gray-700 bg-gray-100/50 dark:bg-gray-800/50 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider">Predicted</th>
                <th className="px-5 py-3 border-b border-gray-200 dark:border-gray-700 bg-gray-100/50 dark:bg-gray-800/50 text-left text-xs font-semibold text-gray-600 dark:text-gray-300 uppercase tracking-wider">Text Snippet</th>
              </tr>
            </thead>
            <tbody>
              {failures.slice(0, 50).map((fail, idx) => {
                const isExpanded = expandedFailures.has(idx);
                const text = fail.text || fail.content || '-';
                const displayText = isExpanded ? text : (text.length > 100 ? text.substring(0, 100) + '...' : text);
                
                return (
                  <tr key={idx}>
                    <td className="px-5 py-5 border-b border-gray-200 dark:border-gray-700 bg-transparent text-sm align-top">
                      <span className="relative inline-block px-3 py-1 font-semibold text-green-900 leading-tight">
                        <span aria-hidden className="absolute inset-0 bg-green-200 opacity-50 rounded-full"></span>
                        <span className="relative">{fail.true_label !== undefined ? fail.true_label : (fail.label || '-')}</span>
                      </span>
                    </td>
                    <td className="px-5 py-5 border-b border-gray-200 dark:border-gray-700 bg-transparent text-sm align-top">
                      <span className="relative inline-block px-3 py-1 font-semibold text-red-900 leading-tight">
                        <span aria-hidden className="absolute inset-0 bg-red-200 opacity-50 rounded-full"></span>
                        <span className="relative">{fail.pred_label !== undefined ? fail.pred_label : (fail.prediction || '-')}</span>
                      </span>
                    </td>
                    <td className="px-5 py-5 border-b border-gray-200 dark:border-gray-700 bg-transparent text-sm">
                      <p className="text-gray-900 dark:text-gray-100 break-words min-w-[300px]">{displayText}</p>
                      {text.length > 100 && (
                        <button onClick={() => toggleFailureExpand(idx)} className="text-blue-500 hover:text-blue-400 text-xs mt-1">
                          {isExpanded ? 'Show less' : 'Show more'}
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">Showing first 50 failures.</p>
        </div>
      </div>
    </div>
  );
};

export default NLPMonitoring;
