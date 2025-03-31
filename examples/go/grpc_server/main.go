package main

import (
	pb "example/freeclimb"
	"fmt"
	"io"
	"log"
	"net"

	"google.golang.org/grpc"
)

type GRPCStreamServiceServer struct {
	pb.UnimplementedGRPCStreamServiceServer
}

func (s *GRPCStreamServiceServer) SendIVRData(stream pb.GRPCStreamService_SendIVRDataServer) error {
	log.Println("Starting to handle streaming grpc connection")

	var contentType string

	for {
		req, err := stream.Recv()
		if err == io.EOF {
			log.Println("Streaming grpc connection completed")
			return nil
		}
		if err != nil {
			log.Printf("Error receiving data: %v\n", err)
			return err
		}

		switch payload := req.GetPayload().(type) {
		case *pb.PlatformMessage_NotifyAudioData:
			log.Printf("Received Notify Audio Data message, seq: %d\n", payload.NotifyAudioData.SequenceNum)
			if contentType != "" {
				response := &pb.AppMessage{
					Payload: &pb.AppMessage_AudioData{
						AudioData: &pb.AppMessage_PlayAudioMessage{
							Id:          "testing",
							AudioData:   payload.NotifyAudioData.AudioData,
							ContentType: contentType,
							SequenceNum: payload.NotifyAudioData.SequenceNum,
						},
					},
				}
				if err := stream.Send(response); err != nil {
					log.Printf("Error sending response to Notify Audio Data message: %v", err)
					return err
				}
			} else {
				log.Println("ERROR: Content type missing")
			}
		case *pb.PlatformMessage_NotifyDtmfReceivedEndData:
			log.Printf("Received Notify DTMF Received End Data, DTMF finished: %s\n", payload.NotifyDtmfReceivedEndData.Digit)
			response := &pb.AppMessage{
				Payload: &pb.AppMessage_DtmfData{
					DtmfData: &pb.AppMessage_PressDTMFMessage{
						Id:              "echo",
						DtmfDigits:      payload.NotifyDtmfReceivedEndData.Digit,
						PressDurationMs: 100,
						BreakDurationMs: 100,
						SequenceNum:     1,
					},
				},
			}
			if err := stream.Send(response); err != nil {
				log.Printf("Error sending response to Notify DTMF Received End Data message: %v", err)
				return err
			}
		case *pb.PlatformMessage_NotifyCallStarted:
			log.Printf("Received Notify Call Started, Call ID: %s, ContentType: %s\n", payload.NotifyCallStarted.CallId, payload.NotifyCallStarted.ContentType)
			contentType = payload.NotifyCallStarted.ContentType
		case *pb.PlatformMessage_NotifyCallEnded:
			log.Printf("Received Notify Call Ended, Call ID: %s, Code: %v, Reason: %s\n", payload.NotifyCallEnded.CallId, payload.NotifyCallEnded.ReasonCode, payload.NotifyCallEnded.Reason)
		default:
			log.Println("Other!")
		}
	}
}

func main() {
	port := 50051
	lis, err := net.Listen("tcp", fmt.Sprintf(":%d", port))
	if err != nil {
		log.Fatalf("failed to listen on port 50051: %v", err)
	}

	s := grpc.NewServer()
	pb.RegisterGRPCStreamServiceServer(s, &GRPCStreamServiceServer{})

	log.Printf("gRPC server listening at %v\n", lis.Addr())
	if err := s.Serve(lis); err != nil {
		log.Fatalf("failed to serve: %v\n", err)
	}
}
