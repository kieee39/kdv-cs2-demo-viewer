package pipeline

import (
	"bufio"
	"errors"
	"fmt"
	"math"
	"os"
	"strconv"

	demoinfocs "github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs"

	"kdv_parser/internal/config"
	"kdv_parser/pkg/kumadem"
)

var errMetaNotReady = errors.New("metadata not ready yet")

func newBaseParseState(cfg config.Config, meta *RoundMeta, psr demoinfocs.Parser) *ParseState {
	st := &ParseState{
		cfg:               cfg,
		meta:              meta,
		psr:               psr,
		ssrate:            32,
		framePerSS:        2.0,
		currentGuidNdiMap: map[int64]*kumadem.NadeDrawingInfo{},
		tempGeidIndexMap:  map[int]int{},
		blindUserIDList:   []int{},
		connectedPlayers:  map[uint64]string{},
		metaMap:           meta.MetaMap,
		team0isT:          true,
	}
	st.framePerSSInt = int(math.Round(st.framePerSS))
	st.slotList = &st.out.MatchStats.PlayerSteamID

	demMD5, _ := md5sum(cfg.SourcePath)
	st.out.Header.OriginalHash = demMD5

	st.out.MatchStats.KdmVersion = "1.0.2"
	return st
}

// newParseState initializes ParseState with header/match stats and basic parameters.
func newParseState(cfg config.Config, meta *RoundMeta, psr demoinfocs.Parser) (*ParseState, error) {
	st := newBaseParseState(cfg, meta, psr)
	if err := st.finalizeWithMeta(psr); err != nil {
		return nil, err
	}
	return st, nil
}

// finalizeWithMeta populates the parts of ParseState that depend on parsed metadata.
func (st *ParseState) finalizeWithMeta(psr demoinfocs.Parser) error {
	if st.initialized {
		return nil
	}
	if st.meta == nil || len(st.meta.TempTeam0) != 5 || len(st.meta.TempTeam1) != 5 {
		return errMetaNotReady
	}

	for i, id := range st.meta.TempTeam0 {
		st.out.MatchStats.PlayerSteamID[i] = id
	}
	for i, id := range st.meta.TempTeam1 {
		st.out.MatchStats.PlayerSteamID[i+5] = id
	}
	st.out.MatchStats.Team0 = [5]uint64(st.meta.TempTeam0)
	st.out.MatchStats.Team1 = [5]uint64(st.meta.TempTeam1)

	st.metaMap = st.meta.MetaMap

	st.out.Header.InitHeader(psr, st.ssrate)
	st.out.Header.RoundLength = len(st.meta.TargetFrames)
	st.out.Header.MapName = st.meta.MapName

	if math.IsNaN(st.framePerSS) {
		fmt.Print("<ERROR>: Header corrupted!\n")
		stdin := bufio.NewScanner(os.Stdin)
		fmt.Print("<ERROR>: Set FrameRate(int) manually (32,64,128,etc) :")
		stdin.Scan()
		text := stdin.Text()
		value, _ := strconv.Atoi(text)
		st.framePerSS = float64(value / st.ssrate)
		st.framePerSSInt = int(math.Round(st.framePerSS))
		st.out.Header.FrameRate = float64(value)
		if value <= 32 {
			st.framePerSS = 1
			st.framePerSSInt = 1
		}
		fmt.Print("<ERROR>: Set TickRate(int) manually (64,128,etc) :")
		stdin.Scan()
		text = stdin.Text()
		value, _ = strconv.Atoi(text)
		st.out.Header.TickRate = float64(value)
	}
	if st.out.Header.FrameRate == 0 {
		value := CS2TickRate
		st.framePerSS = float64(value / st.ssrate)
		st.framePerSSInt = int(math.Round(st.framePerSS))
		st.out.Header.FrameRate = float64(value)
	}
	if st.out.Header.TickRate == 0 {
		fmt.Print("<ERROR>: TickRate(int) must not be zero. Set it manually (32,64,128,etc) :")
		stdin := bufio.NewScanner(os.Stdin)
		for {
			stdin.Scan()
			text := stdin.Text()
			value, _ := strconv.Atoi(text)
			if value != 0 {
				st.out.Header.TickRate = float64(value)
				break
			}
		}
		st.out.Header.TickPerSS = st.out.Header.TickRate / float64(st.ssrate)
	}

	if st.out.Header.FrameRate < 32 {
		st.out.Header.SnapshotRate = int(math.Round(st.out.Header.FrameRate))
	}

	st.initialized = true
	return nil
}
