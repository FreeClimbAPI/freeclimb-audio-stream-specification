from concurrent import futures
import logging
from typing import Iterator
import os 

import grpc

from ivr_pb2 import AppMessage, PlatformMessage
import ivr_pb2
import ivr_pb2_grpc

class IVRServicer(ivr_pb2_grpc.GRPCStreamServiceServicer):
    def SendIVRData(self, request_iterator: Iterator[PlatformMessage], context) -> Iterator[AppMessage]:
        print("Starting to handle streaming grpc connection")
        content_type = ""
        try:
            p_message: ivr_pb2.PlatformMessage
            for p_message in request_iterator:
                payload = p_message.WhichOneof("payload")
                match payload:
                    case "notify_audio_data":
                        print(f"Received Notify Audio Data message, seq: {p_message.notify_audio_data.sequence_num}")
                        if content_type:
                            yield AppMessage(audio_data=AppMessage.PlayAudioMessage(id="testing", audio_data=p_message.notify_audio_data.audio_data, content_type=content_type, sequence_num=p_message.notify_audio_data.sequence_num))
                        else:
                            print("ERROR: content type missing")
                    case "notify_dtmf_received_end_data":
                        print("Received Notify DTMF Recieved End message, DTMF finished: {p_message.notify_dtmf_received_end_data.digit}")
                        yield AppMessage(dtmf_data=AppMessage.PressDTMFMessage(id="echo", dtmf_digits=p_message.notify_dtmf_received_end_data.digit, press_duration_ms=100, break_duration_ms=100, sequence_num=1))
                    case "notify_call_started":
                        print(f"Received Notify Call Started message, Call ID: {p_message.notify_call_started.call_id} Content Type: {p_message.notify_call_started.content_type}")
                        content_type = p_message.notify_call_started.content_type
                    case "notify_call_ended":
                        print(f"Received Notify Call Ended message, Call ID: {p_message.notify_call_ended.call_id} Code: {str(p_message.notify_call_ended.reason_code)} Reason: {p_message.notify_call_ended.reason}")
                    case _:
                        print("Other!")
        except Exception as e:
            print(f"Exception: {e}")
            print(f"Caught, stream closed")

        print("Streaming grpc connection completed")
        # one yield is required but won't actually send anything
        yield # type: ignore

def serve():
    print(f'Launching gRPC server on port {os.environ.get("gRPC_PORT", "50051")}')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    ivr_pb2_grpc.add_GRPCStreamServiceServicer_to_server(IVRServicer(), server)
    server.add_insecure_port(f'0.0.0.0:{os.environ.get("gRPC_PORT", "50051")}')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
