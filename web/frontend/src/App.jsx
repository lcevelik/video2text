import React, { useState } from 'react';
import { Mic, Settings } from 'lucide-react';
import Sidebar from './components/Sidebar';
import UploadArea from './components/UploadArea';
import TranscriptView from './components/TranscriptView';

function App() {
  const [activeTab, setActiveTab] = useState('upload');
  const [transcript, setTranscript] = useState(null);

  return (
    <div className="flex flex-col h-screen bg-background text-text-primary overflow-hidden relative">
      {/* Animated Background Blobs */}
      <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-accent/10 rounded-full blur-3xl animate-blob mix-blend-screen"></div>
        <div className="absolute top-0 right-1/4 w-96 h-96 bg-success/10 rounded-full blur-3xl animate-blob animation-delay-2000 mix-blend-screen"></div>
        <div className="absolute -bottom-32 left-1/3 w-96 h-96 bg-info/10 rounded-full blur-3xl animate-blob animation-delay-4000 mix-blend-screen"></div>
      </div>

      {/* Top Bar */}
      <div className="h-16 bg-sidebar/80 backdrop-blur-md border-b border-border flex items-center justify-center shrink-0 relative z-10">
        <div className="flex items-center gap-3">
          <span className="text-2xl font-bold bg-gradient-to-r from-accent to-success bg-clip-text text-transparent tracking-wide">
            FonixFlow
          </span>
        </div>
      </div>

      {/* Main Layout: Content Left, Sidebar Right */}
      <div className="flex flex-1 overflow-hidden relative z-10">
        {/* Content Area */}
        <div className="flex-1 p-6 overflow-auto bg-transparent">
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

          {activeTab === 'settings' && (
            <div className="flex flex-col items-center justify-center h-full text-text-secondary p-4 text-center">
              <Settings className="w-16 h-16 mb-4 opacity-50" />
              <h2 className="text-xl font-semibold">Settings</h2>
              <p className="mt-2">Web settings are not yet implemented.</p>
            </div>
          )}
        </div>

        {/* Right Sidebar (Vertical Tab Bar) */}
        <Sidebar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
        />
      </div>
    </div>
  );
}

export default App;
