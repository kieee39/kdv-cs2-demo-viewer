# -*- coding: utf-8 -*-

NADE_SYMBOL_MAP = {
    501: "D",
    502: "M",
    503: "I",
    504: "F",
    505: "S",
    506: "H",
}


def build_seekbar_hints(round_snapshot, ss_index_max, snapshot_rate):
    if ss_index_max <= 0:
        return [], [], [], 0, "", []

    time_list = []
    for t in [snapshot_rate * 25, snapshot_rate * 55, snapshot_rate * 85]:
        time_list.append(t / ss_index_max)

    tk_list = []
    ctk_list = []
    plant_site = ""

    event_logs = round_snapshot.get("EventLogs") or []
    for el in event_logs:
        if el["Type"] == "Kill" and el["Side"] == "T":
            tk_list.append(el["SsIndex"] / ss_index_max)
        elif el["Type"] == "Kill" and el["Side"] == "CT":
            ctk_list.append(el["SsIndex"] / ss_index_max)
        elif el["Type"] == "PlantedA" or el["Type"] == "PlantedB":
            plant_site = el["Type"][-1]

    tick_nade_map = []
    nades = round_snapshot.get("NadesDrawingInfoMap") or []
    for ndi in nades:
        tick_nade_map.append((int(ndi["StartTick"]), ndi))
    tick_nade_map.sort(key=lambda x: x[0])

    n_list = []
    for _, nade_info in tick_nade_map:
        nade = NADE_SYMBOL_MAP.get(nade_info["NadeType"], "")
        n_list.append((nade_info["StartSnapShotIndex"] / ss_index_max, nade, nade_info["ThrowerSide"]))

    plant = round_snapshot.get("BombPlantedSSIndex", 0) / ss_index_max
    return time_list, tk_list, ctk_list, plant, plant_site, n_list
