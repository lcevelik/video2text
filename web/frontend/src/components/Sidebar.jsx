import React from 'react';
import { Upload, Mic, FileText, Settings } from 'lucide-react';

const Sidebar = ({ activeTab, setActiveTab }) => {
  const tabs = [
    { id: 'record', label: 'Record', icon: Mic },
    { id: 'upload', label: 'Upload', icon: Upload },
    { id: 'transcript', label: 'Transcript', icon: FileText },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <div className="w-[260px] bg-sidebar/80 backdrop-blur-md flex flex-col gap-4 py-8 px-4 shrink-0 border-l border-border">
      {tabs.map((tab) => {
        const Icon = tab.icon;
        const isActive = activeTab === tab.id;

        return (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`
              w-full flex flex-col items-center justify-center gap-2 py-4 rounded-xl transition-all duration-300 border-2 group
              ${isActive
                ? 'bg-gradient-to-r from-accent to-success text-white border-transparent shadow-lg shadow-accent/20'
                : 'bg-transparent text-text-primary border-border hover:bg-bg-tertiary hover:border-accent/50 hover:text-white'
              }
            `}
          >
            <Icon className={`w-8 h-8 transition-transform duration-300 ${isActive ? '' : 'group-hover:scale-110'}`} />
            <span className="font-bold text-lg">{tab.label}</span>
          </button>
        );
      })}
    </div>
  );
};

export default Sidebar;