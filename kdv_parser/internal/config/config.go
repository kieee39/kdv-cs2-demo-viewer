package config

import (
	"flag"
	"fmt"
	"os"
	"path/filepath"
)

type Config struct {
	SourcePath string // input .dem
	OutputPath string // output .kdz
	Debug      bool
}

func FromFlags() (Config, error) {
	var cfg Config
	flag.StringVar(&cfg.SourcePath, "s", "", "path to .dem")
	flag.StringVar(&cfg.OutputPath, "o", "", "path to output .kdz (default: same dir/name)")
	flag.BoolVar(&cfg.Debug, "debug", false, "verbose logging")
	flag.Parse()

	if cfg.SourcePath == "" {
		return cfg, fmt.Errorf("source path (-s) is required")
	}
	if _, err := os.Stat(cfg.SourcePath); err != nil {
		return cfg, fmt.Errorf("cannot stat source: %w", err)
	}

	if cfg.OutputPath == "" {
		base := cfg.SourcePath
		ext := filepath.Ext(base)
		cfg.OutputPath = base[:len(base)-len(ext)] + ".kdz"
	}

	return cfg, nil
}
