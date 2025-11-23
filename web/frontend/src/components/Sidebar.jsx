import React from 'react';
import { Upload, Mic, FileText } from 'lucide-react';

const Sidebar = ({ activeTab, setActiveTab }) => {
  const tabs = [
    { id: 'record', label: 'Record', icon: Mic },
    { id: 'upload', label: 'Upload', icon: Upload },
    { id: 'transcript', label: 'Transcript', icon: FileText },
  ];

  return (
    <div className="w-64 bg-sidebar border-r border-gray-800 flex flex-col">
      <div className="p-6">
        <div className="w-8 h-8 bg-blue-500 rounded-lg mb-2 hidden"></div> 
        {/* Logo placeholder */}
      </div>

      <nav className="flex-1 px-4 space-y-2">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                isActive 
                  ? 'bg-blue-600 text-white shadow-lg shadow-blue-900/20' 
                  : 'text-text-secondary hover:bg-gray-800 hover:text-white'
              }`}
            >
              <Icon className="w-5 h-5" />
              <span className="font-medium">{tab.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="p-4 border-t border-gray-800 text-xs text-text-secondary text-center">
        FonixFlow Web v1.0
      </div>
    </div>
  );
};

export default Sidebar;
