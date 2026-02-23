package kumadem

import (
	demoinfocs "github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs"
	common "github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs/common"
	events "github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs/events"
)

type MatchStats struct {
	KdmVersion string
	Title      string
	HltvLink   string

	TeamName      [2]string
	RoundInfoList []RoundInfo
	PlayerSteamID [10]uint64
	Team0         [5]uint64
	Team1         [5]uint64
}

func (ms *MatchStats) Init(psr demoinfocs.Parser) {
	for i, _ := range ms.Team0 {
		player := FindBySteamID(ms.Team0[i], psr)
		if player != nil && player.TeamState != nil && player.TeamState.Opponent != nil {
			ms.TeamName[0] = player.TeamState.ClanName()
			ms.TeamName[1] = player.TeamState.Opponent.ClanName()
			break
		}
	}
	if ms.TeamName[0] == "" {
		ms.TeamName[0] = "Team0"
	}
	if ms.TeamName[1] == "" {
		ms.TeamName[1] = "Team1"
	}
}

type RoundInfo struct {
	RoundNumber int

	Team0isT bool

	Team0Side common.Team
	Team1Side common.Team
	Team0     [5]uint64
	Team1     [5]uint64

	EquipmentCounts [2]EquipmentCount
	EquipmentValues [2]int
	Money           [2]int

	BombPlantedSite rune

	Score        [2]int
	CorrectScore [2]int
	WinTeam      common.Team
	WinReason    events.RoundEndReason
}

func (ri *RoundInfo) RoundStart(psr demoinfocs.Parser) {
	ri.RoundNumber = psr.GameState().TotalRoundsPlayed()
	for i, _ := range ri.Team0 {
		player := FindBySteamID(ri.Team0[i], psr)
		if player == nil {
			continue
		}
		if player.Team == common.TeamTerrorists {
			ri.Team0Side = common.TeamTerrorists
		} else {
			ri.Team0Side = common.TeamCounterTerrorists
		}
	}
	for i, _ := range ri.Team1 {
		player := FindBySteamID(ri.Team1[i], psr)
		if player == nil {
			continue
		}
		if player.Team == common.TeamTerrorists {
			ri.Team1Side = common.TeamTerrorists
		} else {
			ri.Team1Side = common.TeamCounterTerrorists
		}
	}
}
func (ri *RoundInfo) RoundStartEqCalc(psr demoinfocs.Parser) {

	var t0, t1 *common.TeamState

	var playert0 *common.Player

	for _, p := range ri.Team0 {
		playert0 = FindBySteamID(p, psr)
		if playert0 != nil {
			break
		}
	}
	if playert0 == nil {
		return
	}
	if playert0.Team == common.TeamTerrorists {
		//if ri.Team0isT {
		t0 = psr.GameState().TeamTerrorists()
		t1 = psr.GameState().TeamCounterTerrorists()

	} else {
		t0 = psr.GameState().TeamCounterTerrorists()
		t1 = psr.GameState().TeamTerrorists()
	}
	if t0 == nil || t1 == nil {
		return
	}

	ri.EquipmentValues[0] = 0
	for _, v := range t0.Members() {
		ri.EquipmentValues[0] += v.EquipmentValueCurrent()
		ri.Money[0] += v.Money()
	}
	ri.EquipmentValues[1] = 0
	for _, v := range t1.Members() {
		ri.EquipmentValues[1] += v.EquipmentValueCurrent()
		ri.Money[1] += v.Money()
	}
	ri.EquipmentCounts[0].countWeapons(t0.Members())
	ri.EquipmentCounts[1].countWeapons(t1.Members())

}
func (ri *RoundInfo) Planted(site rune) {
	ri.BombPlantedSite = site
}

func (ri *RoundInfo) RoundEnd(e events.RoundEnd, psr demoinfocs.Parser, inserver map[uint64]string) {
	var t0State, t1State *common.TeamState

	ri.WinReason = e.Reason
	ri.WinTeam = e.Winner

	var playert0 *common.Player
	for _, p := range ri.Team0 {
		playert0 = FindBySteamID(p, psr)
		if _, ok := inserver[p]; !ok && playert0 != nil {
			break
		}

	}
	if playert0 == nil {
		return
	}
	if playert0.Team == common.TeamTerrorists {
		t0State = psr.GameState().TeamTerrorists()
		t1State = psr.GameState().TeamCounterTerrorists()
	} else {
		t0State = psr.GameState().TeamCounterTerrorists()
		t1State = psr.GameState().TeamTerrorists()
	}
	if t0State == nil || t1State == nil {
		return
	}
	ri.CorrectScore[0] = t0State.Score()
	ri.CorrectScore[1] = t1State.Score()
}

type EquipmentCount struct {
	AwpNumber   int
	RifleNumber int
	SmgNumber   int
}

func (ec *EquipmentCount) countWeapons(plist []*common.Player) {
	for _, v := range plist {
		if v == nil {
			continue
		}
		for _, eq := range v.Weapons() {
			if eq == nil {
				continue
			}
			switch eq.Type {
			case common.EqAWP:
				ec.AwpNumber++
			case common.EqGalil, common.EqAK47, common.EqSG553, common.EqAUG, common.EqFamas, common.EqM4A1, common.EqM4A4, common.EqG3SG1, common.EqScar20:
				ec.RifleNumber++
			case common.EqBizon, common.EqMP7, common.EqMP9, common.EqMac10, common.EqUMP, common.EqP90, common.EqMP5:
				ec.SmgNumber++
			default:
			}

		}
	}
}
