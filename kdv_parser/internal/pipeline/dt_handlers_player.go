package pipeline

import (
	"fmt"

	demoinfocs "github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs"
	events "github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs/events"
)

func (st *DetectState) onPlayerConnect(psr demoinfocs.Parser, e events.PlayerConnect) {
	tick, frame := getTickAndFrame(psr)
	if st.cfg.Debug {
		name := "Unknown"
		if e.Player != nil {
			name = e.Player.Name
		}
		fmt.Printf("(PlayerConnect t:%d f:%d n:%s)", tick, frame, name)
	}
}

func (st *DetectState) onPlayerDisconnected(psr demoinfocs.Parser, e events.PlayerDisconnected) {
	tick, frame := getTickAndFrame(psr)
	if st.cfg.Debug {
		name := "Unknown"
		if e.Player != nil {
			name = e.Player.Name
		}
		fmt.Printf("(PlayerDisconnecte t:%d f:%d n:%s)", tick, frame, name)
	}
}
