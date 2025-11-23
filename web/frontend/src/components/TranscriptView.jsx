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

    const file = new Blob([content], {type: type});
    element.href = URL.createObjectURL(file);
    element.download = `transcript.${format}`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return (
    <div className="h-full flex flex-col max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <button 
            onClick={onBack}
            className="p-2 hover:bg-gray-800 rounded-full transition-colors"
          >
            <ArrowLeft className="w-6 h-6" />
          </button>
          <div>
            <h1 className="text-2xl font-bold">Transcription Results</h1>
            <p className="text-text-secondary text-sm">
              Language: <span className="uppercase font-semibold text-blue-400">{data?.language}</span>
            </p>
          </div>
        </div>

        <div className="flex gap-2">
          <button 
            onClick={handleCopy}
            className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
          >
            {copied ? <Check className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
            {copied ? "Copied" : "Copy Text"}
          </button>
          
          <div className="h-8 w-px bg-gray-700 mx-2"></div>

          <button 
            onClick={() => handleDownload('txt')}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors text-white"
          >
            <Download className="w-4 h-4" />
            Download TXT
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-hidden bg-gray-900 rounded-xl border border-gray-800 shadow-xl flex">
        {/* Main Text Area */}
        <div className="flex-1 p-8 overflow-y-auto font-serif text-lg leading-relaxed text-gray-200 whitespace-pre-wrap">
          {data?.text}
        </div>

        {/* Segments Sidebar (Optional - visual enhancement) */}
        <div className="w-80 border-l border-gray-800 bg-sidebar overflow-y-auto p-4 hidden lg:block">
          <h3 className="text-sm font-bold text-text-secondary uppercase tracking-wider mb-4">Timeline</h3>
          <div className="space-y-4">
            {data?.segments?.map((seg, idx) => (
              <div key={idx} className="group p-3 rounded-lg hover:bg-gray-800 transition-colors cursor-pointer">
                <div className="text-xs text-blue-400 font-mono mb-1">
                  {formatTime(seg.start)} - {formatTime(seg.end)}
                </div>
                <p className="text-sm text-gray-400 line-clamp-3 group-hover:text-gray-200">
                  {seg.text}
                </p>
              </div>
            ))}
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
