import React from 'react';
import GlassEffect from '../../components/GlassEffect';

interface Stats {
  users: number;
  text_analyses: number;
  image_analyses: number;
  status: string;
}

interface OverviewProps {
  stats: Stats | null;
}

const Overview: React.FC<OverviewProps> = ({ stats }) => {
  if (!stats) {
    return <div className="text-center p-12 text-gray-500 animate-pulse">Gathering system statistics...</div>;
  }

  const items = [
    { label: 'Total Users', value: stats.users, color: 'bg-blue-500', icon: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197' },
    { label: 'Text Analyses', value: stats.text_analyses, color: 'bg-green-500', icon: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z' },
    { label: 'Image Analyses', value: stats.image_analyses, color: 'bg-purple-500', icon: 'M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z' },
    { label: 'System Health', value: stats.status, color: 'bg-yellow-500', icon: 'M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z' },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {items.map((item, idx) => (
        <GlassEffect key={idx} className="p-12 relative overflow-hidden group">
          <span className={`absolute left-0 top-0 h-full w-1 ${item.color}`}></span>
          <div className="mr-3">
            <div className="absolute -right-4 -bottom-4 opacity-5 group-hover:opacity-10 transition-opacity">
              <svg className="w-24 h-24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                 <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d={item.icon} />
              </svg>
            </div>

            <h3 className="text-gray-400 text-xs font-semibold tracking-tight leading-none">{item.label}</h3>
            <p className={`text-xxl font-bold ${item.label === 'System Health' && item.value !== 'Healthy' ? 'text-red-400' : 'text-white'}`}>{item.value}</p>
          </div>
        </GlassEffect>
      ))}
    </div>
  );
};

export default Overview;
