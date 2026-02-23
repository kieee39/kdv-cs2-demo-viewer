package kumadem

import (
	ex "github.com/markus-wa/demoinfocs-golang/v5/examples"
	common "github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs/common"
)

type PlayerDrawingInfo struct {
	Positions         KDVector
	LastAlivePosition KDVector
	ViewDirectionX    float32
	FlashDuration     float32

	Hp              int
	Alive           bool
	Armor           int
	HasHelmet       bool
	HasBomb         bool
	HasDefuseKit    bool
	ActiveEquipment common.EquipmentType
	PrimaryEq       common.EquipmentType
	SecondaryEq     common.EquipmentType
	He              byte
	Fb              byte
	Smk             byte
	Mol             byte
	Inc             byte
	Dec             byte

	Firing bool
}

func (pdi *PlayerDrawingInfo) resetEquipment() {
	pdi.PrimaryEq, pdi.SecondaryEq = 0, 0
	pdi.He, pdi.Fb, pdi.Smk, pdi.Mol, pdi.Inc, pdi.Dec = 0, 0, 0, 0, 0, 0
}

func (pdi *PlayerDrawingInfo) update(player *common.Player, mp *ex.Map, inserver map[uint64]string) {
	// Reset equipment info
	pdi.resetEquipment()

	// Validate player
	if !isValidPlayer(player, inserver) {
		return
	}

	// If player is dead, only update last alive position and set HP to 0
	if !player.IsAlive() && player.Health() <= 0 {
		pdi.Hp = 0
		pdi.LastAlivePosition.ConvertWithMap(player.Position(), mp)
		return
	}

	// Update player basic infos such as position, HP, armor, etc.
	pdi.Positions.ConvertWithMap(player.Position(), mp)
	pdi.ViewDirectionX = player.ViewDirectionX()
	pdi.FlashDuration = float32(player.FlashDurationTimeRemaining().Seconds())
	pdi.Hp = player.Health()
	pdi.Alive = player.IsAlive()
	pdi.Armor = player.Armor()
	pdi.HasHelmet = player.HasHelmet()
	pdi.HasDefuseKit = player.HasDefuseKit()
	if player.ActiveWeapon() != nil {
		pdi.ActiveEquipment = player.ActiveWeapon().Type
	}

	// Update player equipment info
	for _, eq := range player.Weapons() {
		if 0 < eq.Type && eq.Type < 100 {
			pdi.SecondaryEq = eq.Type
		} else if 100 < eq.Type && eq.Type < 400 {
			pdi.PrimaryEq = eq.Type
		} else {
			switch eq.Type {
			case common.EqHE:
				pdi.He = byte(eq.AmmoInMagazine() + eq.AmmoReserve())
			case common.EqFlash:
				pdi.Fb = byte(eq.AmmoInMagazine() + eq.AmmoReserve())
			case common.EqSmoke:
				pdi.Smk = byte(eq.AmmoInMagazine() + eq.AmmoReserve())
			case common.EqMolotov:
				pdi.Mol = byte(eq.AmmoInMagazine() + eq.AmmoReserve())
			case common.EqIncendiary:
				pdi.Inc = byte(eq.AmmoInMagazine() + eq.AmmoReserve())
			case common.EqDecoy:
				pdi.Dec = byte(eq.AmmoInMagazine() + eq.AmmoReserve())
			}
		}
	}

}
