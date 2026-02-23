package pipeline

import (
	"fmt"

	"github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs"
	"github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs/events"

	"kdv_parser/pkg/kumadem"
)

func (st *ParseState) ensureEffectCapacity(idx int) {
	for len(st.currentRS.NadesSnapShots) <= idx {
		st.currentRS.NadesSnapShots = append(st.currentRS.NadesSnapShots, nil)
	}
	for len(st.currentRS.NadeEffectSnapShots) <= idx {
		st.currentRS.NadeEffectSnapShots = append(st.currentRS.NadeEffectSnapShots, nil)
	}
}

func (st *ParseState) onFrameDone(psr demoinfocs.Parser) {
	if st.meta == nil || !st.initialized || st.currentRound >= len(st.meta.TargetFrames) {
		return
	}
	currentf := psr.CurrentFrame()
	startFrame := st.meta.TargetFrames[st.currentRound]
	endFrame := -1
	if st.currentRound < len(st.meta.TargetEndFrames) {
		endFrame = st.meta.TargetEndFrames[st.currentRound]
	}

	if !st.isParsing && currentf >= startFrame {
		st.startCurrentRound(psr)
	}

	if st.isParsing && currentf == startFrame+128 {
		st.roundStartEqCalc(psr)
	}

	if st.isParsing && endFrame >= 0 && currentf >= endFrame {
		st.finishCurrentRound(psr)
		return
	}

	if st.isParsing && st.framePerSSInt != 0 && currentf%st.framePerSSInt == 1 {
		st.appendSnapshot(psr)
	}
}

func (st *ParseState) startCurrentRound(psr demoinfocs.Parser) {
	if st.cfg.Debug {
		fmt.Printf("<DEBUG>cf:%d Framedone Start\n", psr.CurrentFrame())
	}

	st.isParsing = true
	st.nowSSIndex = 0

	st.currentRI = new(kumadem.RoundInfo)
	st.currentRI.Team0isT = st.team0isT
	st.currentRI.Team0 = st.out.MatchStats.Team0
	st.currentRI.Team1 = st.out.MatchStats.Team1
	if st.currentRound == 0 {
		st.out.MatchStats.Init(psr)
	}
	st.currentRI.RoundStart(psr)

	st.currentRS = new(kumadem.RoundSnapshot)
	st.currentRS.Team0isT = st.team0isT
	st.currentRS.Team0 = st.out.MatchStats.Team0
	st.currentRS.Team1 = st.out.MatchStats.Team1
	for i, id := range st.out.MatchStats.Team0 {
		st.currentRS.PlayerSlot[i] = id
	}
	for i, id := range st.out.MatchStats.Team1 {
		st.currentRS.PlayerSlot[i+5] = id
	}
	st.currentRS.InitRoundStats(psr)
	st.currentRS.SetPlayerNames(psr, st.out.MatchStats.PlayerSteamID)

	st.currentPDS = new(kumadem.PlayerDrawingSnapShot)
	st.currentBS = new(kumadem.BombSnapShot)

	st.currentPDS.Update(psr, st.slotList, &st.metaMap, st.connectedPlayers)
	st.currentBS.Update(psr, &st.metaMap)

	st.currentGuidNdiMap = map[int64]*kumadem.NadeDrawingInfo{}
	st.tempGeidIndexMap = map[int]int{}
	st.ensureEffectCapacity(0)
}

func (st *ParseState) roundStartEqCalc(psr demoinfocs.Parser) {
	if st.cfg.Debug {
		fmt.Printf("<DEBUG>cf:%d Framedone Start+128\n", psr.CurrentFrame())
	}
	st.currentRI.RoundStartEqCalc(psr)
}

func (st *ParseState) finishCurrentRound(psr demoinfocs.Parser) {
	if st.cfg.Debug {
		fmt.Printf("<DEBUG>cf:%d Framedone End\n", psr.CurrentFrame())
	}
	st.isParsing = false

	st.currentRS.SetPlayerNames(psr, st.out.MatchStats.PlayerSteamID)
	st.fillTrailingTicks()
	st.mergeNades()
	st.currentRS.MarshalNadeEffect()
	st.out.RoundSnapshots = append(st.out.RoundSnapshots, *st.currentRS)

	if st.currentRound == len(st.out.MatchStats.RoundInfoList) {
		st.out.MatchStats.RoundInfoList = append(st.out.MatchStats.RoundInfoList, *st.currentRI)
	}

	fmt.Printf("[parse] round %d completed\n", st.currentRound+1)
	st.currentRound++
}

func (st *ParseState) fillTrailingTicks() {
	if len(st.currentRS.TickList) == 0 {
		return
	}
	last := findLastNonZero(st.currentRS.TickList)
	if last == 0 {
		return
	}
	for i := len(st.currentRS.TickList) - 1; i >= 0 && st.currentRS.TickList[i] == 0; i-- {
		st.currentRS.TickList[i] = last
	}
}

func findLastNonZero(list []int) int {
	for i := len(list) - 1; i >= 0; i-- {
		if list[i] != 0 {
			return list[i]
		}
	}
	return 0
}

// mergeNades maps nade drawing info to snapshot indices.
func (st *ParseState) mergeNades() {
	nssLen := len(st.currentRS.TickList)
	st.ensureEffectCapacity(nssLen)
	currentListIndex := 0
	for _, v := range st.currentGuidNdiMap {
		for i := 0; i < len(v.NadePointsList); i++ {
			targetIndex := v.StartSnapShotIndex + i
			if targetIndex < nssLen {
				st.currentRS.NadesSnapShots[targetIndex] = append(st.currentRS.NadesSnapShots[targetIndex], currentListIndex)
			}
		}
		st.currentRS.NadesDrawingInfoMap = append(st.currentRS.NadesDrawingInfoMap, *v)
		currentListIndex++
	}
}

func (st *ParseState) appendSnapshot(psr demoinfocs.Parser) {
	if st.cfg.Debug {
		fmt.Printf("<DEBUG>cf:%d Framedone Parsing\n", psr.CurrentFrame())
	}

	tick, _ := getTickAndFrame(psr)
	st.currentRS.TickList = append(st.currentRS.TickList, tick)
	st.currentRS.PlayerDrawingSnapShots = append(st.currentRS.PlayerDrawingSnapShots, *st.currentPDS)
	st.currentRS.BombSnapShots = append(st.currentRS.BombSnapShots, *st.currentBS)
	st.ensureEffectCapacity(st.nowSSIndex)

	st.currentPDS = new(kumadem.PlayerDrawingSnapShot)
	st.currentBS = new(kumadem.BombSnapShot)
	st.currentPDS.Update(psr, st.slotList, &st.metaMap, st.connectedPlayers)
	st.currentBS.Update(psr, &st.metaMap)

	gpm := psr.GameState().GrenadeProjectiles()
	for _, v := range gpm {
		uID := v.UniqueID()
		if st.currentGuidNdiMap[uID] == nil {
			continue
		}
		st.currentGuidNdiMap[uID].UpdateOnTickDone(st.nowSSIndex, v, &st.metaMap)
	}
	st.blindUserIDList = []int{}

	st.nowSSIndex++
	st.ensureEffectCapacity(st.nowSSIndex)
}

func (st *ParseState) onRoundEnd(psr demoinfocs.Parser, e events.RoundEnd) {
	if st.cfg.Debug {
		fmt.Printf("<DEBUG>cf:%d RoundEnd\n", psr.CurrentFrame())
	}
	if !st.isParsing {
		return
	}
	st.currentRI.RoundEnd(e, psr, st.connectedPlayers)
}

func (st *ParseState) onAnnouncement(psr demoinfocs.Parser) {
	if st.cfg.Debug {
		fmt.Printf("<DEBUG>cf:%d AnnouncementWinPanelMatch\n", psr.CurrentFrame())
	}
}

func (st *ParseState) onTeamSideSwitch() {
	if st.currentRound < 11 {
		return
	}
	st.team0isT = !st.team0isT
}
