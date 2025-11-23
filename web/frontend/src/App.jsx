import React, { useState } from 'react';
import { Upload, Mic, FileText, Settings, Menu } from 'lucide-react';
import Sidebar from './components/Sidebar';
import UploadArea from './components/UploadArea';
import TranscriptView from './components/TranscriptView';

function App() {
  const [activeTab, setActiveTab] = useState('upload');
  const [transcript, setTranscript] = useState(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen bg-background text-text-primary overflow-hidden">
      {/* Sidebar */}
      <Sidebar 
        activeTab={activeTab} 
        setActiveTab={setActiveTab} 
        isOpen={isSidebarOpen} 
        onClose={() => setIsSidebarOpen(false)} 
      />

      {/* Main Content */}
      <div className="flex-1 flex flex-col w-full relative">
        {/* Top Bar */}
        <div className="h-14 bg-sidebar border-b border-gray-800 flex items-center px-4 md:px-6 justify-between shrink-0">
          <div className="flex items-center gap-3">
            <button 
              onClick={() => setIsSidebarOpen(true)}
              className="p-1 -ml-2 text-text-secondary hover:bg-gray-700 rounded-lg md:hidden"
            >
              <Menu className="w-6 h-6" />
            </button>
            <span className="text-lg md:text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent truncate">
              FonixFlow Web
            </span>
          </div>
          <div className="flex items-center gap-4">
            <button className="p-2 hover:bg-gray-700 rounded-full transition-colors">
              <Settings className="w-5 h-5 text-text-secondary" />
            </button>
          </div>
        </div>

        {/* Content Area */}
        <div className="flex-1 p-4 md:p-6 overflow-auto w-full">
          {activeTab === 'upload' && (
            <UploadArea 
              onTranscriptionComplete={(data) => {
                setTranscript(data);
                setActiveTab('transcript');
              }} 
            />
          )}
          
          {activeTab === 'transcript' && (
            <TranscriptView 
              data={transcript} 
              onBack={() => setActiveTab('upload')}
            />
          )}

          {activeTab === 'record' && (
             <div className="flex flex-col items-center justify-center h-full text-text-secondary p-4 text-center">
               <Mic className="w-16 h-16 mb-4 opacity-50" />
               <h2 className="text-xl font-semibold">Recording Coming Soon</h2>
               <p className="mt-2">Browser-based recording is under development.</p>
             </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
