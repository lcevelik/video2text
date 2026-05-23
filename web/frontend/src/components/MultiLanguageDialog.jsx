import React, { useState } from 'react';
import { X, Check } from 'lucide-react';

const MultiLanguageDialog = ({ isOpen, onClose, onConfirm }) => {
    const [mode, setMode] = useState('initial'); // 'initial', 'single', 'multi'
    const [singleType, setSingleType] = useState('english'); // 'english', 'other'
    const [selectedLanguages, setSelectedLanguages] = useState(['en', 'es']);

    if (!isOpen) return null;

    const availableLanguages = [
        { code: 'en', name: 'English' }, { code: 'cs', name: 'Czech' },
        { code: 'de', name: 'German' }, { code: 'fr', name: 'French' },
        { code: 'es', name: 'Spanish' }, { code: 'it', name: 'Italian' },
        { code: 'pl', name: 'Polish' }, { code: 'ru', name: 'Russian' },
        { code: 'zh', name: 'Chinese' }, { code: 'ja', name: 'Japanese' },
        { code: 'ko', name: 'Korean' }, { code: 'ar', name: 'Arabic' }
    ];

    const handleConfirm = () => {
        if (mode === 'single') {
            onConfirm({
                isMulti: false,
                language: singleType === 'english' ? 'en' : 'auto'
            });
        } else if (mode === 'multi') {
            if (selectedLanguages.length === 0) {
                alert("Select at least one language.");
                return;
            }
            onConfirm({
                isMulti: true,
                languages: selectedLanguages
            });
        }
    };

    const toggleLanguage = (code) => {
        if (selectedLanguages.includes(code)) {
            setSelectedLanguages(selectedLanguages.filter(l => l !== code));
        } else {
            setSelectedLanguages([...selectedLanguages, code]);
        }
    };

    return (
        <div className="absolute inset-0 bg-black/70 flex items-center justify-center z-50 backdrop-blur-sm p-[10px]">
            <div className="bg-[#2d2d30] border-2 border-[#555] rounded-2xl shadow-2xl w-[600px] max-h-full overflow-hidden flex flex-col">
                {/* Header */}
                <div className="bg-[#3c3c3c] px-[10px] py-[10px] border-b-2 border-[#555] flex justify-between items-center">
                    <h3 className="text-2xl font-bold text-white">Language Mode</h3>
                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-white hover:bg-[#555] rounded-full p-2 transition-all"
                    >
                        <X size={24} strokeWidth={2.5} />
                    </button>
                </div>

                {/* Content */}
                <div className="p-[10px] flex-1 overflow-y-auto">
                    <h2 className="text-xl font-bold text-white mb-[10px] text-center">Is your file multi-language?</h2>

                    {mode === 'initial' && (
                        <div className="flex gap-[10px] justify-center">
                            <button
                                onClick={() => setMode('multi')}
                                className="flex items-center gap-[15px] px-[20px] py-[15px] rounded-full font-bold text-xl transition-all duration-200 bg-[#00dcd0] text-white shadow-lg hover:bg-[#00c5ba] hover:scale-105 border-0"
                            >
                                <span>Multi-Language</span>
                            </button>
                            <button
                                onClick={() => setMode('single')}
                                className="flex items-center gap-[15px] px-[20px] py-[15px] rounded-full font-bold text-xl transition-all duration-200 bg-[#00dcd0] text-white shadow-lg hover:bg-[#00c5ba] hover:scale-105 border-0"
                            >
                                <span>Single-Language</span>
                            </button>
                        </div>
                    )}

                    {mode === 'single' && (
                        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-300">
                            <p className="font-bold text-white text-lg">Select language type:</p>

                            <label className="flex items-center gap-4 p-4 rounded-2xl border-2 border-[#444] bg-[#252526] cursor-pointer hover:bg-[#2a2a2a] hover:border-[#00dcd0] transition-all">
                                <input
                                    type="radio"
                                    name="singleType"
                                    checked={singleType === 'english'}
                                    onChange={() => setSingleType('english')}
                                    className="w-5 h-5 accent-[#00dcd0]"
                                />
                                <span className="text-gray-200 text-lg">English (uses optimized .en model)</span>
                            </label>

                            <label className="flex items-center gap-4 p-4 rounded-2xl border-2 border-[#444] bg-[#252526] cursor-pointer hover:bg-[#2a2a2a] hover:border-[#00dcd0] transition-all">
                                <input
                                    type="radio"
                                    name="singleType"
                                    checked={singleType === 'other'}
                                    onChange={() => setSingleType('other')}
                                    className="w-5 h-5 accent-[#00dcd0]"
                                />
                                <span className="text-gray-200 text-lg">Other language (uses multilingual model)</span>
                            </label>

                            <div className="pt-6 flex justify-end gap-[10px]">
                                <button
                                    onClick={() => setMode('initial')}
                                    className="flex items-center gap-[15px] px-[15px] py-[12px] rounded-full font-bold text-lg transition-all duration-200 bg-transparent text-gray-300 border-[3px] border-[#444] hover:bg-[#2a2a2a] hover:border-[#00dcd0] hover:text-white"
                                >
                                    <span>Back</span>
                                </button>
                                <button
                                    onClick={handleConfirm}
                                    className="flex items-center gap-[15px] px-[15px] py-[12px] rounded-full font-bold text-lg transition-all duration-200 bg-[#00dcd0] text-white shadow-lg hover:bg-[#00c5ba] hover:scale-105 border-0"
                                >
                                    <Check size={20} strokeWidth={2.5} />
                                    <span>Confirm Selection</span>
                                </button>
                            </div>
                        </div>
                    )}

                    {mode === 'multi' && (
                        <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-300">
                            <p className="font-bold text-white text-lg">Select languages present:</p>

                            <div className="grid grid-cols-3 gap-[10px]">
                                {availableLanguages.map(lang => (
                                    <label
                                        key={lang.code}
                                        className="flex items-center gap-[10px] p-[10px] rounded-xl border-2 border-[#444] bg-[#252526] cursor-pointer hover:bg-[#2a2a2a] hover:border-[#00dcd0] transition-all text-base text-gray-300 hover:text-white"
                                    >
                                        <input
                                            type="checkbox"
                                            checked={selectedLanguages.includes(lang.code)}
                                            onChange={() => toggleLanguage(lang.code)}
                                            className="w-5 h-5 accent-[#00dcd0] rounded"
                                        />
                                        {lang.name}
                                    </label>
                                ))}
                            </div>

                            <div className="pt-6 flex justify-end gap-[10px]">
                                <button
                                    onClick={() => setMode('initial')}
                                    className="flex items-center gap-[15px] px-[15px] py-[12px] rounded-full font-bold text-lg transition-all duration-200 bg-transparent text-gray-300 border-[3px] border-[#444] hover:bg-[#2a2a2a] hover:border-[#00dcd0] hover:text-white"
                                >
                                    <span>Back</span>
                                </button>
                                <button
                                    onClick={handleConfirm}
                                    className="flex items-center gap-[15px] px-[15px] py-[12px] rounded-full font-bold text-lg transition-all duration-200 bg-[#00dcd0] text-white shadow-lg hover:bg-[#00c5ba] hover:scale-105 border-0"
                                >
                                    <Check size={20} strokeWidth={2.5} />
                                    <span>Confirm Languages</span>
                                </button>
                            </div>
                        </div>
                    )}

                    <p className="text-center text-gray-500 text-sm mt-[10px]">
                        {mode === 'initial' ? "Cancel to decide later." : "Select options to proceed."}
                    </p>
                </div>
            </div>
        </div>
    );
};

export default MultiLanguageDialog;
