# -*- coding: utf-8 -*-

from .ui_components import SimpleRoundButton


class RoundListPresenter:
    def __init__(self, root):
        self.root = root

    def load_simple_round_list(self, round_index_max):
        root = self.root
        if root.ko is None:
            return

        root.simple_round_btn_list = []

        for i in range(round_index_max):
            btn = SimpleRoundButton()
            btn.round_index = i
            btn.text = str(root.ko.MatchStats["RoundInfoList"][i]["RoundNumber"])

            if root.ko.oneround_mode is False and i == 0:
                btn.state = "down"
            elif root.ko.oneround_mode is True and root.ko.onefile_index == i:
                btn.state = "down"
            else:
                btn.state = "normal"

            if root.ko.oneround_mode is True and root.ko.onefile_index != btn.round_index:
                btn.opacity = 0.3

            root.simple_round_btn_list.append(btn)
            root.simple_round_list.add_widget(btn)

    def update_simple_round_list(self):
        root = self.root
        for i, srb in enumerate(root.simple_round_btn_list):
            if root.current_round_index == i:
                srb.state = "down"
            else:
                srb.state = "normal"

    def update_round_list(self):
        root = self.root
        rv = root.round_list_panel
        if rv is None or not hasattr(rv, "data") or not rv.data:
            return

        for i, item in enumerate(rv.data):
            item["selected"] = i == root.current_round_index

        rv.refresh_from_data()

        if len(rv.data) > 1:
            rv.scroll_y = 1 - (root.current_round_index / (len(rv.data) - 1))
        else:
            rv.scroll_y = 1
