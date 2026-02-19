"""
MoodSync Light — Flask App
Single-file server: serves the frontend + runs the full analysis pipeline.

Run:
    pip install flask flask-cors opencv-python librosa sounddevice scipy numpy
    python app.py
"""

import threading
import random
import time
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

from audio_analyzer  import MoodAudioAnalyzer
from vision_analyzer import MoodVisionAnalyzer
from light_controller import SmartLightController

app = Flask(__name__)
CORS(app)

# Shared state — written by analysis thread, read by SSE / poll endpoint
analysis_state = {
    "status":       "idle",   # idle | recording | analyzing | done | error
    "step":         0,        # 0-4
    "light_mode":   None,
    "audio_mood":   None,
    "vision_mood":  None,
    "audio_features": {},
    "faces":        0,
    "smiles":       0,
    "error":        None,
}
state_lock = threading.Lock()
current_color = {"r": 255, "g": 255, "b": 255}


# ── Helpers ─────────────────────────────────────────────
def set_state(**kwargs):
    with state_lock:
        analysis_state.update(kwargs)


def get_state():
    with state_lock:
        return dict(analysis_state)


def set_color(r, g, b):
    global current_color
    current_color = {"r": r, "g": g, "b": b}
    print(f"   💡 Color → rgb({r},{g},{b})")


def apply_light_mode(mode):
    """Translate mode string to RGB and persist."""
    if mode == "red":
        set_color(255, 30, 30)
    elif mode == "soothing_blue":
        set_color(30, 120, 255)
    elif mode == "disco":
        # Cycle through 5 random colours quickly (blocking — in analysis thread)
        for _ in range(5):
            set_color(random.randint(80, 255), random.randint(80, 255), random.randint(80, 255))
            time.sleep(0.3)
        # Settle on vivid green-lime for "joyful" steady state
        set_color(140, 255, 60)
    elif mode == "neutral":
        set_color(210, 210, 210)
    else:
        set_color(255, 255, 255)


# ── Analysis worker (runs in background thread) ─────────
def run_analysis():
    try:
        set_state(status="recording", step=1,
                  light_mode=None, audio_mood=None, vision_mood=None,
                  audio_features={}, faces=0, smiles=0, error=None)

        # --- Step 1+2: record audio + video in parallel ---
        audio_result  = {"audio_mood": "CALM", "audio_features": {"rms_db": 0}}
        vision_result = {"vision_mood": "CALM", "faces_detected": 0, "smiles_detected": 0}

        audio_done  = threading.Event()
        vision_done = threading.Event()

        def do_audio():
            try:
                r = MoodAudioAnalyzer(duration=5).analyze()
                audio_result.update(r)
            except Exception as e:
                print(f"⚠️  Audio error: {e}")
            finally:
                audio_done.set()

        def do_vision():
            try:
                r = MoodVisionAnalyzer().analyze(capture_duration=5)
                vision_result.update(r)
            except Exception as e:
                print(f"⚠️  Vision error: {e}")
            finally:
                vision_done.set()

        t_audio  = threading.Thread(target=do_audio,  daemon=True)
        t_vision = threading.Thread(target=do_vision, daemon=True)
        t_audio.start()
        t_vision.start()

        audio_done.wait(timeout=10)
        vision_done.wait(timeout=10)

        set_state(step=2)

        # --- Step 3: fuse moods ---
        set_state(status="analyzing", step=3)
        controller  = SmartLightController()
        light_mode  = controller.process(audio_result, vision_result)
        time.sleep(0.4)

        # --- Step 4: apply lights ---
        set_state(step=4)
        apply_light_mode(light_mode)
        time.sleep(0.4)

        set_state(
            status       = "done",
            step         = 4,
            light_mode   = light_mode,
            audio_mood   = audio_result.get("audio_mood"),
            vision_mood  = vision_result.get("vision_mood"),
            audio_features = audio_result.get("audio_features", {}),
            faces        = vision_result.get("faces_detected", 0),
            smiles       = vision_result.get("smiles_detected", 0),
        )
        print(f"\n✅ Analysis complete — light mode: {light_mode}")

    except Exception as e:
        set_state(status="error", error=str(e))
        print(f"❌ Analysis error: {e}")


# ── Routes ───────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():
    """Kick off analysis in background; return immediately."""
    state = get_state()
    if state["status"] in ("recording", "analyzing"):
        return jsonify({"error": "Analysis already in progress"}), 409

    thread = threading.Thread(target=run_analysis, daemon=True)
    thread.start()
    return jsonify({"started": True})


@app.route("/status")
def status():
    """Poll endpoint — frontend calls this every 500 ms."""
    return jsonify(get_state())


@app.route("/update_light", methods=["POST"])
def update_light():
    """Internal simulator endpoint (also usable externally)."""
    data = request.json or {}
    mode = data.get("mode", "neutral")
    apply_light_mode(mode)
    return jsonify({"status": "success", "final_color": current_color})


@app.route("/current_color")
def current_color_route():
    return jsonify(current_color)


if __name__ == "__main__":
    print("🚀  MoodSync Light running at http://localhost:5000")
    app.run(port=5000, debug=False, threaded=True)
