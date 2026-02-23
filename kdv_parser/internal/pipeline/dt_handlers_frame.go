package pipeline

import demoinfocs "github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs"

func (st *DetectState) onFrameDone(psr demoinfocs.Parser) {
	st.meta.FrameLength++
}
