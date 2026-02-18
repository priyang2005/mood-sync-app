import numpy as np
import librosa
import sounddevice as sd
from scipy.signal import find_peaks


class MoodAudioAnalyzer:

    def __init__(self, duration=5, sample_rate=22050):
        self.duration = duration
        self.sample_rate = sample_rate

    # --------------------------------------------------
    # 1️⃣ Record Audio
    # --------------------------------------------------
    def record_audio(self):
        print("🎤 Recording audio...")
        audio = sd.rec(
            int(self.duration * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32"
        )
        sd.wait()
        print("✅ Recording complete.")
        return np.squeeze(audio)

    # --------------------------------------------------
    # 2️⃣ Extract Audio Features (Improved Stability)
    # --------------------------------------------------
    def extract_features(self, audio):

        # Normalize audio to avoid mic-level issues
        audio = audio / (np.max(np.abs(audio)) + 1e-6)

        # RMS Energy (Volume level)
        rms = float(np.mean(librosa.feature.rms(y=audio)))

        # Pitch Detection
        pitches, magnitudes = librosa.piptrack(y=audio, sr=self.sample_rate)
        pitch_values = pitches[pitches > 0]
        pitch = float(np.mean(pitch_values)) if len(pitch_values) > 0 else 0.0

        # Spectral Centroid (Sharpness)
        spectral_centroid = float(
            np.mean(librosa.feature.spectral_centroid(y=audio, sr=self.sample_rate))
        )

        # Peak detection (burst/laughter detection)
        energy = np.abs(audio)
        peaks, _ = find_peaks(energy, height=0.4, distance=200)
        peak_count = int(len(peaks))

        return {
            "rms": rms,
            "pitch": pitch,
            "spectral_centroid": spectral_centroid,
            "peak_count": peak_count
        }

    # --------------------------------------------------
    # 3️⃣ Classify Mood from Audio
    # --------------------------------------------------
    def classify_mood(self, features):

        rms = features["rms"]
        pitch = features["pitch"]
        peak_count = features["peak_count"]

        # Very quiet environment
        if rms < 0.02:
            return "CALM"

        # Loud + high pitch → argument / scream
        if rms > 0.07 and pitch > 250:
            return "TENSE"

        # Many bursts → laughter
        if peak_count > 30:
            return "JOYFUL"

        return "CALM"

    # --------------------------------------------------
    # 4️⃣ Full Audio Analysis Pipeline
    # --------------------------------------------------
    def analyze(self):

        audio = self.record_audio()
        features = self.extract_features(audio)
        mood = self.classify_mood(features)

        result = {
            "audio_mood": mood,
            "audio_features": features
        }

        print("\n🎧 Audio Analysis Result:")
        print(result)

        return result


# --------------------------------------------------
# Standalone Testing
# --------------------------------------------------
if __name__ == "__main__":
    analyzer = MoodAudioAnalyzer(duration=5)
    analyzer.analyze()
