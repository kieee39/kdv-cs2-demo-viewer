package pipeline

import (
	"errors"
	"fmt"
	"os"

	"kdv_parser/internal/config"
	"kdv_parser/internal/output"

	demoinfocs "github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs"
)

// Run orchestrates the two-pass parsing and file output.
func Run(cfg config.Config) error {
	state, err := ParseDemo(cfg)
	if err != nil {
		return fmt.Errorf("parse demo: %w", err)
	}

	if err := output.WriteKumademFile(cfg.OutputPath, &state.out); err != nil {
		return fmt.Errorf("write kdz: %w", err)
	}
	return nil
}

// ParseDemo runs detection and parsing in a single pass.
func ParseDemo(cfg config.Config) (*ParseState, error) {
	var meta RoundMeta

	f, err := os.Open(cfg.SourcePath)
	if err != nil {
		return nil, err
	}
	psr := demoinfocs.NewParser(f)

	det := &DetectState{cfg: cfg, meta: &meta}
	st := newBaseParseState(cfg, &meta, psr)
	var initErr error
	fmt.Printf("[parse] start parsing %s\n", cfg.SourcePath)

	ensureParseState := func() {
		if st.initialized {
			return
		}
		if err := st.finalizeWithMeta(psr); err != nil {
			if errors.Is(err, errMetaNotReady) {
				return
			}
			initErr = err
		}
	}

	registerDetectHandlers(psr, det)
	registerParseHandlers(psr, st, ensureParseState)

	if err := psr.ParseToEnd(); err != nil && !errors.Is(err, demoinfocs.ErrCancelled) {
		f.Close()
		return nil, err
	}

	if initErr != nil && !errors.Is(initErr, errMetaNotReady) {
		f.Close()
		return nil, initErr
	}
	if !st.initialized {
		if err := st.finalizeWithMeta(psr); err != nil {
			f.Close()
			return nil, fmt.Errorf("metadata incomplete after parse: %w", err)
		}
	}

	st.out.Header.RoundLength = len(meta.TargetFrames)
	if st.out.Header.MapName == "" {
		st.out.Header.MapName = meta.MapName
	}

	f.Close()
	return st, nil
}
