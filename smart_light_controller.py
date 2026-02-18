# smart_light_controller.py

import requests


class SmartLightController:

    def __init__(self, simulator_url="http://localhost:5000/update_light"):
        self.simulator_url = simulator_url

    def decide_light_behavior(self, audio_mood, volume_level):
        """
        Decide final light mode based on audio + environment
        """

        # 🔥 If screaming (very loud)
        if volume_level > 80:
            return "red"

        # 😡 Arguing / Angry (loud but not extreme)
        if audio_mood == "angry":
            return "soothing_blue"

        # 😂 Laughing / Happy
        if audio_mood == "happy":
            return "disco"

        # Default
        return "neutral"

    def send_to_simulator(self, mode):

        payload = {"mode": mode}

        try:
            response = requests.post(self.simulator_url, json=payload)
            print("Light Mode Sent:", mode)
            print("Simulator Response:", response.json())
        except Exception as e:
            print("Simulator not running:", e)

    def process(self, audio_mood, volume_level):
        """
        Main function called from main.py
        """

        mode = self.decide_light_behavior(audio_mood, volume_level)
        self.send_to_simulator(mode)
