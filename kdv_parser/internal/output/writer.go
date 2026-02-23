package output

import (
	"archive/zip"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"strconv"

	"kdv_parser/pkg/kumadem"

	"github.com/vmihailenco/msgpack"
)

// WriteKumademFile writes kumadem data into a .kdz (zip+msgpack) file.
func WriteKumademFile(outputPath string, data *kumadem.Kumadem) error {
	if data == nil {
		return errors.New("kumadem data is nil")
	}
	if outputPath == "" {
		return errors.New("output path is empty")
	}

	if err := os.MkdirAll(filepath.Dir(outputPath), 0o755); err != nil {
		return fmt.Errorf("make output dir: %w", err)
	}

	dest, err := os.Create(outputPath)
	if err != nil {
		return fmt.Errorf("create output file: %w", err)
	}
	defer dest.Close()

	zipWriter := zip.NewWriter(dest)
	defer func() {
		_ = zipWriter.Close()
	}()

	// helper to write any struct as msgpack into zip entry
	writeEntry := func(name string, v any) error {
		entry, err := zipWriter.Create(name)
		if err != nil {
			return fmt.Errorf("create zip entry %q: %w", name, err)
		}
		enc := msgpack.NewEncoder(entry)
		if err := enc.Encode(v); err != nil {
			return fmt.Errorf("encode %q: %w", name, err)
		}
		return nil
	}

	if err := writeEntry("kdm_header", data.Header); err != nil {
		return err
	}
	if err := writeEntry("kdm_matchstats", data.MatchStats); err != nil {
		return err
	}
	for i, v := range data.RoundSnapshots {
		if err := writeEntry("kdm_round_"+strconv.Itoa(i), v); err != nil {
			return err
		}
	}
	if err := WriteRoundTrajectoryImages(zipWriter, data.RoundSnapshots); err != nil {
		return err
	}
	return nil
}
