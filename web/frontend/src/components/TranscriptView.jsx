import React from 'react';
import { Download, Copy, ArrowLeft, Check } from 'lucide-react';

const TranscriptView = ({ data, onBack }) => {
  const [copied, setCopied] = React.useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(data.text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownload = (format) => {
    const element = document.createElement("a");
    let content = data.text;
    let type = "text/plain";

    if (format === 'json') {
      content = JSON.stringify(data, null, 2);
      type = "application/json";
    }

    const file = new Blob([content], { type: type });
    element.href = URL.createObjectURL(file);
    element.download = `transcript.${format}`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between mb-6 shrink-0">
        <div>
          <h1 className="text-2xl font-bold text-white">Transcription</h1>
        </div>

        <div className="flex gap-[10px]">
          <button
            onClick={handleCopy}
            className="flex items-center gap-[15px] px-[15px] py-[15px] rounded-full font-bold text-xl transition-all duration-200 bg-transparent text-gray-300 border-[3px] border-[#444] hover:bg-[#2a2a2a] hover:border-[#00dcd0] hover:text-white hover:scale-105"
          >
            {copied ? <Check size={22} strokeWidth={2.5} className="text-green-500" /> : <Copy size={22} strokeWidth={2.5} />}
            <span>{copied ? "Copied" : "Copy"}</span>
          </button>

          <button
            onClick={() => handleDownload('txt')}
            className="flex items-center gap-[15px] px-[15px] py-[15px] rounded-full font-bold text-xl transition-all duration-200 bg-[#00dcd0] text-white shadow-lg hover:bg-[#00c5ba] hover:scale-105 border-0"
          >
            <Download size={22} strokeWidth={2.5} />
            <span>Save TXT</span>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 min-h-0 flex gap-6 overflow-hidden">
        {/* Transcript Text */}
        <div className="flex-1 bg-[#1a1a1a] border border-[#333] rounded-lg overflow-hidden flex flex-col">
          <div className="flex-1 p-6 overflow-y-auto font-serif text-lg leading-relaxed text-gray-200 whitespace-pre-wrap">
            {data?.text}
          </div>
        </div>

        {/* Segments Sidebar */}
        <div className="w-72 shrink-0 flex flex-col gap-4 hidden lg:flex min-h-0">
          <div className="bg-[#1a1a1a] border border-[#333] rounded-lg flex-1 overflow-hidden flex flex-col">
            <div className="p-3 border-b border-[#333] bg-[#222]">
              <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider">Timeline</h3>
            </div>
            <div className="overflow-y-auto p-2 space-y-1 flex-1">
              {data?.segments?.map((seg, idx) => (
                <div key={idx} className="group p-2 rounded hover:bg-[#333] transition-colors cursor-pointer">
                  <div className="text-xs text-cyan-500 font-mono mb-1 font-bold">
                    {formatTime(seg.start)} - {formatTime(seg.end)}
                  </div>
                  <p className="text-xs text-gray-400 line-clamp-2 group-hover:text-gray-200 transition-colors">
                    {seg.text}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

function formatTime(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

export default TranscriptView;
