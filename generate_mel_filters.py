import numpy as np
import librosa

np.savez_compressed(
    "_internal/whisper/assets/mel_filters.npz",
    mel_80=librosa.filters.mel(sr=16000, n_fft=400, n_mels=80),
    mel_128=librosa.filters.mel(sr=16000, n_fft=400, n_mels=128),
)
print("mel_filters.npz generated successfully.")
