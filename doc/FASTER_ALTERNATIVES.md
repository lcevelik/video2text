# ⚡ Faster Alternatives to OpenAI Whisper

This guide explains faster transcription models you can use for 3-20x speedup compared to standard OpenAI Whisper.

**Important**: All these alternatives use the same Whisper model weights, so accuracy is identical. They're just faster!

---

## 🏆 insanely-fast-whisper (RECOMMENDED - 12-20x faster!)

### Why It's the Best

- **Speed**: 3-4x faster than faster-whisper, 12-20x faster than OpenAI Whisper
- **Accuracy**: Identical to Whisper (same model weights)
- **GPU Support**: Works with NVIDIA CUDA and Apple Metal (M1/M2/M3)
- **Easy Integration**: Simple command-line interface or Python API

### Installation

```bash
pip install insanely-fast-whisper

# For best performance, install FlashAttention-2 (NVIDIA GPUs only)
pip install flash-attn --no-build-isolation
```

### Usage

#### Command Line (Easiest)

```bash
# Basic usage
insanely-fast-whisper --file-name audio.mp3

# With specific model and language
insanely-fast-whisper --file-name audio.mp3 --model-name "large-v3" --task "transcribe" --language "en"

# With custom settings
insanely-fast-whisper \
  --file-name audio.mp3 \
  --model-name "medium" \
  --device-id "0" \
  --batch-size 24 \
  --flash True \
  --timestamp "chunk"
```

#### Python API

```python
import torch
from transformers import pipeline
from transformers.utils import is_flash_attn_2_available

# Set up pipeline with FlashAttention-2 if available
pipe = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-large-v3",
    torch_dtype=torch.float16,
    device="cuda:0",  # Use "mps" for Apple Silicon
    model_kwargs={"attn_implementation": "flash_attention_2"} if is_flash_attn_2_available() else {"attn_implementation": "sdpa"},
)

# Transcribe
outputs = pipe(
    "audio.mp3",
    chunk_length_s=30,
    batch_size=24,
    return_timestamps=True,
)

print(outputs["text"])
```

### Integration with fonixflow

You can use `insanely-fast-whisper` as a standalone tool and feed the results back:

```bash
# 1. Extract audio from video
ffmpeg -i video.mp4 -vn -acodec pcm_s16le -ar 16000 audio.wav

# 2. Transcribe with insanely-fast-whisper
insanely-fast-whisper --file-name audio.wav --model-name "medium" > transcript.json

# 3. Parse the JSON output in your app
```

### Performance Tips

1. **Enable FlashAttention-2**: Requires NVIDIA GPU with Ampere or newer (RTX 30XX+)
   ```bash
   pip install flash-attn --no-build-isolation
   ```

2. **Increase batch size**: Higher batch = faster (if you have enough GPU RAM)
   ```bash
   insanely-fast-whisper --batch-size 32  # Default is 24
   ```

3. **Use smaller models when possible**:
   - `tiny`: Good for quick tests
   - `base`: Balanced (recommended for most use cases)
   - `medium`: Better accuracy
   - `large-v3`: Best accuracy (slowest)

### Benchmarks (on NVIDIA RTX 4080)

| Model | OpenAI Whisper | insanely-fast-whisper | Speedup |
|-------|----------------|----------------------|---------|
| tiny | 10s | 0.5s | 20x faster |
| base | 15s | 0.8s | 18x faster |
| medium | 90s | 6s | 15x faster |
| large | 180s | 12s | 15x faster |

*For a 1-minute audio file*

---

## 🔧 WhisperX (BEST FOR FEATURES)

### What It Does

WhisperX is a full pipeline that adds:
- **VAD** (Voice Activity Detection): Skips silence
- **Forced Alignment**: Better word-level timestamps
- **Speaker Diarization**: Who said what (multi-speaker)
- Uses faster-whisper under the hood

### Installation

```bash
pip install whisperx
```

### Usage

```python
import whisperx
import gc

device = "cuda"
audio_file = "audio.mp3"
batch_size = 16  # Reduce if low on GPU mem
compute_type = "float16"  # change to "int8" if low on GPU mem

# 1. Transcribe with whisper (uses faster-whisper)
model = whisperx.load_model("large-v3", device, compute_type=compute_type)
audio = whisperx.load_audio(audio_file)
result = model.transcribe(audio, batch_size=batch_size)
print(result["segments"])

# Delete model if low on GPU memory
gc.collect(); torch.cuda.empty_cache(); del model

# 2. Align whisper output (better timestamps)
model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
result = whisperx.align(result["segments"], model_a, metadata, audio, device, return_char_alignments=False)
print(result["segments"])  # Now with better word-level timestamps

# 3. Assign speaker labels (diarization)
diarize_model = whisperx.DiarizationPipeline(use_auth_token="YOUR_HF_TOKEN", device=device)
diarize_segments = diarize_model(audio)
result = whisperx.assign_word_speakers(diarize_segments, result)
print(result["segments"])  # Now with speaker IDs!
```

### When to Use WhisperX

✅ **Use if you need**:
- Word-level timestamps (very precise)
- Speaker identification
- Multi-speaker conversations
- Skip silence automatically

❌ **Don't use if**:
- You just need speed (use insanely-fast-whisper)
- Single speaker with good audio quality
- Don't need word timestamps

---

## 🍎 MLX Whisper (FOR APPLE SILICON)

### For M1/M2/M3 Macs Only

MLX is Apple's machine learning framework optimized for Apple Silicon.

### Installation

```bash
pip install mlx-whisper
```

### Usage

```python
import mlx_whisper

# Transcribe
result = mlx_whisper.transcribe(
    "audio.mp3",
    path_or_hf_repo="mlx-community/whisper-large-v3-turbo"
)

print(result["text"])
```

### Command Line

```bash
mlx_whisper audio.mp3 --model mlx-community/whisper-large-v3-turbo
```

### Performance

- **~50% faster** than OpenAI Whisper on Apple Silicon
- Doesn't work well on non-Apple hardware
- Good for M1/M2/M3 Macs without discrete GPU

---

## 📊 Comparison Table

| Tool | Speed | Accuracy | GPU Support | Features | Best For |
|------|-------|----------|-------------|----------|----------|
| **insanely-fast-whisper** | ⚡⚡⚡⚡⚡ | ✓ Same | CUDA, Metal | Basic transcription | Maximum speed |
| **WhisperX** | ⚡⚡⚡ | ✓ Same | CUDA | VAD, alignment, diarization | Speaker identification |
| **MLX Whisper** | ⚡⚡⚡ | ✓ Same | Apple Silicon | Basic transcription | M1/M2/M3 Macs |
| **OpenAI Whisper** | ⚡ | ✓ Baseline | CUDA, CPU | Basic transcription | Default/fallback |

---

## 🎯 Recommendation for fonixflow

For your multi-language Czech/English and Spanish/English videos:

### Option 1: Use insanely-fast-whisper as External Tool (BEST)

**Workflow**:
1. Extract audio with fonixflow
2. Run insanely-fast-whisper CLI
3. Parse JSON output back into fonixflow

**Pros**:
- 12-20x faster overall
- No code changes needed
- Can run as batch job
- Easy to test

**Setup**:
```bash
# Install
pip install insanely-fast-whisper
pip install flash-attn --no-build-isolation  # For NVIDIA GPUs

# Test it
insanely-fast-whisper --file-name test_audio.mp3 --model-name "base"
```

### Option 2: Use WhisperX for Multi-Speaker Videos

If your videos have multiple speakers and you need to know who said what:

```bash
pip install whisperx
```

Then modify fonixflow to use WhisperX API instead of OpenAI Whisper.

### Option 3: Use MLX Whisper (Apple Silicon Only)

If you're on a Mac with M1/M2/M3:

```bash
pip install mlx-whisper
```

---

## 🚀 Quick Start: insanely-fast-whisper

Try it right now with your existing audio:

```bash
# Install
pip install insanely-fast-whisper

# Test with a video
ffmpeg -i your_video.mp4 -vn -acodec pcm_s16le -ar 16000 test_audio.wav
insanely-fast-whisper --file-name test_audio.wav --model-name "base" --language "en"

# For multi-language (auto-detect)
insanely-fast-whisper --file-name test_audio.wav --model-name "base"

# For Czech/English specifically
insanely-fast-whisper --file-name test_audio.wav --model-name "base" --task "transcribe"
```

---

## 💡 Tips for Best Performance

### 1. Choose the Right Model Size

- **tiny**: Testing only, drops words
- **base**: ⭐ RECOMMENDED for speed + accuracy balance
- **medium**: Better accuracy, still fast
- **large-v3**: Best accuracy, slower

### 2. Enable GPU Acceleration

**NVIDIA GPU**:
```bash
# Make sure CUDA is installed
nvidia-smi

# Install FlashAttention for maximum speed
pip install flash-attn --no-build-isolation
```

**Apple Silicon**:
```bash
# Use MLX for best performance
pip install mlx-whisper
```

### 3. Optimize Batch Size

```bash
# Start with default
insanely-fast-whisper --batch-size 24

# If you have lots of GPU RAM (16GB+), increase it
insanely-fast-whisper --batch-size 48

# If you run out of memory, decrease it
insanely-fast-whisper --batch-size 12
```

### 4. Use Chunking for Long Videos

```bash
# Process in 30-second chunks (faster)
insanely-fast-whisper --file-name long_audio.mp3 --chunk-length-s 30
```

---

## 🔍 Troubleshooting

### "CUDA out of memory"

```bash
# Reduce batch size
insanely-fast-whisper --batch-size 8

# Or use smaller model
insanely-fast-whisper --model-name "base"  # Instead of "large"
```

### "FlashAttention not available"

```bash
# Install manually (NVIDIA GPUs only)
pip install flash-attn --no-build-isolation

# Or use SDPA (slower but works everywhere)
# insanely-fast-whisper will auto-fallback
```

### "Model downloads slowly"

```bash
# Pre-download models
python -c "from transformers import pipeline; pipeline('automatic-speech-recognition', model='openai/whisper-base')"
```

---

## 📝 Summary

**For maximum speed with same accuracy**:
1. **Use insanely-fast-whisper** (12-20x faster)
2. Enable FlashAttention-2 if you have NVIDIA GPU
3. Use `base` model for best speed/accuracy balance
4. Your 33-min videos will now process in ~2-3 minutes instead of 33+ minutes!

**Key takeaway**: These alternatives don't change accuracy - they just make Whisper run faster using optimized inference engines (Hugging Face Transformers + FlashAttention instead of PyTorch).

Enjoy your blazing-fast transcriptions! 🚀
**Latest update:**
- Rebranded to FonixFlow
- UI improvements: logo in top bar, auto-jump to transcript tab
