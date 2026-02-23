package kumadem

import (
	"time"

	demoinfocs "github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs"
)

type Header struct {
	MapName        string
	PlaybackTime   time.Duration
	PlaybackTicks  int
	PlaybackFrames int
	TickRate       float64
	FrameRate      float64
	SnapshotRate   int
	TickPerSS      float64
	RoundLength    int
	OriginalHash   string
}

func (h *Header) InitHeader(p demoinfocs.Parser, srate int) {

	h.TickRate = 64
	h.SnapshotRate = srate

}
