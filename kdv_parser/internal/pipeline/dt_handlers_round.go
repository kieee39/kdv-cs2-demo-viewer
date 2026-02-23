package pipeline

import (
	"fmt"

	demoinfocs "github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs"
)

func (st *DetectState) onMatchStart(psr demoinfocs.Parser) {
	tick, frame := getTickAndFrame(psr)
	if st.cfg.Debug {
		fmt.Printf("(MatchStarted t:%d f:%d)", tick, frame)
	}
	st.roundEnds(psr)
}

func (st *DetectState) onRoundStart(psr demoinfocs.Parser) {
	tick, frame := getTickAndFrame(psr)
	if st.cfg.Debug {
		fmt.Printf("(RoundStarted t:%d f:%d)", tick, frame)
	}
	st.tempFrame = frame
	st.roundEnds(psr)
}

func (st *DetectState) onFreezeEnd(psr demoinfocs.Parser) {
	tick, frame := getTickAndFrame(psr)
	if st.cfg.Debug {
		fmt.Printf("(FreezetimeEnded t:%d f:%d)", tick, frame)
		fmt.Printf("RoundNum: %d ", psr.GameState().TotalRoundsPlayed())
	}
	st.tempFrame = -1
	st.roundEnds(psr)
	st.roundStarts(psr)
	st.setPlayerSteamID(psr)
	st.setTeamID(psr)
}

func (st *DetectState) onRoundEnd(psr demoinfocs.Parser) {
	tick, frame := getTickAndFrame(psr)
	if st.cfg.Debug {
		fmt.Printf("(RoundEnd t:%d f:%d)", tick, frame)
	}
	if st.tempFrame != -1 {
		st.meta.TargetFrames = append(st.meta.TargetFrames, st.tempFrame)
		st.meta.TargetEndFrames = append(st.meta.TargetEndFrames, frame+64)
	}
	st.roundEnds(psr)
	st.setPlayerSteamID(psr)
	st.setTeamID(psr)
	st.meta.TempAll = psr.GameState().Participants().All()
}

func (st *DetectState) onRoundEndOfficial(psr demoinfocs.Parser) {
	tick, frame := getTickAndFrame(psr)
	if st.cfg.Debug {
		fmt.Printf("(RoundEndedOfficialy t:%d f:%d)\n", tick, frame)
	}
	st.roundEnds(psr)
}

func (st *DetectState) onOvertimeChanged(psr demoinfocs.Parser) {
	tick, frame := getTickAndFrame(psr)
	if st.cfg.Debug {
		fmt.Printf("(OvertimeNumberChanged t:%d f:%d)", tick, frame)
	}
}

func (st *DetectState) onTeamSideSwitch(psr demoinfocs.Parser) {
	tick, frame := getTickAndFrame(psr)
	if st.cfg.Debug {
		fmt.Printf("(TeamSideSwitch t:%d f:%d)\n", tick, frame)
	}
}

func (st *DetectState) roundStarts(psr demoinfocs.Parser) {
	if !st.inRound {
		_, frame := getTickAndFrame(psr)
		st.meta.TargetFrames = append(st.meta.TargetFrames, frame)
		st.inRound = true
	}
}

func (st *DetectState) roundEnds(psr demoinfocs.Parser) {
	if st.inRound {
		_, frame := getTickAndFrame(psr)
		st.meta.TargetEndFrames = append(st.meta.TargetEndFrames, frame+64)
		st.inRound = false
	}
}
