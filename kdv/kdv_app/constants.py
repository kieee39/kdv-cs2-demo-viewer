from kivy.utils import get_hex_from_color
from .config_loader import default_json_config, load_config

KDV_VER = "1.0.1"

PLY_SIZE = 77
TIMER_SIZE = 100
GRD_SIZE = 32
BOMB_SIZE = 57

SMOKE_SECOND = 18
MOLOTOV_SECOND = 7

BAR_HINT_WIDTH = 3

UKNOWN_COLOR = (0.5, 0.5, 0.5)
T_COLOR = (0.769, 0.671, 0.341)
CT_COLOR = (0.357, 0.545, 0.694)
T_COLOR_H = get_hex_from_color((0.769, 0.671, 0.341,1))
CT_COLOR_H = get_hex_from_color((0.357, 0.545, 0.694,1))

SIDE_COLOR = {
    0: UKNOWN_COLOR,
    1: UKNOWN_COLOR,
    2: T_COLOR,
    3: CT_COLOR
}

C4_IMG_PATH = "./img/c4.png"
C4P_IMG_PATH = "./img/c4_planted.png"
C4DT_IMG_PATH = "./img/c4_detonated.png"
C4DF_IMG_PATH = "./img/c4_defused.png"

T_LA_IMG_PATH = "./img/tlapos.png"
CT_LA_IMG_PATH = "./img/ctlapos.png"

TEAM_MAP = {
    0: "N/A",
    2: "T",
    3: "CT"
}
WIN_R_MAP = {
    0: "N/A",
    1: "Bomb",
    7: "Def",
    8: "Elim",# CT
    9: "Elim",# T
    10: "Draw",
    12: "Time",
    17: "TSur",
    18: "CTSur"
}

UTIL_MAP = {
    501: 'DC',
    502: 'ML',
    503: 'IC',
    504: 'FB',
    505: 'SG',
    506: 'HE' 
}

UTIL_FULL_MAP = {
    501: 'Decoy',
    502: 'Molotov',
    503: 'Incendiary',
    504: 'FB',
    505: 'Smoke',
    506: 'HE' 
}

# in-game overlay scale value.
MAP_SCALE  = 0

# UI scale value for this application.
KDV_SCALE_MAP = {}

# Map-specific view offsets (xgap, ygap)
KDV_GAP_MAP = {}
KDV_GAP_DEFAULT = (0, 0)

# UI defaults
CHECKBOX_DEFAULTS = {
    "wico": False,
    "num": False,
    "hp": False,
    "name": False,
    "sl": False,
    "pu": False,
}

NUKE_BDR = 0
NUKE_Y_BDR = 0
VERTIGO_Z_BDR = 0  # in-game default = 11764
VERTIGO_A_X_BDR = 0  # This value is not in-game coordination. -1140
VERTIGO_B_X_BDR = 0
VERTIGO_B_Y_BDR = 0


def apply_config(config):
    if not isinstance(config, dict):
        config = {}

    def _cfg(section, key):
        try:
            return config[section][key]
        except Exception:
            return default_json_config[section][key]

    CHECKBOX_DEFAULTS["wico"] = _cfg("ui_setting", "weapon_icon")
    CHECKBOX_DEFAULTS["num"] = _cfg("ui_setting", "player_number")
    CHECKBOX_DEFAULTS["hp"] = _cfg("ui_setting", "hpbar")
    CHECKBOX_DEFAULTS["name"] = _cfg("ui_setting", "player_name")
    CHECKBOX_DEFAULTS["sl"] = _cfg("ui_setting", "sightline")
    CHECKBOX_DEFAULTS["pu"] = _cfg("ui_setting", "utility_icon")

    scale_map = dict(default_json_config["kdv_scale_map"])
    try:
        scale_map.update(config["kdv_scale_map"])
    except Exception:
        pass
    KDV_SCALE_MAP.clear()
    KDV_SCALE_MAP.update(scale_map)

    gap_map = dict(default_json_config["kdv_gap_map"])
    try:
        gap_map.update(config["kdv_gap_map"])
    except Exception:
        pass

    global KDV_GAP_DEFAULT
    try:
        KDV_GAP_DEFAULT = tuple(gap_map["default"])
    except Exception:
        KDV_GAP_DEFAULT = tuple(default_json_config["kdv_gap_map"]["default"])

    KDV_GAP_MAP.clear()
    for key, value in gap_map.items():
        if key == "default":
            continue
        try:
            KDV_GAP_MAP[key] = (value[0], value[1])
        except Exception:
            fallback = default_json_config["kdv_gap_map"].get(key)
            if fallback is not None:
                KDV_GAP_MAP[key] = (fallback[0], fallback[1])

    global NUKE_BDR, NUKE_Y_BDR, VERTIGO_Z_BDR, VERTIGO_A_X_BDR, VERTIGO_B_X_BDR, VERTIGO_B_Y_BDR
    NUKE_BDR = _cfg("map_bounds", "nuke_bdr")
    NUKE_Y_BDR = _cfg("map_bounds", "nuke_y_bdr")
    VERTIGO_Z_BDR = _cfg("map_bounds", "vertigo_z_bdr")
    VERTIGO_A_X_BDR = _cfg("map_bounds", "vertigo_a_x_bdr")
    VERTIGO_B_X_BDR = _cfg("map_bounds", "vertigo_b_x_bdr")
    VERTIGO_B_Y_BDR = _cfg("map_bounds", "vertigo_b_y_bdr")
def is_on_targetlayer(player_z, map_layer, map_name):
    if map_layer == 0:
        if map_name =='de_nuke' and player_z <= NUKE_BDR:
            return False
        elif map_name =='de_vertigo' and player_z <= VERTIGO_Z_BDR:
            return False
        else:
            return True
    elif map_layer == -1:
        if map_name =='de_nuke' and player_z <= NUKE_BDR:
            return True
        elif map_name =='de_vertigo' and player_z <= VERTIGO_Z_BDR:
            return True
        else:
            return False
