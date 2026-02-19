"""
MoodSync Light — Audio Analyzer
Captures 5 seconds of audio and classifies the mood.
"""

import numpy as np
import librosa
import sounddevice as sd
from scipy.signal import find_peaks


class MoodAudioAnalyzer:

    def __init__(self, duration=5, sample_rate=22050):
        self.duration = duration
        self.sample_rate = sample_rate

    # ── 1. Record ───────────────────────────────────────
    def record_audio(self):
        print("🎤 Recording audio...")
        audio = sd.rec(
            int(self.duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
        )
        sd.wait()
        print("✅ Recording complete.")
        return np.squeeze(audio)

    # ── 2. Feature Extraction ───────────────────────────
    def extract_features(self, audio):
        # Normalize to remove mic-level variance
        audio = audio / (np.max(np.abs(audio)) + 1e-6)

        # RMS energy (volume)
        rms = float(np.mean(librosa.feature.rms(y=audio)))

        # Pitch
        pitches, magnitudes = librosa.piptrack(y=audio, sr=self.sample_rate)
        pitch_values = pitches[pitches > 0]
        pitch = float(np.mean(pitch_values)) if len(pitch_values) > 0 else 0.0

        # Spectral centroid (sharpness / brightness of sound)
        spectral_centroid = float(
            np.mean(librosa.feature.spectral_centroid(y=audio, sr=self.sample_rate))
        )

        # Zero-crossing rate (speech vs. noise vs. laughter)
        zcr = float(np.mean(librosa.feature.zero_crossing_rate(y=audio)))

        # Energy burst / peak detection → laughter fingerprint
        energy = np.abs(audio)
        peaks, _ = find_peaks(energy, height=0.35, distance=150)
        peak_count = int(len(peaks))

        # Volume in dB (for the controller threshold)
        rms_db = float(20 * np.log10(rms + 1e-9))

        return {
            "rms": rms,
            "rms_db": rms_db,
            "pitch": pitch,
            "spectral_centroid": spectral_centroid,
            "zcr": zcr,
            "peak_count": peak_count,
        }

    # ── 3. Classify Mood ────────────────────────────────
    def classify_mood(self, features):
        rms        = features["rms"]
        pitch      = features["pitch"]
        peak_count = features["peak_count"]
        zcr        = features["zcr"]

        # Silence / very quiet
        if rms < 0.02:
            return "CALM"

        # Loud + high-pitch → argument / scream → red alert
        if rms > 0.07 and pitch > 250:
            return "TENSE"

        # Frequent energy bursts + high ZCR → laughter
        if peak_count > 30 or (peak_count > 15 and zcr > 0.1):
            return "JOYFUL"

        # Moderate noise, low pitch → neutral chatter
        return "CALM"

    # ── 4. Full Pipeline ────────────────────────────────
    def analyze(self):
        audio    = self.record_audio()
        features = self.extract_features(audio)
        mood     = self.classify_mood(features)

        result = {
            "audio_mood":     mood,
            "audio_features": features,
        }
        print("\n🎧 Audio Analysis Result:")
        print(result)
        return result


# ── Standalone test ─────────────────────────────────────
if __name__ == "__main__":
    MoodAudioAnalyzer(duration=5).analyze()
