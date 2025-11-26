import React from 'react';
import { Download, Copy, ArrowLeft, Check } from 'lucide-react';
import ModernButton from './ui/ModernButton';
import Card from './ui/Card';

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
    <div className="h-full flex flex-col max-w-6xl mx-auto p-4 gap-6">
      {/* Header */}
      <div className="flex items-center justify-between shrink-0">
        <div className="flex items-center gap-4">
          <button
            onClick={onBack}
            className="p-2 hover:bg-bg-tertiary rounded-full transition-colors text-text-secondary hover:text-text-primary"
          >
            <ArrowLeft className="w-6 h-6" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-text-primary">Transcription Results</h1>
            <p className="text-text-secondary text-sm flex items-center gap-2">
              Language: <span className="uppercase font-bold text-accent">{data?.language}</span>
            </p>
          </div>
        </div>

        <div className="flex gap-3">
          <ModernButton onClick={handleCopy}>
            <div className="flex items-center gap-2">
              {copied ? <Check className="w-4 h-4 text-success" /> : <Copy className="w-4 h-4" />}
              {copied ? "Copied" : "Copy Text"}
            </div>
          </ModernButton>

          <ModernButton primary onClick={() => handleDownload('txt')}>
            <div className="flex items-center gap-2">
              <Download className="w-4 h-4" />
              Download TXT
            </div>
          </ModernButton>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 min-h-0 flex gap-6">
        {/* Transcript Text */}
        <Card className="flex-1 flex flex-col min-h-0 p-0 overflow-hidden bg-bg-secondary border-border">
          <div className="flex-1 p-8 overflow-y-auto font-serif text-lg leading-relaxed text-text-primary whitespace-pre-wrap">
            {data?.text}
          </div>
        </Card>

        {/* Segments Sidebar */}
        <div className="w-80 shrink-0 flex flex-col gap-4 hidden lg:flex min-h-0">
          <div className="bg-bg-secondary border border-border rounded-xl flex-1 overflow-hidden flex flex-col">
            <div className="p-4 border-b border-border bg-bg-tertiary/50">
              <h3 className="text-sm font-bold text-text-secondary uppercase tracking-wider">Timeline</h3>
            </div>
            <div className="overflow-y-auto p-2 space-y-1 flex-1">
              {data?.segments?.map((seg, idx) => (
                <div key={idx} className="group p-3 rounded-lg hover:bg-bg-tertiary transition-colors cursor-pointer border border-transparent hover:border-border">
                  <div className="text-xs text-accent font-mono mb-1 font-bold">
                    {formatTime(seg.start)} - {formatTime(seg.end)}
                  </div>
                  <p className="text-sm text-text-secondary line-clamp-3 group-hover:text-text-primary transition-colors">
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
