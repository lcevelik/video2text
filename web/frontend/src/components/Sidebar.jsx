import React from 'react';
import { Mic, Folder, FileText, Settings } from 'lucide-react';

const Sidebar = ({ activeTab, setActiveTab }) => {
  const tabs = [
    { id: 'record', icon: Mic, label: 'Record' },
    { id: 'upload', icon: Folder, label: 'Upload' },
    { id: 'transcript', icon: FileText, label: 'Transcript' },
    { id: 'settings', icon: Settings, label: 'Settings' },
  ];

  return (
    <div className="flex flex-col gap-[20px] w-full">
      {tabs.map((tab) => {
        const Icon = tab.icon;
        const isActive = activeTab === tab.id;

        return (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`
              flex items-center gap-[15px] px-[15px] py-[15px] rounded-full font-bold text-sm transition-all duration-200 w-full
              ${isActive
                ? 'bg-[#00dcd0] text-white shadow-lg scale-105 border-0'
                : 'bg-transparent text-gray-300 border-[3px] border-[#444] hover:bg-[#2a2a2a] hover:border-[#00dcd0] hover:text-white'
              }
            `}
          >
            <Icon size={22} strokeWidth={2.5} />
            <span className="text-2xl font-bold">{tab.label}</span>
          </button>
        );
      })}
    </div>
  );
};

export default Sidebar;