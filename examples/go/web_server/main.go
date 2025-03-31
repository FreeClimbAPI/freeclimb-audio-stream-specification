package main

import (
	"encoding/json"
	"log"
	"net/http"
	"os"
)

var percl = []map[string]interface{}{
	{
		"AudioStream": map[string]interface{}{
			"location": map[string]string{
				"uri": "",
			},
			"contentType": "audio/mulaw;rate=8000",
			"actionUrl":   "",
			"metadata":    []string{"testing"},
		},
	},
}

func inboundHandler(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(percl)
}

func callbackHandler(w http.ResponseWriter, r *http.Request) {
	var requestData map[string]interface{}

	if err := json.NewDecoder(r.Body).Decode(&requestData); err != nil {
		http.Error(w, "Invalid JSON", http.StatusBadRequest)
		return
	}

	log.Printf("Received JSON: %v\n", requestData)

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
}

func main() {
	audioStreamHost := os.Getenv("AUDIO_STREAM_HOST")
	webhookHost := os.Getenv("WEBHOOK_HOST")

	if audioStreamHost == "" {
		log.Fatal("No AUDIO_STREAM_HOST set")
	}
	if webhookHost == "" {
		log.Fatal("No WEBHOOK_HOST set")
	}

	percl[0]["AudioStream"].(map[string]interface{})["location"].(map[string]string)["uri"] = audioStreamHost
	percl[0]["AudioStream"].(map[string]interface{})["actionUrl"] = webhookHost + "/callback"
	router := http.NewServeMux()

	router.HandleFunc("POST /inbound", inboundHandler)
	router.HandleFunc("POST /callback", callbackHandler)

	server := http.Server{
		Addr:    ":5001",
		Handler: router,
	}

	log.Println("Starting server on port: 5001")
	server.ListenAndServe()
}
