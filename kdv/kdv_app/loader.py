# -*- coding: utf-8 -*-
import os

from . import constants, kdm
from .constants import KDV_SCALE_MAP


class KdvLoader:
    def __init__(self, root):
        self.root = root

    def load_kdm_ver(self, file_path):
        self.root.ko = kdm.KdmObj(file_path)
        self.root.ver = "KDZ_VER_" + self.root.ko.MatchStats["KdmVersion"]

    def load_kdm(self, file_path):
        root = self.root
        root.current_ss_index = 0
        root.current_round_index = 0
        root.current_demo_tick = 0

        root.simple_round_list.clear_widgets()
        root.round_list_panel.data = []

        root.ko = kdm.KdmObj(file_path)
        if root.ko is None:
            print("Kdm is None.")
            return

        root.ver = "KDZ_VER_" + root.ko.MatchStats["KdmVersion"]
        root.second_per_frame = 1 / root.ko.Header["SnapshotRate"]
        root.demo_tick = int(root.ko.Header["TickRate"])
        root.round_index_max = len(root.ko.MatchStats["RoundInfoList"])

        root.team0_name = root.ids["result0"].team_name = root.ko.MatchStats["TeamName"][0]
        root.team1_name = root.ids["result1"].team_name = root.ko.MatchStats["TeamName"][1]
        if root.team0_name == "":
            root.team0_name = root.ids["result0"].team_name = "Team0"
        if root.team1_name == "":
            root.team1_name = root.ids["result1"].team_name = "Team1"
        root.ids["result0"].score = root.ko.MatchStats["RoundInfoList"][-1]["CorrectScore"][0]
        root.ids["result1"].score = root.ko.MatchStats["RoundInfoList"][-1]["CorrectScore"][1]

        round_data = []
        for i, ri in enumerate(root.ko.MatchStats["RoundInfoList"]):
            round_data.append(
                {
                    "index": i,
                    "ri": ri,
                    "traj_image_path": root.ko.get_round_trajectory_path(i),
                    "selected": i == 0,
                }
            )
        root.round_list_panel.data = round_data

        root.teams_panel.load_teamnames(root.ko.MatchStats)

        root.map_name = root.ko.Header["MapName"]
        print(root.ko.Header["MapName"])
        root.kdvmap.load_map(root.map_name)
        if root.map_name not in KDV_SCALE_MAP:
            print(f"Unknown map scale: {root.map_name}")
        root.kdvmap.scale = KDV_SCALE_MAP.get(root.map_name, 1.0)
        xgap, ygap = constants.KDV_GAP_MAP.get(root.map_name, constants.KDV_GAP_DEFAULT)
        root.kdvmap.xgap = xgap
        root.kdvmap.ygap = ygap

        constants.MAP_SCALE = root.ko.get_mapscale()

        root.chk_wico.bind(active=root.refresh)
        root.chk_name.bind(active=root.refresh)
        root.chk_num.bind(active=root.refresh)
        root.chk_hp.bind(active=root.refresh)
        root.chk_sl.bind(active=root.refresh)
        root.chk_pu.bind(active=root.refresh)

        root.load_round(0)
        root.load_simple_round_list(root.round_index_max)
        root.resize_map(root.ids["map_board"].size)
        if not (root.map_name in ["de_nuke", "de_vertigo"]):
            root.change_layer()
        root.refresh_layer()

    def load_round(self, round_index):
        root = self.root
        root.stop()

        root.current_ss_index = 0
        root.bookmark_index = 0

        root.current_round_index = round_index
        if root.current_round_index < 0:
            root.current_round_index = 0
        elif root.current_round_index >= len(root.ko.MatchStats["RoundInfoList"]):
            root.current_round_index = len(root.ko.MatchStats["RoundInfoList"]) - 1

        try:
            root.ko.load_roundsnapshots(root.current_round_index)
        except KeyError:
            print("RoundSnapshots KeyError")
            root.kdvmap.canvas.clear()
            return
        root.ss_index_max = len(root.ko.rs["PlayerDrawingSnapShots"])

        root.teams_panel.load_round(root.ko.rs, root.current_round_index)
        root.teams_panel.update(0)

        root.nade_list_panel.data = []
        tick_nade_map = []
        if root.ko.rs["NadesDrawingInfoMap"] is None:
            root.ko.rs["NadesDrawingInfoMap"] = []
        for ndi in root.ko.rs["NadesDrawingInfoMap"]:
            tick_nade_map.append((int(ndi["StartTick"]), ndi))
        tick_nade_map.sort(key=lambda x: x[0])

        nade_data = []
        for _, ndi in tick_nade_map:
            nade_data.append(
                {
                    "ndm": ndi,
                    "time": root.ko.get_current_time(ndi["StartSnapShotIndex"]),
                }
            )
        root.nade_list_panel.data = nade_data

        root.event_logger.load_logs(root.ko.rs["EventLogs"])

        root.kdvmap.load_round(root.ko.rs, root)

        root.update_ss(0)
        root.load_seekbar()
        root.update_simple_round_list()
        root.update_round_list()
