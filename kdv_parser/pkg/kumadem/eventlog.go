package kumadem

import (
	"fmt"

	common "github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs/common"
	events "github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs/events"
)

type EventLog struct {
	Tick    int
	SsIndex int
	Side    string
	Type    string
	Log     string
}

func (el *EventLog) LogKill(tick int, ssindex int, killer *common.Player, victim *common.Player, weapon *common.Equipment, hs bool, wb bool) {
	el.Tick = tick
	el.SsIndex = ssindex
	el.Type = "Kill"
	kl := ""
	wep := ""
	vic := ""

	if killer != nil {
		kl = killer.Name
	}

	if weapon != nil {
		wep = weapon.String()
	}

	if victim != nil {
		vic = victim.Name
	}

	if killer == nil {
		el.Side = "nil"
	} else if killer.Team == common.TeamTerrorists {
		el.Side = "T"
	} else {
		el.Side = "CT"
	}
	hss := ""
	wbs := ""
	if hs {
		hss = "(H)"
	}
	if wb {
		wbs = "(W)"
	}

	el.Log = fmt.Sprintf("\"%s\" [ %s %s%s] \"%s\"", kl, wep, wbs, hss, vic)
}
func (el *EventLog) LogPlanted(tick int, ssindex int, e events.BombPlanted) {
	el.Tick = tick
	el.SsIndex = ssindex
	el.Type = fmt.Sprintf("Planted%s", string(e.Site))
	el.Side = "T"
	playerName := "Unknown"
	if e.Player != nil {
		playerName = e.Player.Name
	}
	el.Log = fmt.Sprintf("\"%s\" planted bomb at %s", playerName, string(e.Site))
}

func (el *EventLog) LogPlanting(tick int, ssindex int, e events.BombPlantBegin) {
	el.Tick = tick
	el.SsIndex = ssindex
	el.Type = fmt.Sprintf("Planting%s", string(e.Site))
	el.Side = "T"
	playerName := "Unknown"
	if e.Player != nil {
		playerName = e.Player.Name
	}
	el.Log = fmt.Sprintf("\"%s\" begins to plant at %s", playerName, string(e.Site))
}

func (el *EventLog) LogDefusing(tick int, ssindex int, e events.BombDefuseStart) {
	el.Tick = tick
	el.SsIndex = ssindex
	el.Type = "Defusing"
	el.Side = "CT"
	kit := ""
	if e.HasKit == true {
		kit = "(Kit)"
	}
	playerName := "Unknown"
	if e.Player != nil {
		playerName = e.Player.Name
	}
	el.Log = fmt.Sprintf("\"%s\" begins to defuse %s", playerName, kit)
}

func (el *EventLog) LogGrenadeThrown(tick int, ssindex int, e events.GrenadeProjectileThrow) {
	el.Tick = tick
	el.SsIndex = ssindex
	el.Type = "GrenadeThrown"
	el.Side = "N/A"

	if e.Projectile == nil || e.Projectile.Thrower == nil {
		el.Log = "Unknown player threw a grenade"
		return
	}

	if e.Projectile.Thrower.Team == common.TeamTerrorists {
		el.Side = "T"
	} else if e.Projectile.Thrower.Team == common.TeamCounterTerrorists {
		el.Side = "CT"
	}
	weapon := "grenade"
	if e.Projectile.WeaponInstance != nil {
		weapon = e.Projectile.WeaponInstance.String()
	}
	el.Log = fmt.Sprintf("\"%s\" threw %s", e.Projectile.Thrower.Name, weapon)
}
