package main

import (
	"fmt"
	"log"
	"runtime/debug"

	"kdv_parser/internal/config"
	"kdv_parser/internal/pipeline"
)

const demoInfocsModule = "github.com/markus-wa/demoinfocs-golang/v5"

func main() {
	printDemoInfocsVersion()

	cfg, err := config.FromFlags()
	if err != nil {
		log.Fatalf("failed to parse flags: %v", err)
	}
	if err := pipeline.Run(cfg); err != nil {
		log.Fatalf("failed to run pipeline: %v", err)
	}
}

func printDemoInfocsVersion() {
	info, ok := debug.ReadBuildInfo()
	if !ok {
		fmt.Printf("[startup] demoinfocs-golang: unknown (build info unavailable)\n")
		return
	}

	for _, dep := range info.Deps {
		if dep.Path != demoInfocsModule {
			continue
		}
		if dep.Replace != nil {
			fmt.Printf("[startup] demoinfocs-golang: %s (replaced by %s %s)\n", dep.Version, dep.Replace.Path, dep.Replace.Version)
			return
		}
		fmt.Printf("[startup] demoinfocs-golang: %s\n", dep.Version)
		return
	}

	fmt.Printf("[startup] demoinfocs-golang: unknown (module not found in build info)\n")
}
