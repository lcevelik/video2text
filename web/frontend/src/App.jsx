import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import UploadArea from './components/UploadArea';
import TranscriptView from './components/TranscriptView';
import RecordView from './components/RecordView';
import SettingsView from './components/SettingsView';
import logo from './assets/logo.png';

function App() {
  const [activeTab, setActiveTab] = useState('record');
  const [transcript, setTranscript] = useState(null);

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#1a1a1a] to-[#2d2d30] flex items-center justify-center p-8">

      {/* 800x600 Frame with 15px internal padding */}
      <div className="w-[900px] h-[700px] bg-[#2d2d30] text-white font-sans flex flex-col shadow-2xl overflow-hidden rounded-2xl border-2 border-[#555] p-[15px]">

        {/* Inner container */}
        <div className="flex flex-col h-full bg-[#2d2d30] rounded-xl overflow-hidden relative">

          {/* Top Header Bar with Logo */}
          <div className="bg-[#3c3c3c] border-b border-[#1e1e1e] py-2 flex justify-center shrink-0">
            <img src={logo} alt="FonixFlow" className="h-4 object-contain" />
          </div>

          {/* Main Content Area */}
          <div className="flex-1 flex overflow-hidden min-h-0">

            {/* Left Content Panel */}
            <div className="flex-1 p-[10px] flex flex-col min-h-0">
              {activeTab === 'record' && (
                <RecordView onTranscriptionComplete={(data) => {
                  setTranscript(data);
                  setActiveTab('transcript');
                }} />
              )}

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

              {activeTab === 'settings' && (
                <SettingsView />
              )}
            </div>

            {/* Right Sidebar Panel */}
            <div className="w-[200px] bg-[#252526] border-l border-[#1e1e1e] p-[10px] flex flex-col gap-3 shrink-0">
              <Sidebar
                activeTab={activeTab}
                setActiveTab={setActiveTab}
              />
            </div>
          </div>

          {/* Status Bar */}
          <div className="h-5 bg-[#007acc] text-white text-[10px] flex items-center px-3 shrink-0">
            Ready
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
