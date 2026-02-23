package output

import (
	"archive/zip"
	"fmt"
	"image"
	"image/color"
	"image/png"
	"math"
	"strconv"

	"kdv_parser/pkg/kumadem"

	"github.com/fogleman/gg"
)

const (
	trajectoryImageWidth  = 1024
	trajectoryImageHeight = 1024
	trajectoryLineWidth   = 1.5

	trajectoryThumWidth  = 256
	trajectoryThumHeight = 215
	trajectoryThumLineW  = 7

	kdCoordSize = 1024.0
)

var trajectoryColors = [10]color.RGBA{
	{R: 230, G: 57, B: 70, A: 255},  // 0: red
	{R: 245, G: 124, B: 25, A: 255}, // 1: orange
	{R: 252, G: 186, B: 3, A: 255},  // 2: amber
	{R: 211, G: 227, B: 26, A: 255}, // 3: yellow-green
	{R: 94, G: 205, B: 60, A: 255},  // 4: green
	{R: 16, G: 184, B: 155, A: 255}, // 5: teal
	{R: 0, G: 164, B: 225, A: 255},  // 6: cyan / sky blue
	{R: 49, G: 110, B: 245, A: 255}, // 7: blue
	{R: 132, G: 74, B: 255, A: 255}, // 8: violet
	{R: 227, G: 73, B: 182, A: 255}, // 9: magenta
}

// WriteRoundTrajectoryImages writes one aggregated trajectory image per round.
func WriteRoundTrajectoryImages(zipWriter *zip.Writer, rounds []kumadem.RoundSnapshot) error {
	for i, round := range rounds {
		img := renderRoundTrajectory(round)
		name := "kdm_traj_round_" + strconv.Itoa(i) + ".png"
		if err := writePNGEntry(zipWriter, name, img); err != nil {
			return err
		}

		thumImg := renderRoundTrajectoryThum(round)
		thumName := "kdm_traj_round_thum_" + strconv.Itoa(i) + ".png"
		if err := writePNGEntry(zipWriter, thumName, thumImg); err != nil {
			return err
		}
	}
	return nil
}

func renderRoundTrajectory(rs kumadem.RoundSnapshot) image.Image {
	return renderRoundTrajectoryStyled(rs, trajectoryImageWidth, trajectoryImageHeight, trajectoryLineWidth)
}

func renderRoundTrajectoryThum(rs kumadem.RoundSnapshot) image.Image {
	return renderRoundTrajectoryStyled(rs, trajectoryThumWidth, trajectoryThumHeight, trajectoryThumLineW)
}

func renderRoundTrajectoryStyled(rs kumadem.RoundSnapshot, width, height int, lineWidth float64) image.Image {
	dc := gg.NewContext(width, height)
	// Keep the background transparent; gg context starts with zero alpha.
	dc.SetLineWidth(lineWidth)

	for slot := 0; slot < len(trajectoryColors); slot++ {
		trail := collectPlayerTrail(rs, slot, width, height)
		drawTrail(dc, trail, trajectoryColors[slot])
	}

	return dc.Image()
}

func collectPlayerTrail(rs kumadem.RoundSnapshot, slot, width, height int) []image.Point {
	trail := make([]image.Point, 0, len(rs.PlayerDrawingSnapShots))
	for _, snap := range rs.PlayerDrawingSnapShots {
		info := snap.PlayerDrawingInfo[slot]
		if !info.Alive || info.Hp <= 0 {
			continue
		}
		p := toTrajectoryPixel(info.Positions, width, height)
		trail = append(trail, p)
	}
	return trail
}

func toTrajectoryPixel(pos kumadem.KDVector, width, height int) image.Point {
	x := clamp(int(math.Round(float64(pos.X)*float64(width)/kdCoordSize)), 0, width-1)
	scaledY := clamp(int(math.Round(float64(pos.Y)*float64(height)/kdCoordSize)), 0, height-1)
	y := height - 1 - scaledY
	return image.Point{X: x, Y: y}
}

func clamp(v, minV, maxV int) int {
	if v < minV {
		return minV
	}
	if v > maxV {
		return maxV
	}
	return v
}

func drawTrail(dc *gg.Context, pts []image.Point, c color.RGBA) {
	switch len(pts) {
	case 0:
		return
	case 1:
		dc.SetColor(c)
		dc.DrawPoint(float64(pts[0].X), float64(pts[0].Y), 0.75)
		dc.Fill()
		return
	}

	dc.SetColor(c)
	dc.NewSubPath()
	dc.MoveTo(float64(pts[0].X), float64(pts[0].Y))
	for i := 1; i < len(pts); i++ {
		dc.LineTo(float64(pts[i].X), float64(pts[i].Y))
	}
	dc.Stroke()
}

func writePNGEntry(zipWriter *zip.Writer, name string, img image.Image) error {
	entry, err := zipWriter.Create(name)
	if err != nil {
		return fmt.Errorf("create zip entry %q: %w", name, err)
	}
	if err := png.Encode(entry, img); err != nil {
		return fmt.Errorf("encode png %q: %w", name, err)
	}
	return nil
}
