"""
MoodSync Light — Vision Analyzer
Captures 5 seconds from webcam, detects faces + smiles → classifies mood.
"""

import cv2
import time


class MoodVisionAnalyzer:

    def __init__(self):
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        self.smile_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_smile.xml"
        )

    # ── 1. Analyze video stream ─────────────────────────
    def analyze(self, capture_duration=5):
        print("📷 Starting camera...")
        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            print("⚠️  Camera not available — returning CALM default.")
            return {"vision_mood": "CALM", "faces_detected": 0, "smiles_detected": 0}

        face_total  = 0
        smile_total = 0
        frame_count = 0
        max_frames  = capture_duration * 20   # ~20 fps target

        start = time.time()

        while frame_count < max_frames and (time.time() - start) < capture_duration + 1:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.3, minNeighbors=5
            )
            face_total += len(faces)

            for (x, y, w, h) in faces:
                roi_gray = gray[y : y + h, x : x + w]
                smiles   = self.smile_cascade.detectMultiScale(
                    roi_gray, scaleFactor=1.7, minNeighbors=20
                )
                smile_total += len(smiles)

            frame_count += 1

        cap.release()
        cv2.destroyAllWindows()

        mood = self.classify_mood(face_total, smile_total)

        result = {
            "vision_mood":      mood,
            "faces_detected":   face_total,
            "smiles_detected":  smile_total,
        }
        print("\n🎭 Vision Analysis Result:")
        print(result)
        return result

    # ── 2. Mood logic ───────────────────────────────────
    def classify_mood(self, face_count, smile_count):
        if face_count == 0:
            return "CALM"
        if smile_count > 5:
            return "JOYFUL"
        if face_count > 20 and smile_count == 0:
            return "TENSE"
        return "CALM"


# ── Standalone test ─────────────────────────────────────
if __name__ == "__main__":
    MoodVisionAnalyzer().analyze(capture_duration=5)
