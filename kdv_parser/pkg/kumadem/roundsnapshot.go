package kumadem

import (
	ex "github.com/markus-wa/demoinfocs-golang/v5/examples"
	demoinfocs "github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs"
	"github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs/common"
	events "github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs/events"
)

type RoundSnapshot struct {
	// This list holds each tick-time of snapshot.
	Team0isT           bool
	TickList           []int
	RoundNumber        int
	RoundStartTick     int
	RoundStartFrame    int
	BombPlantedTick    int
	BombPlantedSSIndex int
	//BombWipedTick      int
	BombDetonatedSSIndex int
	BombDefusedSSIndex   int

	Team0Side common.Team
	Team1Side common.Team
	Team0     [5]uint64
	Team1     [5]uint64

	PlayerSlot  [10]uint64
	PlayerNames [10]string
	//PlayerLastPos [10]KDVector

	// These two values will be updated every SS update
	PlayerDrawingSnapShots []PlayerDrawingSnapShot
	BombSnapShots          []BombSnapShot
	// These will be every round end
	NadesSnapShots      [][]int
	NadeEffectSnapShots [][]int

	NadesDrawingInfoMap []NadeDrawingInfo
	NadeEffectMap       []NadeEffectInfo

	EventLogs []EventLog
	DeathLogs []DeathLog
}

type NadeEffectInfo struct {
	GEID        int
	StartTick   int
	EndTick     int
	ThrowerSide common.Team
	Point       KDVector
	NadeType    common.EquipmentType
}

func (rs *RoundSnapshot) InitRoundStats(psr demoinfocs.Parser) {
	rs.RoundNumber = psr.GameState().TotalRoundsPlayed()
	rs.RoundStartTick = psr.GameState().IngameTick()
	rs.RoundStartFrame = psr.CurrentFrame()

	if rs.RoundStartTick < 1 {
		rs.RoundStartTick = 1
	}
	for i, _ := range rs.Team0 {
		player := FindBySteamID(rs.Team0[i], psr)
		if player == nil {
			continue
		}
		if player.Team == common.TeamTerrorists {
			rs.Team0Side = common.TeamTerrorists
		} else {
			rs.Team0Side = common.TeamCounterTerrorists
		}
	}
	for i, _ := range rs.Team1 {
		player := FindBySteamID(rs.Team1[i], psr)
		if player == nil {
			continue
		}
		if player.Team == common.TeamTerrorists {
			rs.Team1Side = common.TeamTerrorists
		} else {
			rs.Team1Side = common.TeamCounterTerrorists
		}
	}
}
func (rs *RoundSnapshot) SetPlayerNames(psr demoinfocs.Parser, steamids [10]uint64) {
	for i, id := range steamids {
		player := FindBySteamID(id, psr)
		if player != nil {
			rs.PlayerNames[i] = player.Name
		} else {
			rs.PlayerNames[i] = "N/A"
		}
	}
}
func (rs *RoundSnapshot) findPlayerSlot(player *common.Player) int {
	if player == nil {
		return -1
	}
	for i, v := range rs.PlayerSlot {
		//if v == player.UserID {
		if v == player.SteamID64 {
			return i
		}
	}
	return -1
}

func (rs *RoundSnapshot) MarshalNadeEffect() {
	effectMapLen := len(rs.NadeEffectMap)
	ssLen := len(rs.NadeEffectSnapShots)
	for ei := 0; ei < effectMapLen; ei++ {
		for si := 0; si < ssLen-1; si++ {
			if isIn(ei, &rs.NadeEffectSnapShots[si]) == true {
				if isIn(ei, &rs.NadeEffectSnapShots[si+1]) == false {
					rs.NadeEffectSnapShots[si+1] = append(rs.NadeEffectSnapShots[si+1], ei)
				} else {
					break
				}
			}
		}
	}
}

func isIn(num int, sl *[]int) bool {
	for _, v := range *sl {
		if num == v {
			return true
		}
	}
	return false
}

type PlayerDrawingSnapShot struct {
	PlayerDrawingInfo [10]PlayerDrawingInfo
}

func (pds *PlayerDrawingSnapShot) Update(psr demoinfocs.Parser, slotList *[10]uint64, mp *ex.Map, inserver map[uint64]string) bool {

	bombCarrier := psr.GameState().Bomb().Carrier
	res := true

	for i, v := range slotList {
		targetPlayer := FindBySteamID(v, psr)
		if targetPlayer == nil {
			res = false
			continue
		}

		pds.PlayerDrawingInfo[i].update(targetPlayer, mp, inserver)
		if bombCarrier == targetPlayer {
			pds.PlayerDrawingInfo[i].HasBomb = true
		}
	}
	return res
}

func (pds *PlayerDrawingSnapShot) UpdateWeaponFired(psr demoinfocs.Parser, slotList *[10]uint64, e events.WeaponFire, mp *ex.Map, inserver map[uint64]string) {
	pds.Update(psr, slotList, mp, inserver)
	for i, v := range slotList {
		targetPlayer := FindBySteamID(v, psr)
		if _, ok := inserver[v]; !ok && targetPlayer == nil { //&& !targetPlayer.IsConnected {
			continue
		}
		if e.Shooter == targetPlayer {
			pds.PlayerDrawingInfo[i].Firing = true
			pds.PlayerDrawingInfo[i].ActiveEquipment = e.Weapon.Type
		}

	}
}

type BombSnapShot struct {
	Pos         KDVector
	OnGround    bool
	IsPlanted   bool
	IsDetonated bool
	IsDefused   bool
}

func (bs *BombSnapShot) Update(psr demoinfocs.Parser, mp *ex.Map) {
	bombstate := psr.GameState().Bomb()
	if bombstate.Carrier == nil {
		bs.Pos.ConvertWithMap(bombstate.Position(), mp)
		bs.OnGround = true
	}
}

type DeathLog struct {
	KillerTeamSide common.Team
	KillerPos      KDVector
	VictimPos      KDVector
}

func (kl *DeathLog) LogKill(killer *common.Player, victim *common.Player, mp *ex.Map) {
	if killer == nil || victim == nil {
		return
	}
	kl.KillerTeamSide = killer.Team
	kl.KillerPos.ConvertWithMap(killer.Position(), mp)
	kl.VictimPos.ConvertWithMap(victim.Position(), mp)
}
