import copy
import json
import os
import sys

default_json_config = {
  "ui_setting": {
    "weapon_icon": False,
    "player_number": True,
    "hpbar": False,
    "player_name": True,
    "sightline": False,
    "utility_icon": False
  },
  "kdv_scale_map": {
    "": 1.0,
    "de_ancient": 1.1,
    "de_cache": 1.2,
    "de_dust2": 0.95,
    "de_inferno": 1.0,
    "de_mirage": 1.25,
    "de_nuke": 1.4,
    "de_overpass": 0.95,
    "de_train": 1.1,
    "de_vertigo": 1.05,
    "de_anubis": 1.1
  },
  "kdv_gap_map": {
    "default": [0, 0],
    "de_nuke": [-40, 0],
    "de_vertigo": [80, 0]
  },
  "map_bounds": {
    "nuke_bdr": -505,
    "nuke_y_bdr": 740,
    "vertigo_z_bdr": 11680,
    "vertigo_a_x_bdr": 510,
    "vertigo_b_x_bdr": 256,
    "vertigo_b_y_bdr": 530
  }
}

def _config_base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def config_path():
    return os.path.join(_config_base_dir(), "kdv_config.json")


def load_config(path=None):
    base = copy.deepcopy(default_json_config)
    path = path or config_path()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return base
    except (OSError, json.JSONDecodeError):
        return base
    if not isinstance(data, dict):
        return base
    return _deep_merge(base, data)


def _deep_merge(base, override):
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(base.get(key), dict):
            base[key] = _deep_merge(base[key], value)
        else:
            base[key] = value
    return base
