package pipeline

import (
	"fmt"

	"slices"

	demoinfocs "github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs"
	common "github.com/markus-wa/demoinfocs-golang/v5/pkg/demoinfocs/common"

	"kdv_parser/pkg/kumadem"
)

func (st *DetectState) setPlayerSteamID(psr demoinfocs.Parser) {
	playing := psr.GameState().Participants().Playing()
	for _, player := range playing {
		if player == nil {
			continue
		}
		if !slices.Contains(st.meta.TempPlayerIDs, player.SteamID64) && player.SteamID64 != 0 {
			st.meta.TempPlayerIDs = append(st.meta.TempPlayerIDs, player.SteamID64)
		}
	}
	slices.Sort(st.meta.TempPlayerIDs)
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
	st.meta.TempPlayerIDs, st.meta.TempTeam0, st.meta.TempTeam1 = []uint64{}, []uint64{}, []uint64{}
	var player0Side common.Team
	steamIDMap := map[uint64]*common.Player{}

	for _, p := range st.meta.TempAll {
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
