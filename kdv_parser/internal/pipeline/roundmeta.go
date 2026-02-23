package pipeline

import (
	ex "github.com/markus-wa/demoinfocs-golang/v5/examples"
	common "github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs/common"
)

// RoundMeta holds metadata about a game round needed for parsing.
type RoundMeta struct {
	TargetFrames    []int
	TargetEndFrames []int
	FrameLength     int
	MapName         string
	MetaMap         ex.Map
	TempAll         []*common.Player
	TempTeam0       []uint64
	TempTeam1       []uint64
	TempPlayerIDs   []uint64
}

const CS2TickRate = 64
