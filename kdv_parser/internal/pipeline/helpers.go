package pipeline

import (
	"crypto/md5"
	"encoding/hex"
	"io"
	"os"

	demoinfocs "github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs"
)

func getTickAndFrame(psr demoinfocs.Parser) (int, int) {
	tick := psr.GameState().IngameTick()
	frame := psr.CurrentFrame()
	return tick, frame
}

func md5sum(filePath string) (result string, err error) {
	file, err := os.Open(filePath)
	if err != nil {
		return
	}
	defer file.Close()

	hash := md5.New()
	_, err = io.Copy(hash, file)
	if err != nil {
		return
	}

	result = hex.EncodeToString(hash.Sum(nil))
	return
}
