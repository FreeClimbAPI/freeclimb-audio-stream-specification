require("dotenv").config();
const grpc = require("@grpc/grpc-js");
const PROTO_PATH = process.env.PROTO_PATH || "../../proto/ivr.proto"
const GRPC_PORT = process.env.GRPC_PORT || "50051";
const protoLoader = require("@grpc/proto-loader");

const options = {
    keepCase: true,
    longs: String,
    enums: String,
    defaults: true,
    oneofs: true,
}

var packageDefinition = protoLoader.loadSync(PROTO_PATH, options);
const ivrProto = grpc.loadPackageDefinition(packageDefinition).freeclimb;

function SendIVRData(call) {
    console.log("Starting to handle streaming gRPC connection");
    let contentType = "";

    call.on("data", (message) => {
        switch (message.payload) {
            case "notify_audio_data":
                console.log(`Received Notify Audio Data message, seq: ${message.notify_audio_data.sequence_num}`);
                if (contentType) {
                    call.write({
                        audio_data: {
                            id: "testing",
                            audio_data: message.notify_audio_data.audio_data,
                            content_type: contentType,
                            sequence_num: message.notify_audio_data.sequence_num,
                        },
                    });
                } else {
                    console.error("ERROR: content type missing");
                }
                break;
            case "notify_dtmf_received_end_data":
                console.log(`Received Notify DTMF Received End message, DTMF: ${message.notify_dtmf_received_end_data.digit}`);
                call.write({
                    dtmf_data: {
                        id: "echo",
                        dtmf_digits: message.notify_dtmf_received_end_data.digit,
                        press_duration_ms: 100,
                        break_duration_ms: 100,
                        sequence_num: 1,
                    },
                });
                break;
            case "notify_call_started":
                console.log(`Received Notify Call Started message, Call ID: ${message.notify_call_started.call_id}`);
                contentType = message.notify_call_started.content_type;
                break;
            case "notify_call_ended":
                console.log(`Received Notify Call Ended message, Call ID: ${message.notify_call_ended.call_id}`);
                break;
            default:
                console.log("Other!");
            }
    });

    call.on("end", () => {
        console.log("Streaming gRPC connection completed");
        call.end();
    });

    call.on("error", (err) => {
        console.error(`gRPC Error: ${err.message}`);
    });
}

const server = new grpc.Server();
server.addService(ivrProto.GRPCStreamService.service, { SendIVRData });

server.bindAsync(
    `0.0.0.0:${GRPC_PORT}`,
    grpc.ServerCredentials.createInsecure(),
    (err, port) => {
        if (err) {
            console.errro(`gRPC server bind err: ${err.message}`);
            process.exit(1)
        }
        console.log(`Server running at 0.0.0.0:${port}`);
    }
);
