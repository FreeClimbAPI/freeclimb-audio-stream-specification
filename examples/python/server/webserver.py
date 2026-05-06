from flask import Flask, request, jsonify
import freeclimb
import os 
import sys
import json

app = Flask(__name__)

AUDIO_STREAM_HOST = os.environ.get("AUDIO_STREAM_HOST", None)
WEBHOOK_HOST = os.environ.get("WEBHOOK_HOST", None)

if not WEBHOOK_HOST:
    print("No WEBHOOK_HOST set")
    sys.exit(1)

if not AUDIO_STREAM_HOST:
    print("No AUDIO_STREAM_HOST set")
    sys.exit(1)

def build_audiostream_percl_body(
    *,
    audio_stream_host: str,
    webhook_base: str,
    callback_path: str = "/callback",
    content_type: str = "audio/l16;rate=16000",
    privacy_mode: bool = False,
) -> str:
    webhook_base = webhook_base.rstrip("/")
    stream = freeclimb.AudioStream(
        location=audio_stream_host,
        action_url=f"{webhook_base}{callback_path}",
        content_type=content_type,
        privacy_mode=privacy_mode,
    )
    d: dict[str, Any] = stream.to_dict()
    cmd = d.pop("command")
    inner = {k: v for k, v in d.items() if v is not None}
    inner["location"] = {"uri": audio_stream_host}
    return json.dumps([{cmd: inner}])


@app.route("/inbound", methods=["GET", "POST"])
def inbound():
    body = build_audiostream_percl_body(
        audio_stream_host=AUDIO_STREAM_HOST,
        webhook_base=WEBHOOK_HOST,
    )
    return body

@app.route("/callback", methods=["GET", "POST"])
def callback():
    print(request.json)
    return jsonify({}),200

if __name__ == "__main__":
    app.run(port=5001)
