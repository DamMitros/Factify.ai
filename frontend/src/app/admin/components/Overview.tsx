import React from 'react';

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
    return <div className="text-center p-4">Loading stats...</div>;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <div className="bg-white/40 dark:bg-black/40 backdrop-blur-sm p-6 rounded-lg shadow-sm border-l-4 border-blue-500">
        <h3 className="text-gray-600 dark:text-gray-300 text-sm font-medium uppercase">Users</h3>
        <p className="text-3xl font-bold text-gray-800 dark:text-white">{stats.users}</p>
      </div>
      <div className="bg-white/40 dark:bg-black/40 backdrop-blur-sm p-6 rounded-lg shadow-sm border-l-4 border-green-500">
        <h3 className="text-gray-600 dark:text-gray-300 text-sm font-medium uppercase">Text Analyses</h3>
        <p className="text-3xl font-bold text-gray-800 dark:text-white">{stats.text_analyses}</p>
      </div>
      <div className="bg-white/40 dark:bg-black/40 backdrop-blur-sm p-6 rounded-lg shadow-sm border-l-4 border-purple-500">
        <h3 className="text-gray-600 dark:text-gray-300 text-sm font-medium uppercase">Image Analyses</h3>
        <p className="text-3xl font-bold text-gray-800 dark:text-white">{stats.image_analyses}</p>
      </div>
      <div className="bg-white/40 dark:bg-black/40 backdrop-blur-sm p-6 rounded-lg shadow-sm border-l-4 border-yellow-500">
        <h3 className="text-gray-600 dark:text-gray-300 text-sm font-medium uppercase">System Status</h3>
        <p className={`text-3xl font-bold ${stats.status === 'Healthy' ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>
          {stats.status}
        </p>
      </div>
    </div>
  );
};

export default Overview;
