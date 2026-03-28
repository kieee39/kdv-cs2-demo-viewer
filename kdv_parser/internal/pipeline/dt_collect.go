package pipeline

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
	"strings"

	"slices"

	demoinfocs "github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs"
	common "github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs/common"

	"kdv_parser/pkg/kumadem"
)

func (st *DetectState) setPlayerSteamID(psr demoinfocs.Parser) {
	if st.ignoredSteamID == nil {
		st.ignoredSteamID = map[uint64]struct{}{}
	}
	playing := psr.GameState().Participants().Playing()
	for _, player := range playing {
		if player == nil {
			continue
		}
		if _, ignored := st.ignoredSteamID[player.SteamID64]; ignored {
			continue
		}
		if !slices.Contains(st.meta.TempPlayerIDs, player.SteamID64) && player.SteamID64 != 0 {
			st.meta.TempPlayerIDs = append(st.meta.TempPlayerIDs, player.SteamID64)
		}
	}
	slices.Sort(st.meta.TempPlayerIDs)
	for len(st.meta.TempPlayerIDs) > 10 {
		playerNames := map[uint64]string{}
		for _, player := range psr.GameState().Participants().Playing() {
			playerNames[player.SteamID64] = player.Name
		}

		fmt.Printf("[detect] collected %d player SteamIDs; choose one to remove\n", len(st.meta.TempPlayerIDs))
		for i, id := range st.meta.TempPlayerIDs {
			name := playerNames[id]
			if name == "" {
				name = "Unknown"
			}
			fmt.Printf("  [%d] %d (%s)\n", i, id, name)
		}
		fmt.Print("[detect] enter index to remove: ")

		scanner := bufio.NewScanner(os.Stdin)
		if !scanner.Scan() {
			fmt.Print("[detect] failed to read input while trimming player SteamIDs\n")
			return
		}

		idx, err := strconv.Atoi(strings.TrimSpace(scanner.Text()))
		if err != nil || idx < 0 || idx >= len(st.meta.TempPlayerIDs) {
			fmt.Print("[detect] invalid index\n")
			continue
		}

			name := playerNames[st.meta.TempPlayerIDs[idx]]
			if name == "" {
				name = "Unknown"
			}
			fmt.Printf("[detect] removing SteamID %d (%s)\n", st.meta.TempPlayerIDs[idx], name)
			st.ignoredSteamID[st.meta.TempPlayerIDs[idx]] = struct{}{}
			st.meta.TempPlayerIDs = append(st.meta.TempPlayerIDs[:idx], st.meta.TempPlayerIDs[idx+1:]...)
	}
}

func (st *DetectState) setTeamID(psr demoinfocs.Parser) {
	if len(st.meta.TempPlayerIDs) != 10 || len(st.meta.TempTeam0) == 5 || len(st.meta.TempTeam1) == 5 {
		return
	}
	player0 := kumadem.FindBySteamID(st.meta.TempPlayerIDs[0], psr)
	if player0 == nil {
		fmt.Print("[detect] team resolution skipped: primary player not found\n")
		return
	}
	if player0.TeamState == nil || player0.TeamState.Opponent == nil {
		fmt.Print("[detect] team resolution skipped: team state not ready\n")
		return
	}
	for i, p := range player0.TeamState.Members() {
		if p == nil {
			continue
		}
		if i >= 6 {
			continue
		}
		if !slices.Contains(st.meta.TempTeam0, p.SteamID64) {
			st.meta.TempTeam0 = append(st.meta.TempTeam0, p.SteamID64)
		}
	}
	for i, p := range player0.TeamState.Opponent.Members() {
		if p == nil {
			continue
		}
		if i >= 6 {
			continue
		}
		if !slices.Contains(st.meta.TempTeam1, p.SteamID64) {
			st.meta.TempTeam1 = append(st.meta.TempTeam1, p.SteamID64)
		}
	}
	slices.Sort(st.meta.TempTeam0)
	slices.Sort(st.meta.TempTeam1)
}

func (st *DetectState) collectPlayers() error {
	if len(st.meta.TempAll) < 10 {
		return fmt.Errorf("detect: collectPlayers failed (participants=%d)", len(st.meta.TempAll))
	}
	if st.ignoredSteamID == nil {
		st.ignoredSteamID = map[uint64]struct{}{}
	}
	st.meta.TempPlayerIDs, st.meta.TempTeam0, st.meta.TempTeam1 = []uint64{}, []uint64{}, []uint64{}
	var player0Side common.Team
	steamIDMap := map[uint64]*common.Player{}

	for _, p := range st.meta.TempAll {
		if p != nil {
			if _, ignored := st.ignoredSteamID[p.SteamID64]; ignored {
				continue
			}
		}
		if p != nil && p.SteamID64 != 0 && !p.IsBot && !slices.Contains(st.meta.TempPlayerIDs, p.SteamID64) {
			st.meta.TempPlayerIDs = append(st.meta.TempPlayerIDs, p.SteamID64)
			steamIDMap[p.SteamID64] = p
		}
	}
	if len(st.meta.TempPlayerIDs) != 10 {
		return fmt.Errorf("detect: collectPlayers failed (steamIDs=%d/10)", len(st.meta.TempPlayerIDs))
	}
	slices.Sort(st.meta.TempPlayerIDs)
	for i, pid := range st.meta.TempPlayerIDs {
		player := steamIDMap[pid]
		if player == nil {
			return fmt.Errorf("detect: collectPlayers failed (steamID=%d missing player)", pid)
		}
		if i == 0 {
			player0Side = player.Team
		}
		if player.Team == player0Side {
			st.meta.TempTeam0 = append(st.meta.TempTeam0, pid)
		} else {
			st.meta.TempTeam1 = append(st.meta.TempTeam1, pid)
		}
	}
	if len(st.meta.TempTeam0) != 5 || len(st.meta.TempTeam1) != 5 {
		return fmt.Errorf("detect: collectPlayers failed (teams=%d/%d)", len(st.meta.TempTeam0), len(st.meta.TempTeam1))
	}
	return nil
}
