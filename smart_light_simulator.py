# light_simulator.py

from flask import Flask, request, jsonify
import random
import time

app = Flask(__name__)

current_color = {"r": 255, "g": 255, "b": 255}


def set_color(r, g, b):
    global current_color
    current_color = {"r": r, "g": g, "b": b}
    print("Light Color Updated:", current_color)


@app.route("/update_light", methods=["POST"])
def update_light():

    data = request.json
    mode = data.get("mode")

    if mode == "red":
        set_color(255, 0, 0)

    elif mode == "soothing_blue":
        set_color(0, 0, 255)

    elif mode == "neutral":
        set_color(200, 200, 200)

    elif mode == "disco":
        # Disco pulse effect
        print("Disco Mode Activated!")
        for _ in range(5):
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            set_color(r, g, b)
            time.sleep(0.5)

    return jsonify({
        "status": "success",
        "final_color": current_color
    })


if __name__ == "__main__":
    print("Starting Light Simulator on http://localhost:5000")
    app.run(port=5000)
