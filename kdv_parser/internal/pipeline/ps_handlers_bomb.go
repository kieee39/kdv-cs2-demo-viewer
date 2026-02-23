package pipeline

import (
	"fmt"

	demoinfocs "github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs"
	"github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs/events"

	"kdv_parser/pkg/kumadem"
)

func (st *ParseState) onBombPlanted(psr demoinfocs.Parser, e events.BombPlanted) {
	if st.cfg.Debug {
		fmt.Printf("<DEBUG>cf:%d BombPlanted\n", psr.CurrentFrame())
	}
	if !st.isParsing {
		return
	}
	st.currentRI.Planted(rune(e.Site))

	tick, _ := getTickAndFrame(psr)
	st.currentRS.BombPlantedTick = tick
	st.currentRS.BombPlantedSSIndex = st.nowSSIndex
	st.currentBS.IsPlanted = true

	el := new(kumadem.EventLog)
	el.LogPlanted(tick, st.nowSSIndex, e)
	st.currentRS.EventLogs = append(st.currentRS.EventLogs, *el)
}

func (st *ParseState) onBombPlantBegin(psr demoinfocs.Parser, e events.BombPlantBegin) {
	if st.cfg.Debug {
		fmt.Printf("<DEBUG>cf:%d BombPlantBegin\n", psr.CurrentFrame())
	}
	if !st.isParsing {
		return
	}
	tick, _ := getTickAndFrame(psr)
	el := new(kumadem.EventLog)
	el.LogPlanting(tick, st.nowSSIndex, e)
	st.currentRS.EventLogs = append(st.currentRS.EventLogs, *el)
}

func (st *ParseState) onBombExplode() {
	if !st.isParsing {
		return
	}
	st.currentRS.BombDetonatedSSIndex = st.nowSSIndex
}

func (st *ParseState) onBombDefuseStart(psr demoinfocs.Parser, e events.BombDefuseStart) {
	if st.cfg.Debug {
		fmt.Printf("<DEBUG>cf:%d BombDefuseStart\n", psr.CurrentFrame())
	}
	if !st.isParsing {
		return
	}
	tick, _ := getTickAndFrame(psr)
	el := new(kumadem.EventLog)
	el.LogDefusing(tick, st.nowSSIndex, e)
	st.currentRS.EventLogs = append(st.currentRS.EventLogs, *el)
}

func (st *ParseState) onBombDefused() {
	if !st.isParsing {
		return
	}
	st.currentRS.BombDefusedSSIndex = st.nowSSIndex
}
