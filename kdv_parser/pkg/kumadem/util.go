package kumadem

import (
	"github.com/golang/geo/r3"
	ex "github.com/markus-wa/demoinfocs-golang/v5/examples"
	demoinfocs "github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs"
	common "github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs/common"
)

type KDVector struct {
	X float32
	Y float32
	Z int
}

func (kdv *KDVector) ConvertWithMap(vec r3.Vector, mp *ex.Map) {
	X, Y := mp.TranslateScale(vec.X, vec.Y)
	kdv.X = float32(X)
	kdv.Y = 1024 - float32(Y) // Flip Y to match Kivy's bottom-left, upward-positive coordinate system (the map Y is top-down).
	kdv.Z = int(vec.Z)
}

type KDPoint struct {
	X float32
	Y float32
}

func (kdp *KDPoint) ConvertWithMap(vec r3.Vector, mp *ex.Map) {
	X, Y := mp.TranslateScale(vec.X, vec.Y)
	kdp.X = float32(X)
	kdp.Y = 1024 - float32(Y)
}

func FindBySteamID(sid uint64, psr demoinfocs.Parser) *common.Player {
	if sid == 0 || psr == nil {
		return nil
	}

	var fallback *common.Player
	for _, p := range psr.GameState().Participants().All() {
		if p == nil || p.SteamID64 != sid {
			continue
		}
		if p.IsConnected {
			return p
		}
		if fallback == nil {
			fallback = p
		}
	}
	return fallback
}

func isValidPlayer(p *common.Player, inserver map[uint64]string) bool {
	if p == nil {
		return false
	}
	if p.SteamID64 == 0 {
		return false
	}
	if !p.IsConnected {
		if _, ok := inserver[p.SteamID64]; !ok {
			return false
		}
	}
	return true
}
