"""
MoodSync Light — Smart Light Controller
Fuses audio + vision mood → selects light mode → notifies simulator.
"""

import requests


class SmartLightController:

    def __init__(self, simulator_url="http://localhost:5001/update_light"):
        self.simulator_url = simulator_url

    # ── Decision logic ──────────────────────────────────
    def decide_light_mode(self, audio_mood, vision_mood, rms_db=0):
        """
        Fuse audio + vision signals into a single light mode.

        Priority order (highest → lowest):
          1. Very loud / screaming (rms_db > 20)  → RED
          2. Both agree on TENSE                  → SOOTHING_BLUE
          3. Either says JOYFUL                   → DISCO
          4. Vision TENSE, audio neutral          → SOOTHING_BLUE
          5. Default                              → NEUTRAL
        """

        # Scream / extreme volume
        if rms_db > 20:
            return "red"

        # Consensus: tension / argument
        if audio_mood == "TENSE" and vision_mood == "TENSE":
            return "soothing_blue"

        # Anger from audio alone (high confidence)
        if audio_mood == "TENSE":
            return "soothing_blue"

        # Laughter / joy (either source)
        if audio_mood == "JOYFUL" or vision_mood == "JOYFUL":
            return "disco"

        # Faces present but no smiles → mild tension
        if vision_mood == "TENSE":
            return "soothing_blue"

        return "neutral"

    # ── Send to in-process simulator ────────────────────
    def send_to_simulator(self, mode):
        payload = {"mode": mode}
        try:
            response = requests.post(self.simulator_url, json=payload, timeout=3)
            print(f"💡 Light Mode Sent: {mode}")
            print(f"   Simulator Response: {response.json()}")
            return response.json()
        except Exception as e:
            print(f"⚠️  Simulator not reachable: {e}")
            return {"status": "offline", "mode": mode}

    # ── Main entry called from app.py ───────────────────
    def process(self, audio_result, vision_result):
        audio_mood  = audio_result.get("audio_mood", "CALM")
        vision_mood = vision_result.get("vision_mood", "CALM")
        rms_db      = audio_result.get("audio_features", {}).get("rms_db", 0)

        mode = self.decide_light_mode(audio_mood, vision_mood, rms_db)
        return mode
