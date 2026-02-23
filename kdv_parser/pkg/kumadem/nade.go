package kumadem

import (
	"github.com/golang/geo/r3"
	ex "github.com/markus-wa/demoinfocs-golang/v5/examples"
	demoinfocs "github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs"
	common "github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs/common"
)

type NadeDrawingInfo struct {
	UID         int64
	EID         int
	RoundNumber int
	StartTick   int
	ThrowerName string
	ThrowerSide common.Team
	ThrowPos    r3.Vector
	ThrowAngX   float32
	ThrowAngY   float32
	IsDucking   bool

	StartSnapShotIndex int
	NadeType           common.EquipmentType
	NadePointsList     []NadePoints
}

func (ndi *NadeDrawingInfo) Init(psr demoinfocs.Parser, ridx int, ssidx int, tick int, gp *common.GrenadeProjectile, mp *ex.Map) {
	if ndi == nil || gp == nil {
		return
	}
	ndi.UID = gp.UniqueID()
	if gp.Entity != nil {
		ndi.EID = gp.Entity.ID()
	}
	//ndi.RoundNumber = ridx + 1
	if psr != nil {
		ndi.RoundNumber = psr.GameState().TotalRoundsPlayed()
	}
	ndi.StartSnapShotIndex = ssidx
	ndi.StartTick = tick

	thr := gp.Thrower

	if thr != nil {
		ndi.ThrowerName = thr.Name
		ndi.ThrowerSide = thr.Team
		ndi.ThrowPos = thr.Position()
		ndi.ThrowAngX = thr.ViewDirectionX()
		ndi.ThrowAngY = thr.ViewDirectionY()
		ndi.IsDucking = thr.IsDucking() || thr.IsDuckingInProgress() || thr.IsUnDuckingInProgress()
	}

	if gp.WeaponInstance != nil {
		ndi.NadeType = gp.WeaponInstance.Type
	}

	var throwPoint KDVector
	if thr != nil && mp != nil {
		throwPoint.ConvertWithMap(thr.Position(), mp)
	}
	var nowNadePoints NadePoints
	nowNadePoints.Points = append(nowNadePoints.Points, throwPoint, throwPoint)
	ndi.NadePointsList = append(ndi.NadePointsList, nowNadePoints)
}

func (ndi *NadeDrawingInfo) UpdateOnTickDone(ssidx int, gp *common.GrenadeProjectile, mp *ex.Map) {
	lastIndex := len(ndi.NadePointsList) - 1
	nowIndex := ssidx - ndi.StartSnapShotIndex
	if gp == nil || mp == nil {
		return
	}
	if lastIndex == -1 || lastIndex == nowIndex {
		return
	}
	if ndi.NadePointsList[lastIndex].IsDetonated == false {
		var nextPoints NadePoints
		for _, v := range ndi.NadePointsList[lastIndex].Points {
			nextPoints.Points = append(nextPoints.Points, v)
		}
		var nowPoint KDVector
		nowPoint.ConvertWithMap(gp.Position(), mp)
		nextPoints.Points[len(nextPoints.Points)-1] = nowPoint
		ndi.NadePointsList = append(ndi.NadePointsList, nextPoints)
	}
}
func (ndi *NadeDrawingInfo) UpdateOnBounce(ssidx int, gp *common.GrenadeProjectile, mp *ex.Map) {
	lastIndex := len(ndi.NadePointsList) - 1
	if gp == nil || mp == nil {
		return
	}
	if lastIndex == -1 {
		return
	}
	if ndi.NadePointsList[lastIndex].IsDetonated == true {
		return
	}
	nowIndex := ssidx - ndi.StartSnapShotIndex
	lastPoints := ndi.NadePointsList[lastIndex]
	var bouncePoint KDVector
	bouncePoint.ConvertWithMap(gp.Position(), mp)
	lastPoints.Points[len(lastPoints.Points)-1] = bouncePoint
	lastPoints.Points = append(lastPoints.Points, bouncePoint)
	if lastIndex == nowIndex {
		ndi.NadePointsList[lastIndex] = lastPoints
	} else if lastIndex == nowIndex-1 {
		ndi.NadePointsList = append(ndi.NadePointsList, lastPoints)
	}
}
func (ndi *NadeDrawingInfo) DetonateLastElement(ssidx int, dpoint r3.Vector, mp *ex.Map) {
	if ndi == nil || mp == nil {
		return
	}
	lastIndex := len(ndi.NadePointsList) - 1
	if lastIndex == -1 {
		return
	}
	nowIndex := ssidx - ndi.StartSnapShotIndex
	var detonatedPoints NadePoints
	var detonatedPoint KDVector
	detonatedPoint.ConvertWithMap(dpoint, mp)
	detonatedPoints.Points = append(detonatedPoints.Points, detonatedPoint)
	detonatedPoints.IsDetonated = true
	if lastIndex == nowIndex {
		ndi.NadePointsList[lastIndex] = detonatedPoints
	} else if lastIndex == nowIndex-1 {
		ndi.NadePointsList = append(ndi.NadePointsList, detonatedPoints)
	}
}

type NadePoints struct {
	Points      []KDVector
	IsDetonated bool
}
