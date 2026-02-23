package pipeline

import (
	"fmt"
	"os"

	ex "github.com/markus-wa/demoinfocs-golang/v5/examples"
	demoinfocs "github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs"
	"github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs/events"
	"github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs/msg"

	"kdv_parser/internal/config"
)

// DetectRounds performs the first parsing pass to collect round boundaries and metadata.
func DetectRounds(cfg config.Config) (RoundMeta, error) {
	var meta RoundMeta
	st := &DetectState{cfg: cfg, meta: &meta}

	demoPath := cfg.SourcePath
	f, err := os.Open(demoPath)
	if err != nil {
		return meta, err
	}
	defer f.Close()

	psr := demoinfocs.NewParser(f)
	defer psr.Close()

	fmt.Printf("[detect] start scanning %s\n", demoPath)
	registerDetectHandlers(psr, st)

	psr.ParseToEnd()

	// Post-process frame lists
	if len(st.meta.TargetFrames) == len(st.meta.TargetEndFrames)+1 {
		if st.meta.TargetFrames[len(st.meta.TargetFrames)-1] <= st.meta.TargetEndFrames[len(st.meta.TargetEndFrames)-1] {
			st.meta.TargetFrames = st.meta.TargetFrames[:len(st.meta.TargetFrames)-1]
		} else {
			st.meta.TargetEndFrames = append(st.meta.TargetEndFrames, st.meta.FrameLength-64)
		}
	}
	if len(st.meta.TargetFrames) != len(st.meta.TargetEndFrames) {
		return meta, fmt.Errorf("detect: frame list length mismatch (start=%d end=%d)", len(st.meta.TargetFrames), len(st.meta.TargetEndFrames))
	}
	if len(st.meta.TargetFrames) == len(st.meta.TargetEndFrames)+1 {
		st.meta.TargetEndFrames = append(st.meta.TargetEndFrames, st.meta.FrameLength-64)
	}
	if len(st.meta.TargetFrames) != len(st.meta.TargetEndFrames) {
		return meta, fmt.Errorf("detect: frame list length mismatch after patch (start=%d end=%d)", len(st.meta.TargetFrames), len(st.meta.TargetEndFrames))
	}

	if len(st.meta.TempPlayerIDs) != 10 {
		if err := st.collectPlayers(); err != nil {
			return meta, err
		}
	}
	if len(st.meta.TempTeam0) != 5 || len(st.meta.TempTeam1) != 5 {
		if err := st.collectPlayers(); err != nil {
			return meta, err
		}
	}

	if cfg.Debug {
		fmt.Printf("\nPlayer's SteamIDs of Team0:%v\n", st.meta.TempTeam0)
		fmt.Printf("Player's SteamIDs of Team1:%v\n", st.meta.TempTeam1)
		fmt.Printf("Nnumbers of the frame where each round starts:%v\n", st.meta.TargetFrames)
		fmt.Printf("Nnumbers of the frame where each round ends:%v\n", st.meta.TargetEndFrames)
		fmt.Printf("Length of total rounds : %d\n", len(st.meta.TargetEndFrames))
	}

	meta.TargetFrames = st.meta.TargetFrames
	meta.TargetEndFrames = st.meta.TargetEndFrames
	meta.FrameLength = st.meta.FrameLength
	meta.MapName = st.meta.MapName
	meta.MetaMap = st.meta.MetaMap
	meta.TempAll = st.meta.TempAll
	meta.TempTeam0 = st.meta.TempTeam0
	meta.TempTeam1 = st.meta.TempTeam1
	meta.TempPlayerIDs = st.meta.TempPlayerIDs

	fmt.Printf("[detect] teams: %v vs %v\n", meta.TempTeam0, meta.TempTeam1)
	fmt.Printf("[detect] rounds detected: %d (map: %s)\n", len(st.meta.TargetEndFrames), meta.MapName)

	return meta, nil
}

func registerDetectHandlers(psr demoinfocs.Parser, st *DetectState) {
	// Map metadata
	psr.RegisterNetMessageHandler(func(m *msg.CSVCMsg_ServerInfo) {
		st.meta.MetaMap = ex.GetMapMetadata(m.GetMapName())
		st.meta.MapName = m.GetMapName()
	})

	psr.RegisterEventHandler(func(e events.MatchStart) { st.onMatchStart(psr) })
	psr.RegisterEventHandler(func(e events.RoundStart) { st.onRoundStart(psr) })
	psr.RegisterEventHandler(func(e events.RoundFreezetimeEnd) { st.onFreezeEnd(psr) })
	psr.RegisterEventHandler(func(e events.RoundEnd) { st.onRoundEnd(psr) })
	psr.RegisterEventHandler(func(e events.RoundEndOfficial) { st.onRoundEndOfficial(psr) })
	psr.RegisterEventHandler(func(e events.OvertimeNumberChanged) { st.onOvertimeChanged(psr) })
	psr.RegisterEventHandler(func(e events.TeamSideSwitch) { st.onTeamSideSwitch(psr) })
	psr.RegisterEventHandler(func(e events.PlayerConnect) { st.onPlayerConnect(psr, e) })
	psr.RegisterEventHandler(func(e events.PlayerDisconnected) { st.onPlayerDisconnected(psr, e) })
	psr.RegisterEventHandler(func(e events.FrameDone) { st.onFrameDone(psr) })
}
