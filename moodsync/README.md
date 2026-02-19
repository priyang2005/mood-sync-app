# MoodSync Light 💡

AI-powered mood-reactive lighting webapp.  
Records 5 seconds of audio + video → classifies the room's energy → changes your lights.

---

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

> **macOS:** If `sounddevice` errors, install PortAudio first:
> ```bash
> brew install portaudio
> ```

### 2. Run the app

```bash
python app.py
```

Open your browser at **http://localhost:5000**

---

## How it works

| Step | Module | What happens |
|------|--------|--------------|
| 1 | `audio_analyzer.py` | Records 5s mic audio, extracts RMS, pitch, spectral centroid, peak count |
| 2 | `vision_analyzer.py` | Captures 5s webcam frames, detects faces + smiles via Haar cascades |
| 3 | `light_controller.py` | Fuses audio + vision moods into a single light mode |
| 4 | `app.py` | Flask server coordinates everything; frontend polls `/status` |
| 5 | `templates/index.html` | Animated 4-page webapp with live light simulator |

---

## Mood → Light Mapping

| Detected Mood | Light Mode | Color |
|---------------|------------|-------|
| Screaming / very loud | `red` | 🔴 Red flash |
| Arguing / tense | `soothing_blue` | 🔵 Calm blue pulse |
| Laughing / joyful | `disco` | 🟢 RGB disco cycle |
| Calm / neutral | `neutral` | ⚪ Soft warm white |

---

## File Structure

```
moodsync/
├── app.py                  ← Flask server (main entry point)
├── audio_analyzer.py       ← Mic recording + mood classification
├── vision_analyzer.py      ← Webcam face/smile detection
├── light_controller.py     ← Mood fusion + light mode decision
├── requirements.txt
├── templates/
│   └── index.html          ← Full frontend webapp
└── README.md
```

---

## Notes

- The frontend works in **demo mode** even without the Python backend (useful for UI testing)
- All analysis runs in background threads — the frontend stays responsive via `/status` polling
- For real Philips Hue integration, add your bridge IP + token to `light_controller.py` and call `send_to_simulator()` with `http://<bridge-ip>/api/<token>/lights/<id>/state`
