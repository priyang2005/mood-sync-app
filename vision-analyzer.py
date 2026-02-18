import cv2


class MoodVisionAnalyzer:

    def __init__(self):

        # Load Haar Cascades from OpenCV
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

        self.smile_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_smile.xml"
        )

    # --------------------------------------------------
    # 1️⃣ Analyze Video
    # --------------------------------------------------
    def analyze(self, capture_duration=5):

        print("📷 Starting camera...")
        cap = cv2.VideoCapture(0)

        face_count_total = 0
        smile_count_total = 0
        frame_count = 0

        max_frames = capture_duration * 20  # approx 20 FPS

        while frame_count < max_frames:

            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # STEP 3: Detect Faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.3,
                minNeighbors=5
            )

            face_count_total += len(faces)

            for (x, y, w, h) in faces:

                roi_gray = gray[y:y+h, x:x+w]

                # STEP 4: Detect Smile inside face
                smiles = self.smile_cascade.detectMultiScale(
                    roi_gray,
                    scaleFactor=1.7,
                    minNeighbors=20
                )

                smile_count_total += len(smiles)

            frame_count += 1

        cap.release()
        cv2.destroyAllWindows()

        # --------------------------------------------------
        # STEP 6: Determine Mood
        # --------------------------------------------------
        mood = self.classify_mood(face_count_total, smile_count_total)

        result = {
            "vision_mood": mood,
            "faces_detected": face_count_total,
            "smiles_detected": smile_count_total
        }

        print("\n🎭 Vision Analysis Result:")
        print(result)

        return result

    # --------------------------------------------------
    # Mood Logic (Simple Rules)
    # --------------------------------------------------
    def classify_mood(self, face_count, smile_count):

        if face_count == 0:
            return "CALM"

        if smile_count > 5:
            return "JOYFUL"

        if face_count > 20 and smile_count == 0:
            return "TENSE"

        return "CALM"


# --------------------------------------------------
# Standalone Test
# --------------------------------------------------
if __name__ == "__main__":
    analyzer = MoodVisionAnalyzer()
    analyzer.analyze(capture_duration=5)
