package main

import (
	"log"
	"kdv_parser/internal/config"
	"kdv_parser/internal/pipeline"
)

func main() {
	cfg, err := config.FromFlags()
	if err != nil {
		log.Fatalf("failed to parse flags: %v", err)
	}
	if err := pipeline.Run(cfg); err != nil {
		log.Fatalf("failed to run pipeline: %v", err)
	}
}
