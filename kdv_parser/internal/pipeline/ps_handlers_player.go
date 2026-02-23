package pipeline

import (
	"fmt"

	demoinfocs "github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs"
	"github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs/events"

	"kdv_parser/pkg/kumadem"
)

func (st *ParseState) onWeaponFire(psr demoinfocs.Parser, e events.WeaponFire) {
	if st.cfg.Debug {
		fmt.Printf("<DEBUG>cf:%d WeaponFire\n", psr.CurrentFrame())
	}
	if !st.isParsing || e.Shooter == nil || e.Weapon == nil {
		return
	}
	st.currentPDS.UpdateWeaponFired(psr, st.slotList, e, &st.metaMap, st.connectedPlayers)
}

func (st *ParseState) onKill(psr demoinfocs.Parser, e events.Kill) {
	if st.cfg.Debug {
		fmt.Printf("<DEBUG>cf:%d Kill\n", psr.CurrentFrame())
	}
	if !st.isParsing {
		return
	}
	tick, _ := getTickAndFrame(psr)
	var wb bool
	if e.PenetratedObjects > 0 {
		wb = true
	}
	el := new(kumadem.EventLog)
	el.LogKill(tick, st.nowSSIndex, e.Killer, e.Victim, e.Weapon, e.IsHeadshot, wb)
	st.currentRS.EventLogs = append(st.currentRS.EventLogs, *el)

	if e.Killer != nil && e.Victim != nil {
		kl := new(kumadem.DeathLog)
		kl.LogKill(e.Killer, e.Victim, &st.metaMap)
		st.currentRS.DeathLogs = append(st.currentRS.DeathLogs, *kl)
	}
}

func (st *ParseState) onPlayerFlashed(psr demoinfocs.Parser, e events.PlayerFlashed) {
	if st.cfg.Debug {
		fmt.Printf("<DEBUG>cf:%d PlayerFlashed\n", psr.CurrentFrame())
	}
	if !st.isParsing || e.Player == nil {
		return
	}
	st.blindUserIDList = append(st.blindUserIDList, e.Player.UserID)
}

func (st *ParseState) onPlayerConnect(psr demoinfocs.Parser, e events.PlayerConnect) {
	if st.cfg.Debug {
		fmt.Printf("<DEBUG>cf:%d PlayerConnect\n", psr.CurrentFrame())
	}
	if e.Player == nil {
		return
	}
	st.connectedPlayers[e.Player.SteamID64] = e.Player.Name
	if !st.isParsing {
		return
	}
	st.currentRS.SetPlayerNames(psr, st.out.MatchStats.PlayerSteamID)
}

func (st *ParseState) onPlayerDisconnected(e events.PlayerDisconnected) {
	if e.Player == nil {
		return
	}
	delete(st.connectedPlayers, e.Player.SteamID64)
}
