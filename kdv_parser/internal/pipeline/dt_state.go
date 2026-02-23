package pipeline

import "kdv_parser/internal/config"

// DetectState holds the state for detecting rounds.
type DetectState struct {
	cfg  config.Config
	meta *RoundMeta

	inRound   bool
	tempFrame int
}
