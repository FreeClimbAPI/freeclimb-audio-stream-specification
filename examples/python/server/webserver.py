from flask import Flask, request, jsonify
import os 
import sys 

app = Flask(__name__)

AUDIO_STREAM_HOST = os.environ.get("AUDIO_STREAM_HOST", None)
WEBHOOK_HOST = os.environ.get("WEBHOOK_HOST", None)

if not WEBHOOK_HOST:
    print("No WEBHOOK_HOST set")
    sys.exit(1)

if not AUDIO_STREAM_HOST:
    print("No AUDIO_STREAM_HOST set")
    sys.exit(1)

percl = [
    {
        "AudioStream": {
            "location": {
                "uri": f"{AUDIO_STREAM_HOST}"
            },
            "contentType": "audio/mulaw;rate=8000",
            "actionUrl": f"{WEBHOOK_HOST}/callback",
            "metadata": ["testing"]
        }
    }    
]

@app.route("/inbound", methods=["GET", "POST"])
def inbound():
    return jsonify(percl)

@app.route("/callback", methods=["GET", "POST"])
def callback():
    print(request.json)
    return jsonify({}),200



if __name__ == "__main__":
    app.run(port=5001)
