require("dotenv").config();
const express = require("express");
const freeclimbSDK = require("@freeclimb/sdk");

const { PerclScript, AudioStream } = freeclimbSDK;

const app = express();

const AUDIO_STREAM_HOST = process.env.AUDIO_STREAM_HOST;
const WEBHOOK_HOST = process.env.WEBHOOK_HOST;
const PORT = process.env.PORT || 5001;

if (!AUDIO_STREAM_HOST) {
  console.error("No AUDIO_STREAM_HOST set");
  process.exit(1);
}

if (!WEBHOOK_HOST) {
  console.error("No WEBHOOK_HOST set");
  process.exit(1);
}

const percl = new PerclScript({
  commands: [
    new AudioStream({
      location: {
        uri: `${AUDIO_STREAM_HOST}`,
      },
      contentType: "audio/l16;rate=16000",
      actionUrl: `${WEBHOOK_HOST}/callback`,
      metadata: ["testing"],
      privacyMode: false,
    }),
  ],
});

app.use(express.json());

app.post("/inbound", (req, res) => {
  res.status(200).json(percl.build());
});

app.post("/callback", (req, res) => {
  console.log(req.body);
  res.status(200).json({});
});

app.listen(PORT, () => {
  console.log(`Express server running on port ${PORT}`);
});
