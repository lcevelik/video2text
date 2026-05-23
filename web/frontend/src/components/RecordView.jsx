import React, { useState, useRef, useEffect } from 'react';
import { Mic, Square, Play } from 'lucide-react';
import axios from 'axios';
import MultiLanguageDialog from './MultiLanguageDialog';

const RecordView = ({ onTranscriptionComplete }) => {
    const [isRecording, setIsRecording] = useState(false);
    const [status, setStatus] = useState('Ready to record');
    const [recordedBlob, setRecordedBlob] = useState(null);
    const [showDialog, setShowDialog] = useState(false);

    const mediaRecorderRef = useRef(null);
    const chunksRef = useRef([]);
    const micCanvasRef = useRef(null);
    const systemCanvasRef = useRef(null);
    const audioContextRef = useRef(null);
    const micAnalyserRef = useRef(null);
    const systemAnalyserRef = useRef(null);
    const micAnimationFrameRef = useRef(null);
    const systemAnimationFrameRef = useRef(null);

    useEffect(() => {
        // Start audio monitoring for microphone UV meter on mount
        const startMonitoring = async () => {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

                const audioContext = new (window.AudioContext || window.webkitAudioContext)();
                const analyser = audioContext.createAnalyser();
                const source = audioContext.createMediaStreamSource(stream);
                source.connect(analyser);
                analyser.fftSize = 256;

                audioContextRef.current = audioContext;
                micAnalyserRef.current = analyser;

                drawMicUVMeter();
            } catch (err) {
                console.error("Error accessing microphone for monitoring:", err);
            }
        };

        startMonitoring();

        return () => {
            if (micAnimationFrameRef.current) {
                cancelAnimationFrame(micAnimationFrameRef.current);
            }
            if (systemAnimationFrameRef.current) {
                cancelAnimationFrame(systemAnimationFrameRef.current);
            }
            if (audioContextRef.current) {
                audioContextRef.current.close();
            }
        };
    }, []); // Empty dependency array means this effect runs once on mount and cleans up on unmount

    // Helper function to draw UV meter
    const drawMicUVMeter = () => {
        const canvas = micCanvasRef.current;
        if (!canvas || !micAnalyserRef.current) return;

        const ctx = canvas.getContext('2d');
        const bufferLength = micAnalyserRef.current.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);

        const draw = () => {
            if (!micAnalyserRef.current) return;

            micAnimationFrameRef.current = requestAnimationFrame(draw);
            micAnalyserRef.current.getByteFrequencyData(dataArray);

            let sum = 0;
            for (let i = 0; i < bufferLength; i++) {
                sum += dataArray[i];
            }
            const average = sum / bufferLength;
            const volume = Math.min(1, average / 128);

            ctx.clearRect(0, 0, canvas.width, canvas.height);

            const width = canvas.width;
            const height = canvas.height;
            const barWidth = width * volume;

            ctx.fillStyle = '#333';
            ctx.fillRect(0, 0, width, height);

            const gradient = ctx.createLinearGradient(0, 0, width, 0);
            gradient.addColorStop(0, '#00dcd0');
            gradient.addColorStop(0.6, '#00dcd0');
            gradient.addColorStop(0.8, '#facc15');
            gradient.addColorStop(1, '#ef4444');

            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, barWidth, height);
        };

        draw();
    };

    const drawSystemUVMeter = () => {
        const canvas = systemCanvasRef.current;
        if (!canvas || !systemAnalyserRef.current) return;

        const ctx = canvas.getContext('2d');
        const bufferLength = systemAnalyserRef.current.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);

        const draw = () => {
            if (!systemAnalyserRef.current) return;

            systemAnimationFrameRef.current = requestAnimationFrame(draw);
            systemAnalyserRef.current.getByteFrequencyData(dataArray);

            let sum = 0;
            for (let i = 0; i < bufferLength; i++) {
                sum += dataArray[i];
            }
            const average = sum / bufferLength;
            const volume = Math.min(1, average / 128);

            ctx.clearRect(0, 0, canvas.width, canvas.height);

            const width = canvas.width;
            const height = canvas.height;
            const barWidth = width * volume;

            ctx.fillStyle = '#333';
            ctx.fillRect(0, 0, width, height);

            const gradient = ctx.createLinearGradient(0, 0, width, 0);
            gradient.addColorStop(0, '#9333ea'); // Purple for system audio
            gradient.addColorStop(0.6, '#9333ea');
            gradient.addColorStop(0.8, '#facc15');
            gradient.addColorStop(1, '#ef4444');

            ctx.fillStyle = gradient;
            ctx.fillRect(0, 0, barWidth, height);
        };

        draw();
    };

    const startRecording = async () => {
        try {
            setStatus('Requesting microphone access...');

            const micStream = await navigator.mediaDevices.getUserMedia({ audio: true });

            setStatus('Microphone ready. Now requesting screen/tab audio...');

            let displayStream;
            try {
                displayStream = await navigator.mediaDevices.getDisplayMedia({
                    video: true,
                    audio: {
                        echoCancellation: false,
                        noiseSuppression: false,
                        autoGainControl: false
                    }
                });

                if (displayStream.getAudioTracks().length === 0) {
                    alert('No audio track found in screen share. Make sure to check "Share audio" when sharing!');
                    setStatus('Warning: No system audio captured. Recording microphone only.');
                } else {
                    setStatus('System audio captured! Recording both microphone and system audio...');
                }
            } catch (err) {
                console.warn("Display audio not available:", err);
                alert('Screen sharing cancelled or not available. Recording microphone only.');
                setStatus('Recording microphone only (screen share cancelled).');
                displayStream = null;
            }

            const audioContext = new (window.AudioContext || window.webkitAudioContext)();
            const micAnalyser = audioContext.createAnalyser();
            const systemAnalyser = audioContext.createAnalyser();
            const destination = audioContext.createMediaStreamDestination();

            micAnalyser.fftSize = 256;
            systemAnalyser.fftSize = 256;

            const micSource = audioContext.createMediaStreamSource(micStream);
            micSource.connect(micAnalyser);
            micSource.connect(destination);

            if (displayStream) {
                const audioTracks = displayStream.getAudioTracks();
                if (audioTracks.length > 0) {
                    const displayAudioStream = new MediaStream(audioTracks);
                    const displaySource = audioContext.createMediaStreamSource(displayAudioStream);
                    displaySource.connect(systemAnalyser);
                    displaySource.connect(destination);
                }

                displayStream.getVideoTracks().forEach(track => track.stop());
            }

            audioContextRef.current = audioContext;
            micAnalyserRef.current = micAnalyser;
            systemAnalyserRef.current = systemAnalyser;

            drawMicUVMeter();
            if (displayStream && displayStream.getAudioTracks().length > 0) {
                drawSystemUVMeter();
            }

            mediaRecorderRef.current = new MediaRecorder(destination.stream);
            chunksRef.current = [];

            mediaRecorderRef.current.ondataavailable = (e) => {
                if (e.data.size > 0) {
                    chunksRef.current.push(e.data);
                }
            };

            mediaRecorderRef.current.onstop = async () => {
                const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
                setRecordedBlob(blob);
                setStatus('Recording saved. Ready to transcribe.');

                micStream.getTracks().forEach(track => track.stop());
                if (displayStream) {
                    displayStream.getTracks().forEach(track => track.stop());
                }

                if (audioContextRef.current) {
                    audioContextRef.current.close();
                    audioContextRef.current = null;
                }
                if (micAnimationFrameRef.current) {
                    cancelAnimationFrame(micAnimationFrameRef.current);
                }
                if (systemAnimationFrameRef.current) {
                    cancelAnimationFrame(systemAnimationFrameRef.current);
                }

                const micCanvas = micCanvasRef.current;
                const systemCanvas = systemCanvasRef.current;
                if (micCanvas) {
                    const ctx = micCanvas.getContext('2d');
                    ctx.clearRect(0, 0, micCanvas.width, micCanvas.height);
                }
                if (systemCanvas) {
                    const ctx = systemCanvas.getContext('2d');
                    ctx.clearRect(0, 0, systemCanvas.width, systemCanvas.height);
                }

                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                const newAudioContext = new (window.AudioContext || window.webkitAudioContext)();
                const newAnalyser = newAudioContext.createAnalyser();
                const source = newAudioContext.createMediaStreamSource(stream);
                source.connect(newAnalyser);
                newAnalyser.fftSize = 256;

                audioContextRef.current = newAudioContext;
                micAnalyserRef.current = newAnalyser;
                systemAnalyserRef.current = null;
                drawMicUVMeter();
            };

            mediaRecorderRef.current.start();
            setIsRecording(true);
        } catch (err) {
            console.error("Error accessing audio:", err);
            alert(`Error: ${err.message}`);
            setStatus('Error: Could not access audio devices');
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
        }
    };

    const handleTranscribeClick = () => {
        if (!recordedBlob) return;
        setShowDialog(true);
    };

    const handleDialogConfirm = async (options) => {
        setShowDialog(false);
        await handleUpload(recordedBlob, options);
    };

    const handleUpload = async (audioBlob, options) => {
        const formData = new FormData();
        formData.append('file', audioBlob, 'recording.webm');

        // Add language options to formData
        if (options.isMulti) {
            formData.append('language_mode', 'multi');
            formData.append('languages', JSON.stringify(options.languages));
        } else {
            formData.append('language_mode', 'single');
            formData.append('language', options.language);
        }

        try {
            setStatus('Transcribing...');
            // Assuming backend is on port 8000
            const response = await axios.post('http://localhost:8000/transcribe', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            setStatus('Done!');
            if (onTranscriptionComplete) {
                onTranscriptionComplete(response.data);
            }
        } catch (error) {
            console.error('Transcription error:', error);
            setStatus('Error during transcription');
        }
    };

    return (
        <div className="flex flex-col h-full">
            <p className="text-gray-400 text-xs mb-[5px]">
                Recording will capture microphone + system audio (you'll be asked to share a tab/screen with audio).
            </p>

            {/* Microphone UV Meter */}
            <div className="mb-[5px]">
                <label className="block text-[10px] font-bold text-gray-500 mb-1 uppercase">Microphone Level</label>
                <canvas
                    ref={micCanvasRef}
                    width={400}
                    height={20}
                    className="w-full h-5 rounded bg-[#333]"
                />
            </div>

            {/* System Audio UV Meter */}
            <div className="mb-[5px]">
                <label className="block text-[10px] font-bold text-gray-500 mb-1 uppercase">System Audio Level</label>
                <canvas
                    ref={systemCanvasRef}
                    width={400}
                    height={20}
                    className="w-full h-5 rounded bg-[#333]"
                />
            </div>

            <div className="flex-1 flex flex-col items-center justify-center gap-[10px] min-h-0">
                {!isRecording ? (
                    <>
                        <button
                            onClick={startRecording}
                            className="flex items-center gap-[15px] px-[15px] py-[15px] rounded-full font-bold text-2xl transition-all duration-200 bg-[#00dcd0] text-white shadow-lg hover:bg-[#00c5ba] hover:scale-105 border-0"
                        >
                            <Mic size={28} strokeWidth={2.5} />
                            <span>Start Recording</span>
                        </button>

                        {recordedBlob && (
                            <button
                                onClick={handleTranscribeClick}
                                className="flex items-center gap-[15px] px-[15px] py-[15px] rounded-full font-bold text-xl transition-all duration-200 bg-[#00dcd0] text-white shadow-lg hover:bg-[#00c5ba] hover:scale-105 border-0"
                            >
                                <Play size={22} fill="currentColor" strokeWidth={2.5} />
                                <span>Transcribe Recording</span>
                            </button>
                        )}
                    </>
                ) : (
                    <button
                        onClick={stopRecording}
                        className="flex items-center gap-[15px] px-[15px] py-[15px] rounded-full font-bold text-2xl transition-all duration-200 bg-red-500 text-white shadow-lg hover:bg-red-400 hover:scale-105 border-0 animate-pulse"
                    >
                        <Square size={28} strokeWidth={2.5} />
                        <span>Stop Recording</span>
                    </button>
                )}
            </div>

            <div className="mt-auto pt-2">
                <h3 className="text-xs font-medium text-gray-400 mb-1">{status}</h3>
                <div className="space-y-1 text-[10px] text-[#00dcd0]">
                    <p className="flex items-start gap-2">
                        <span className="bg-[#3e6b73] text-white rounded w-3 h-3 flex items-center justify-center text-[8px] shrink-0">i</span>
                        After stopping, the recording is saved but NOT automatically transcribed
                    </p>
                    <p className="flex items-start gap-2">
                        <span className="bg-[#3e6b73] text-white rounded w-3 h-3 flex items-center justify-center text-[8px] shrink-0">i</span>
                        Click "Transcribe Recording" to manually start transcription
                    </p>
                </div>
            </div>

            <MultiLanguageDialog
                isOpen={showDialog}
                onClose={() => setShowDialog(false)}
                onConfirm={handleDialogConfirm}
            />
        </div>
    );
};

export default RecordView;
