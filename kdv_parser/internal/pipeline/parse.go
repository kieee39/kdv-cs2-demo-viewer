package pipeline

import (
	"errors"
	"os"

	demoinfocs "github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs"
	"github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs/events"

	"kdv_parser/internal/config"
)

// ParseRounds performs the second parsing pass and returns kumadem data.
func ParseRounds(cfg config.Config, meta RoundMeta) (*ParseState, error) {
	f, err := os.Open(cfg.SourcePath)
	if err != nil {
		return nil, err
	}
	psr := demoinfocs.NewParser(f)

	st, err := newParseState(cfg, &meta, psr)
	if err != nil {
		f.Close()
		return nil, err
	}

	registerHandlers(psr, st)

	if err := psr.ParseToEnd(); err != nil && !errors.Is(err, demoinfocs.ErrCancelled) {
		f.Close()
		return nil, err
	}

	f.Close()
	return st, nil
}

// registerHandlers wires all event handlers for the second pass.
func registerHandlers(psr demoinfocs.Parser, st *ParseState) {
	psr.RegisterEventHandler(func(e events.FrameDone) { st.onFrameDone(psr) })
	psr.RegisterEventHandler(func(e events.RoundEnd) { st.onRoundEnd(psr, e) })
	psr.RegisterEventHandler(func(e events.AnnouncementWinPanelMatch) { st.onAnnouncement(psr) })
	psr.RegisterEventHandler(func(e events.TeamSideSwitch) { st.onTeamSideSwitch() })

	psr.RegisterEventHandler(func(e events.WeaponFire) { st.onWeaponFire(psr, e) })
	psr.RegisterEventHandler(func(e events.Kill) { st.onKill(psr, e) })
	psr.RegisterEventHandler(func(e events.PlayerFlashed) { st.onPlayerFlashed(psr, e) })

	psr.RegisterEventHandler(func(e events.BombPlanted) { st.onBombPlanted(psr, e) })
	psr.RegisterEventHandler(func(e events.BombPlantBegin) { st.onBombPlantBegin(psr, e) })
	psr.RegisterEventHandler(func(e events.BombExplode) { st.onBombExplode() })
	psr.RegisterEventHandler(func(e events.BombDefuseStart) { st.onBombDefuseStart(psr, e) })
	psr.RegisterEventHandler(func(e events.BombDefused) { st.onBombDefused() })

	psr.RegisterEventHandler(func(e events.GrenadeProjectileThrow) { st.onNadeThrow(psr, e) })
	psr.RegisterEventHandler(func(e events.GrenadeProjectileBounce) { st.onNadeBounce(psr, e) })
	psr.RegisterEventHandler(func(e events.SmokeStart) { st.onSmokeStart(psr, e) })
	psr.RegisterEventHandler(func(e events.SmokeExpired) { st.onSmokeExpired(psr, e) })
	psr.RegisterEventHandler(func(e events.DecoyStart) { st.onDecoyStart(psr, e) })
	psr.RegisterEventHandler(func(e events.DecoyExpired) { st.onDecoyExpired(psr, e) })
	psr.RegisterEventHandler(func(e events.FireGrenadeStart) { st.onFireStart(psr, e) })
	psr.RegisterEventHandler(func(e events.FireGrenadeExpired) { st.onFireExpired(psr, e) })
	psr.RegisterEventHandler(func(e events.HeExplode) { st.onHeExplode(psr, e) })
	psr.RegisterEventHandler(func(e events.FlashExplode) { st.onFlashExplode(psr, e) })

	psr.RegisterEventHandler(func(e events.PlayerConnect) { st.onPlayerConnect(psr, e) })
	psr.RegisterEventHandler(func(e events.PlayerDisconnected) { st.onPlayerDisconnected(e) })
}

// registerParseHandlers wires event handlers for the one-pass parsing with lazy initialization.
func registerParseHandlers(psr demoinfocs.Parser, st *ParseState, ensure func()) {
	register := func(handler interface{}) { psr.RegisterEventHandler(handler) }
	withInit := func(f func()) {
		ensure()
		if st.initialized {
			f()
		}
	}

	register(func(e events.FrameDone) { withInit(func() { st.onFrameDone(psr) }) })
	register(func(e events.RoundEnd) { withInit(func() { st.onRoundEnd(psr, e) }) })
	register(func(e events.AnnouncementWinPanelMatch) { withInit(func() { st.onAnnouncement(psr) }) })
	register(func(e events.TeamSideSwitch) { withInit(func() { st.onTeamSideSwitch() }) })
	register(func(e events.WeaponFire) { withInit(func() { st.onWeaponFire(psr, e) }) })
	register(func(e events.Kill) { withInit(func() { st.onKill(psr, e) }) })
	register(func(e events.PlayerFlashed) { withInit(func() { st.onPlayerFlashed(psr, e) }) })
	register(func(e events.BombPlanted) { withInit(func() { st.onBombPlanted(psr, e) }) })
	register(func(e events.BombPlantBegin) { withInit(func() { st.onBombPlantBegin(psr, e) }) })
	register(func(e events.BombExplode) { withInit(func() { st.onBombExplode() }) })
	register(func(e events.BombDefuseStart) { withInit(func() { st.onBombDefuseStart(psr, e) }) })
	register(func(e events.BombDefused) { withInit(func() { st.onBombDefused() }) })
	register(func(e events.GrenadeProjectileThrow) { withInit(func() { st.onNadeThrow(psr, e) }) })
	register(func(e events.GrenadeProjectileBounce) { withInit(func() { st.onNadeBounce(psr, e) }) })
	register(func(e events.SmokeStart) { withInit(func() { st.onSmokeStart(psr, e) }) })
	register(func(e events.SmokeExpired) { withInit(func() { st.onSmokeExpired(psr, e) }) })
	register(func(e events.DecoyStart) { withInit(func() { st.onDecoyStart(psr, e) }) })
	register(func(e events.DecoyExpired) { withInit(func() { st.onDecoyExpired(psr, e) }) })
	register(func(e events.FireGrenadeStart) { withInit(func() { st.onFireStart(psr, e) }) })
	register(func(e events.FireGrenadeExpired) { withInit(func() { st.onFireExpired(psr, e) }) })
	register(func(e events.HeExplode) { withInit(func() { st.onHeExplode(psr, e) }) })
	register(func(e events.FlashExplode) { withInit(func() { st.onFlashExplode(psr, e) }) })
	register(func(e events.PlayerConnect) { withInit(func() { st.onPlayerConnect(psr, e) }) })
	register(func(e events.PlayerDisconnected) { withInit(func() { st.onPlayerDisconnected(e) }) })
}
