import React, { useState } from 'react';
import { FileText, Folder, FolderOpen, Sliders, Search, Award, FileText as FileIcon, CheckCircle, Square } from 'lucide-react';

const SettingsView = () => {
    const [enhanceAudio, setEnhanceAudio] = useState(false);
    const [deepScan, setDeepScan] = useState(false);

    const QuickActionButton = ({ icon: Icon, label, onClick }) => (
        <button
            onClick={onClick}
            className="flex items-center gap-2 px-4 py-3 rounded-xl border-2 border-[#333] text-gray-200 font-bold text-sm hover:bg-[#2a2a2a] hover:border-[#00dcd0] hover:text-white transition-all"
        >
            <Icon size={18} />
            {label}
        </button>
    );

    const ToggleButton = ({ icon: Icon, label, isActive, onClick, indent = false }) => (
        <button
            onClick={onClick}
            className={`flex items-center gap-3 w-[180px] h-[50px] px-3 rounded-xl border-2 transition-all font-bold text-sm text-left
        ${isActive
                    ? 'bg-[#00dcd0] border-[#00dcd0] text-white'
                    : 'bg-transparent border-[#333] text-gray-200 hover:bg-[#2a2a2a] hover:border-[#00dcd0] hover:text-white'
                }
      `}
        >
            {isActive ? <CheckCircle size={18} /> : <Square size={18} />}
            <span className={indent ? "pl-2" : ""}>{label}</span>
        </button>
    );

    return (
        <div className="h-full overflow-y-auto p-8">
            <div className="space-y-8">

                {/* Quick Actions */}
                <section>
                    <h3 className="text-lg font-bold text-white mb-4">Quick Actions</h3>
                    <div className="flex gap-[20px]">
                        <button
                            onClick={() => window.location.reload()}
                            className="flex items-center gap-[15px] px-[15px] py-[15px] rounded-full font-bold text-xl transition-all duration-200 bg-transparent text-gray-300 border-[3px] border-[#444] hover:bg-[#2a2a2a] hover:border-[#00dcd0] hover:text-white"
                        >
                            <FileText size={22} strokeWidth={2.5} />
                            <span>New Transcription</span>
                        </button>

                        <button
                            onClick={() => alert("Folder selection not available in web demo")}
                            className="flex items-center gap-[15px] px-[15px] py-[15px] rounded-full font-bold text-xl transition-all duration-200 bg-transparent text-gray-300 border-[3px] border-[#444] hover:bg-[#2a2a2a] hover:border-[#00dcd0] hover:text-white"
                        >
                            <Folder size={22} strokeWidth={2.5} />
                            <span>Change Folder</span>
                        </button>

                        <button
                            onClick={() => alert("Cannot open local folder from web")}
                            className="flex items-center gap-[15px] px-[15px] py-[15px] rounded-full font-bold text-xl transition-all duration-200 bg-transparent text-gray-300 border-[3px] border-[#444] hover:bg-[#2a2a2a] hover:border-[#00dcd0] hover:text-white"
                        >
                            <FolderOpen size={22} strokeWidth={2.5} />
                            <span>Open Folder</span>
                        </button>
                    </div>
                </section>

                {/* Recordings Directory Card */}
                <section>
                    <div className="bg-[#1e1e1e] border border-[#333] rounded-xl p-5 shadow-lg">
                        <h4 className="text-white font-bold text-base mb-4">Recordings Settings</h4>
                        <p className="text-gray-400 text-xs mb-2">Recordings save to:</p>
                        <div className="bg-[#252525] border border-[#333] rounded-md p-3 text-[#00dcd0] text-sm font-mono break-all">
                            /Downloads/FonixFlow/Recordings
                        </div>
                    </div>
                </section>

                {/* Settings */}
                <section>
                    <h3 className="text-lg font-bold text-white mb-4">Settings</h3>

                    <div className="space-y-6">
                        {/* Enhance Audio, Deep Scan, and Activate in one row */}
                        <div className="flex gap-[20px]">
                            <button
                                onClick={() => setEnhanceAudio(!enhanceAudio)}
                                className={`flex items-center gap-[15px] px-[15px] py-[15px] rounded-full font-bold text-xl transition-all duration-200 ${enhanceAudio
                                    ? 'bg-[#00dcd0] text-white shadow-lg scale-105 border-0'
                                    : 'bg-transparent text-gray-300 border-[3px] border-[#444] hover:bg-[#2a2a2a] hover:border-[#00dcd0] hover:text-white'
                                    }`}
                            >
                                <Sliders size={22} strokeWidth={2.5} />
                                <span>Enhance Audio</span>
                            </button>

                            <button
                                onClick={() => setDeepScan(!deepScan)}
                                className={`flex items-center gap-[15px] px-[15px] py-[15px] rounded-full font-bold text-xl transition-all duration-200 ${deepScan
                                    ? 'bg-[#00dcd0] text-white shadow-lg scale-105 border-0'
                                    : 'bg-transparent text-gray-300 border-[3px] border-[#444] hover:bg-[#2a2a2a] hover:border-[#00dcd0] hover:text-white'
                                    }`}
                            >
                                <Search size={22} strokeWidth={2.5} />
                                <span>Deep Scan</span>
                            </button>

                            <button
                                onClick={() => alert("Activation dialog placeholder")}
                                className="flex items-center gap-[15px] px-[15px] py-[15px] rounded-full font-bold text-xl transition-all duration-200 bg-transparent text-gray-300 border-[3px] border-[#444] hover:bg-[#2a2a2a] hover:border-[#00dcd0] hover:text-white"
                            >
                                <Award size={22} strokeWidth={2.5} />
                                <span>Activate</span>
                            </button>
                        </div>
                    </div>
                </section>

            </div>
        </div>
    );
};

export default SettingsView;
