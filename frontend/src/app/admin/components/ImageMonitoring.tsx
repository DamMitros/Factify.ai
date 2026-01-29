'use client';

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useKeycloak } from '../../../auth/KeycloakProviderWrapper';
import GlassEffect from '../../components/GlassEffect';

const ImageMonitoring: React.FC = () => {
  const { keycloak } = useKeycloak();
  const [metrics, setMetrics] = useState<any | null>(null);
  const [confusionMatrixUrl, setConfusionMatrixUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedModel, setSelectedModel] = useState<string>('best_model');
  const availableModels = ['best_model'];

  useEffect(() => {
    const fetchData = async () => {
      if (!keycloak?.token) return;
      setLoading(true);
      const headers = { Authorization: `Bearer ${keycloak.token}` };
      const baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080/api';

      try {
        const [metricsRes, matrixRes] = await Promise.allSettled([
          axios.get(`${baseUrl}/admin/image/metrics`, { headers }),
          axios.get(`${baseUrl}/admin/image/confusion_matrix`, { headers, responseType: 'blob' })
        ]);

        if (metricsRes.status === 'fulfilled') setMetrics(metricsRes.value.data);
        if (matrixRes.status === 'fulfilled') {
          setConfusionMatrixUrl(URL.createObjectURL(matrixRes.value.data));
        }
      } catch (error) {
        console.error("Error fetching Image AI data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [keycloak?.token, selectedModel]);

  if (loading && !metrics) return <div className="text-center text-gray-400 p-8">Loading AI Metrics...</div>;

  return (
    <div className="space-y-6">
      <GlassEffect className="p-4 rounded-2xl flex items-center gap-4">
        <label htmlFor="image-model-select" className="text-sm font-medium text-gray-300 whitespace-nowrap">Select Vision Model:</label>
        <select
          id="image-model-select"
          value={selectedModel}
          onChange={(e) => setSelectedModel(e.target.value)}
          className="flex-1 max-w-md px-4 py-2 bg-black/40 text-white border border-white/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
        >
          {availableModels.map((model) => (
            <option key={model} value={model.split(' ')[0]}>{model}</option>
          ))}
        </select>
      </GlassEffect>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <GlassEffect className="p-6 rounded-2xl">
          <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-blue-500"></span>
            Classification Report
          </h3>
          {metrics ? (
             <div className="space-y-4">
               {Object.entries(metrics).map(([key, value]: [string, any]) => {
                 if (typeof value === 'object') {
                   return (
                     <div key={key} className="p-4 rounded-xl bg-white/5 border border-white/5">
                        <h4 className="text-sm font-bold text-gray-300 uppercase mb-3">{key}</h4>
                        <div className="grid grid-cols-3 gap-2 text-xs">
                           <div className="text-center">
                             <div className="text-gray-500">Precision</div>
                             <div className="text-white font-mono">{value.precision?.toFixed(3)}</div>
                           </div>
                           <div className="text-center">
                             <div className="text-gray-500">Recall</div>
                             <div className="text-white font-mono">{value.recall?.toFixed(3)}</div>
                           </div>
                           <div className="text-center">
                             <div className="text-gray-500">F1-Score</div>
                             <div className="text-white font-mono">{value['f1-score']?.toFixed(3)}</div>
                           </div>
                        </div>
                     </div>
                   );
                 }
                 return (
                   <div key={key} className="flex justify-between items-center p-3 rounded-lg bg-blue-500/10 border border-blue-500/20">
                     <span className="text-gray-300 uppercase text-xs font-bold">{key}</span>
                     <span className="text-blue-300 font-mono font-bold text-lg">{typeof value === 'number' ? value.toFixed(4) : value}</span>
                   </div>
                 );
               })}
             </div>
          ) : (
             <p className="text-gray-500">Metrics not found on server.</p>
          )}
        </GlassEffect>

        <GlassEffect className="p-6 rounded-2xl flex flex-col items-center justify-center">
          <h3 className="text-xl font-bold text-white mb-6 w-full text-left flex items-center gap-2">
             <span className="w-2 h-2 rounded-full bg-purple-500"></span>
             Confusion Matrix
          </h3>
          {confusionMatrixUrl ? (
            <div className="relative rounded-xl overflow-hidden border border-white/10 shadow-2xl bg-black/50">
                <img src={confusionMatrixUrl} alt="Confusion Matrix" className="max-w-full h-auto" />
            </div>
          ) : (
            <div className="text-gray-500 italic py-12">Matrix visualization not available</div>
          )}
        </GlassEffect>
      </div>
    </div>
  );
};

export default ImageMonitoring;