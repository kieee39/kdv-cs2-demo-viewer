package pipeline

import (
	"kdv_parser/internal/config"
	"kdv_parser/pkg/kumadem"

	ex "github.com/markus-wa/demoinfocs-golang/v5/examples"
	demoinfocs "github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs"
)

// ParseState holds the state of the parsing process.
type ParseState struct {
	cfg  config.Config
	meta *RoundMeta

	psr demoinfocs.Parser

	out kumadem.Kumadem

	ssrate        int
	framePerSS    float64
	framePerSSInt int

	currentRound int
	nowSSIndex   int
	isParsing    bool
	team0isT     bool

	currentRI  *kumadem.RoundInfo
	currentRS  *kumadem.RoundSnapshot
	currentPDS *kumadem.PlayerDrawingSnapShot
	currentBS  *kumadem.BombSnapShot

	currentGuidNdiMap map[int64]*kumadem.NadeDrawingInfo
	tempGeidIndexMap  map[int]int
	blindUserIDList   []int
	slotList          *[10]uint64
	connectedPlayers  map[uint64]string

	metaMap ex.Map

	initialized bool
}
