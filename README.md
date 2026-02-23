# KDV (KumaDemoViewer)

[English](README.md) | [日本語](README.ja.md)

Kivy-based viewer for Counter-Strike 2 demo files. A bundled Go parser converts
`.dem` into `.kdz`, and the app visualizes rounds, players, utility, and events.

![KDV main screenshot](doc/main.png)

## Support
- Ko-fi: https://ko-fi.com/kieee

## Features
### Input and conversion
- Drag and drop `.dem` or `.kdz` files into the app window.
- Parse CS2 `.dem` files into `.kdz` with the bundled Go parser.
- Save parsed `.kdz` in the same directory as the source `.dem`.
- If a same-name `.kdz` already exists in the same folder and its version matches the app version, parsing is skipped and the existing `.kdz` is loaded.
- Re-parse automatically when an existing `.kdz` version is different from the app version.
- Use `.kdz` format as zip-compressed msgpack data (`kdm_header`, `kdm_matchstats`, `kdm_round_*`).
- Configure startup defaults via `kdv/kdv_config.json` (UI toggles and map calibration values).

### Round and timeline navigation
- Full round list with per-round score, planted site, economy, equipment counts, and win reason.
- Quick round buttons for direct round jumps.
- Seekbar timeline with 1:30 / 1:00 / 0:30 markers.
- Seekbar kill markers split by side (T / CT).
- Seekbar bomb plant marker with planted site.
- Seekbar utility throw markers by type.
- Playback controls: play/stop, seek, previous/next round.
- Playback speeds: `x1/2`, `x1`, `x2`, `x4`.
- Keyboard time-step jumps (3-second step).
- Right-click seekbar bookmark + jump back to bookmark (`B` key).
- Click the timer/tick display area to copy the current tick command (`demo_gototick <tick>`) to the clipboard.

### Map and tactical visualization
- Player positions, facing direction, active weapon indicator, firing line, and flash state.
- Last-alive position markers for dead players.
- Bomb state rendering: carried, planted, detonated, defused.
- Grenade trajectory rendering and effect areas (HE/Flash/Smoke/Molotov/Incendiary/Decoy).
- Smoke lifetime timer ring rendering.
- Optional round trajectory overlay on radar map.
- Layer switching for multi-floor maps (`de_nuke`, `de_vertigo`): Upper/Lower.
- Player overlay toggles: weapon icon, player number, HP bar, player name, sight line, utility icons.

### Utility and event tools
- Grenade tab listing throw details: time, tick, thrower, type, ducking state.
- Click a grenade entry to jump to its snapshot.
- Copy grenade throw position/angle command to clipboard (`setpos ...;setang ...`).
- Event log panel for kills, utility throws, plant, and defuse timeline events.

### Annotation and interaction
- Draw on the map using right mouse drag.
- Switch drawing color (`White`, `Orange`, `Blue`).
- Clear drawings with button or keyboard shortcut (`C`).
- Toggle fullscreen (`F11`).

### Keyboard shortcuts
- `Space`: Play/Stop.
- `Left` / `A`: Step backward (3 seconds).
- `Right` / `D`: Step forward (3 seconds).
- `Up` / `W`: Previous round.
- `Down` / `S`: Next round.
- `1` / `2` / `4` / `3` (`H`/`5`): Speed presets.
- `V`: Toggle sight line.
- `G`: Toggle utility icons.
- `B`: Jump to bookmark.
- `T`: Toggle trajectory overlay.
- `Tab`: Cycle tabs.
- `Left Ctrl`: Toggle map layer.

## Requirements
- Python 3.10 (see `kdv/.python-version`).
- Python dependencies from `kdv/requirements.txt`.
- Go (required to build `kdv_parser.exe`).

## Setup
Run:

```bat
.\build.bat
```

This script:
- Creates/uses `kdv/.venv`.
- Installs Python dependencies.
- Builds `kdv/kdv_parser.exe`.
- Builds `kdv/kdv.exe` via PyInstaller.

## Run
After setup, launch:

```bat
kdv\kdv.exe
```

## Configuration (`kdv/kdv_config.json`)
- You can edit `kdv/kdv_config.json` to change UI initial values and map calibration.
- Changes are applied when the app starts (restart KDV after editing).
- `ui_setting`: default states of the Team tab overlay checkboxes.
- `ui_setting.weapon_icon`: show/hide active weapon text by default.
- `ui_setting.player_number`: show/hide player number labels by default.
- `ui_setting.hpbar`: show/hide HP bars by default.
- `ui_setting.player_name`: show/hide player name labels by default.
- `ui_setting.sightline`: show/hide sight lines by default.
- `ui_setting.utility_icon`: show/hide carried utility indicators by default.
- `kdv_scale_map`: per-map initial KDV map scale (UI zoom base).
- `kdv_gap_map`: per-map `(x, y)` display offset for map alignment.
- `kdv_gap_map.default`: fallback offset used when a map entry is missing.
- `map_bounds`: boundary values used for multi-floor map layer logic/tuning.
- `map_bounds.nuke_bdr`: Z boundary used to split upper/lower layer on Nuke.
- `map_bounds.vertigo_z_bdr`: Z boundary used to split upper/lower layer on Vertigo.
- `map_bounds.nuke_y_bdr`: reserved tuning value for Nuke boundary adjustments.
- `map_bounds.vertigo_a_x_bdr`: reserved tuning value for Vertigo boundary adjustments.
- `map_bounds.vertigo_b_x_bdr`: reserved tuning value for Vertigo boundary adjustments.
- `map_bounds.vertigo_b_y_bdr`: reserved tuning value for Vertigo boundary adjustments.

## Notes
- `kdv/kdv_parser.exe` must exist to parse `.dem` files.
- To build parser manually:

```bat
cd kdv_parser\cmd\parser
go build -o ..\..\..\kdv\kdv_parser.exe main.go
```

- Keeping Go up to date can reduce false positives from antivirus software.
- Third-party font license: `kdv/img/IPA_Font_License_Agreement_v1.0.txt`.
- Third-party notices: `THIRD_PARTY_NOTICES.txt` and `third_party_licenses/`.
- Project license: MIT (see `LICENSE`).
- Radar images are not bundled in this repository. Add them manually under `kdv/maps`.

## Radar images
- Radar images are not included in this repository.
- Add map images manually to `kdv/maps`.
- To extract radar images from CS2 game files, follow:
  https://cs-demo-manager.com/docs/guides/maps#radars-optional
- Required format: 1024x1024 PNG.
- Naming: `de_<mapname>.png`
- Naming (lower floor maps): `de_<mapname>_lower.png` (for example `nuke` and `vertigo`).
