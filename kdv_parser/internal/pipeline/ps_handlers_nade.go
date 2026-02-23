package pipeline

import (
	"fmt"

	demoinfocs "github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs"
	common "github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs/common"
	"github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs/events"

	"kdv_parser/pkg/kumadem"
)

func (st *ParseState) onNadeThrow(psr demoinfocs.Parser, e events.GrenadeProjectileThrow) {
	if st.cfg.Debug {
		fmt.Printf("<DEBUG>cf:%d GrenadeProjectileThrow\n", psr.CurrentFrame())
	}
	if !st.isParsing || e.Projectile == nil {
		return
	}
	tick, _ := getTickAndFrame(psr)
	newNDI := new(kumadem.NadeDrawingInfo)
	newNDI.Init(psr, st.currentRound, st.nowSSIndex, tick, e.Projectile, &st.metaMap)
	st.currentGuidNdiMap[e.Projectile.UniqueID()] = newNDI

	el := new(kumadem.EventLog)
	el.LogGrenadeThrown(tick, st.nowSSIndex, e)
	st.currentRS.EventLogs = append(st.currentRS.EventLogs, *el)
}

func (st *ParseState) onNadeBounce(psr demoinfocs.Parser, e events.GrenadeProjectileBounce) {
	if st.cfg.Debug {
		fmt.Printf("<DEBUG>cf:%d GrenadeProjectileBounce\n", psr.CurrentFrame())
	}
	if !st.isParsing || e.Projectile == nil {
		return
	}
	uID := e.Projectile.UniqueID()
	if st.currentGuidNdiMap[uID] == nil {
		return
	}
	st.currentGuidNdiMap[uID].UpdateOnBounce(st.nowSSIndex, e.Projectile, &st.metaMap)
}

func (st *ParseState) onSmokeStart(psr demoinfocs.Parser, e events.SmokeStart) {
	if st.cfg.Debug {
		fmt.Printf("<DEBUG>cf:%d SmokeStart\n", psr.CurrentFrame())
	}
	if !st.isParsing {
		return
	}
	st.ensureEffectCapacity(st.nowSSIndex)
	gpm := psr.GameState().GrenadeProjectiles()
	gp := gpm[e.GrenadeEntityID]
	if gp == nil {
		fmt.Println("Smoke doesn't exist!")
	} else if ndi := st.currentGuidNdiMap[gp.UniqueID()]; ndi != nil {
		ndi.DetonateLastElement(st.nowSSIndex, e.Position, &st.metaMap)
	}

	trgIndex := int(len(st.currentRS.NadeEffectMap))
	st.tempGeidIndexMap[e.GrenadeEntityID] = trgIndex
	var trgNF kumadem.NadeEffectInfo
	trgNF.StartTick = psr.GameState().IngameTick()

	trgNF.GEID = e.GrenadeEntityID
	if e.Thrower != nil {
		trgNF.ThrowerSide = e.Thrower.Team
	} else {
		trgNF.ThrowerSide = common.TeamUnassigned
	}

	trgNF.NadeType = e.GrenadeType
	trgNF.Point.ConvertWithMap(e.Position, &st.metaMap)
	st.currentRS.NadeEffectMap = append(st.currentRS.NadeEffectMap, trgNF)
	if st.nowSSIndex < len(st.currentRS.NadeEffectSnapShots) {
		st.currentRS.NadeEffectSnapShots[st.nowSSIndex] = append(st.currentRS.NadeEffectSnapShots[st.nowSSIndex], trgIndex)
	}
}

func (st *ParseState) onSmokeExpired(psr demoinfocs.Parser, e events.SmokeExpired) {
	if st.cfg.Debug {
		fmt.Printf("<DEBUG>cf:%d SmokeExpired\n", psr.CurrentFrame())
	}
	if !st.isParsing {
		return
	}
	st.ensureEffectCapacity(st.nowSSIndex)

	for i, v := range st.currentRS.NadeEffectMap {
		if e.GrenadeEntityID == v.GEID {
			st.currentRS.NadeEffectMap[i].EndTick = psr.GameState().IngameTick()
		}
	}

	trgIndex, ok := st.tempGeidIndexMap[e.GrenadeEntityID]
	if !ok {
		return
	}
	if st.nowSSIndex < len(st.currentRS.NadeEffectSnapShots) {
		st.currentRS.NadeEffectSnapShots[st.nowSSIndex] = append(st.currentRS.NadeEffectSnapShots[st.nowSSIndex], trgIndex)
	}
}

func (st *ParseState) onDecoyStart(psr demoinfocs.Parser, e events.DecoyStart) {
	if st.cfg.Debug {
		fmt.Printf("<DEBUG>cf:%d DecoyStart\n", psr.CurrentFrame())
	}
	if !st.isParsing {
		return
	}
	st.ensureEffectCapacity(st.nowSSIndex)
	gpm := psr.GameState().GrenadeProjectiles()
	gp := gpm[e.GrenadeEntityID]
	if gp == nil {
		fmt.Println("Decoy doesn't exist!")
	} else if ndi := st.currentGuidNdiMap[gp.UniqueID()]; ndi != nil {
		ndi.DetonateLastElement(st.nowSSIndex, e.Position, &st.metaMap)
	}

	trgIndex := int(len(st.currentRS.NadeEffectMap))
	st.tempGeidIndexMap[e.GrenadeEntityID] = trgIndex
	var trgNF kumadem.NadeEffectInfo
	trgNF.NadeType = e.GrenadeType
	trgNF.Point.ConvertWithMap(e.Position, &st.metaMap)
	st.currentRS.NadeEffectMap = append(st.currentRS.NadeEffectMap, trgNF)
	if st.nowSSIndex < len(st.currentRS.NadeEffectSnapShots) {
		st.currentRS.NadeEffectSnapShots[st.nowSSIndex] = append(st.currentRS.NadeEffectSnapShots[st.nowSSIndex], trgIndex)
	}
}

func (st *ParseState) onDecoyExpired(psr demoinfocs.Parser, e events.DecoyExpired) {
	if st.cfg.Debug {
		fmt.Printf("<DEBUG>cf:%d DecoyExpired\n", psr.CurrentFrame())
	}
	if !st.isParsing {
		return
	}
	st.ensureEffectCapacity(st.nowSSIndex)
	trgIndex, ok := st.tempGeidIndexMap[e.GrenadeEntityID]
	if !ok {
		return
	}
	if st.nowSSIndex < len(st.currentRS.NadeEffectSnapShots) {
		st.currentRS.NadeEffectSnapShots[st.nowSSIndex] = append(st.currentRS.NadeEffectSnapShots[st.nowSSIndex], trgIndex)
	}
}

func (st *ParseState) onFireStart(psr demoinfocs.Parser, e events.FireGrenadeStart) {
	if st.cfg.Debug {
		fmt.Printf("<DEBUG>cf:%d FireGrenadeStart\n", psr.CurrentFrame())
	}
	if !st.isParsing {
		return
	}
	st.ensureEffectCapacity(st.nowSSIndex)
	trgIndex := int(len(st.currentRS.NadeEffectMap))
	st.tempGeidIndexMap[e.GrenadeEntityID] = trgIndex
	var trgNF kumadem.NadeEffectInfo
	trgNF.NadeType = e.GrenadeType
	trgNF.GEID = e.GrenadeEntityID
	if e.Thrower != nil {
		trgNF.ThrowerSide = e.Thrower.Team
	} else {
		trgNF.ThrowerSide = common.TeamUnassigned
	}
	trgNF.Point.ConvertWithMap(e.Position, &st.metaMap)
	st.currentRS.NadeEffectMap = append(st.currentRS.NadeEffectMap, trgNF)
	if st.nowSSIndex < len(st.currentRS.NadeEffectSnapShots) {
		st.currentRS.NadeEffectSnapShots[st.nowSSIndex] = append(st.currentRS.NadeEffectSnapShots[st.nowSSIndex], trgIndex)
	}
}

func (st *ParseState) onFireExpired(psr demoinfocs.Parser, e events.FireGrenadeExpired) {
	if st.cfg.Debug {
		fmt.Printf("<DEBUG>cf:%d FireGrenadeExpired\n", psr.CurrentFrame())
	}
	if !st.isParsing {
		return
	}
	st.ensureEffectCapacity(st.nowSSIndex)
	for i, v := range st.currentRS.NadeEffectMap {
		if e.GrenadeEntityID == v.GEID {
			st.currentRS.NadeEffectMap[i].EndTick = psr.GameState().IngameTick()
		}
	}
	trgIndex, ok := st.tempGeidIndexMap[e.GrenadeEntityID]
	if !ok {
		return
	}
	if st.nowSSIndex < len(st.currentRS.NadeEffectSnapShots) {
		st.currentRS.NadeEffectSnapShots[st.nowSSIndex] = append(st.currentRS.NadeEffectSnapShots[st.nowSSIndex], trgIndex)
	}
}

func (st *ParseState) onHeExplode(psr demoinfocs.Parser, e events.HeExplode) {
	if st.cfg.Debug {
		fmt.Printf("<DEBUG>cf:%d HeExplode\n", psr.CurrentFrame())
	}
	if !st.isParsing {
		return
	}
	st.ensureEffectCapacity(st.nowSSIndex + 4)
	trgIndex := int(len(st.currentRS.NadeEffectMap))
	var trgNF kumadem.NadeEffectInfo
	trgNF.NadeType = e.GrenadeType
	trgNF.Point.ConvertWithMap(e.Position, &st.metaMap)
	st.currentRS.NadeEffectMap = append(st.currentRS.NadeEffectMap, trgNF)
	for i := 0; i < 5; i++ {
		if st.nowSSIndex+i < len(st.currentRS.NadeEffectSnapShots) {
			st.currentRS.NadeEffectSnapShots[st.nowSSIndex+i] = append(st.currentRS.NadeEffectSnapShots[st.nowSSIndex+i], trgIndex)
		}
	}
	gpm := psr.GameState().GrenadeProjectiles()
	if gp := gpm[e.GrenadeEntityID]; gp != nil {
		if ndi := st.currentGuidNdiMap[gp.UniqueID()]; ndi != nil {
			ndi.DetonateLastElement(st.nowSSIndex, e.Position, &st.metaMap)
		}
	}
}

func (st *ParseState) onFlashExplode(psr demoinfocs.Parser, e events.FlashExplode) {
	if st.cfg.Debug {
		fmt.Printf("<DEBUG>cf:%d FlashExplode\n", psr.CurrentFrame())
	}
	if !st.isParsing {
		return
	}
	st.ensureEffectCapacity(st.nowSSIndex + 4)
	trgIndex := int(len(st.currentRS.NadeEffectMap))
	var trgNF kumadem.NadeEffectInfo
	trgNF.NadeType = e.GrenadeType
	trgNF.Point.ConvertWithMap(e.Position, &st.metaMap)
	st.currentRS.NadeEffectMap = append(st.currentRS.NadeEffectMap, trgNF)
	for i := 0; i < 5; i++ {
		if st.nowSSIndex+i < len(st.currentRS.NadeEffectSnapShots) {
			st.currentRS.NadeEffectSnapShots[st.nowSSIndex+i] = append(st.currentRS.NadeEffectSnapShots[st.nowSSIndex+i], trgIndex)
		}
	}
}
