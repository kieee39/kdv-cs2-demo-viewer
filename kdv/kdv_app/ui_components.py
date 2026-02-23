# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.core.clipboard import Clipboard
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line
from kivy.properties import (
    BooleanProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.behaviors.togglebutton import ToggleButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.uix.stacklayout import StackLayout
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.factory import Factory

from . import kdm
from .constants import CT_COLOR, CT_COLOR_H, T_COLOR, T_COLOR_H, TEAM_MAP, UTIL_FULL_MAP, WIN_R_MAP


class SimpleRoundButton(ToggleButton):
    def __init__(self, **kwargs):
        super(SimpleRoundButton, self).__init__(**kwargs)
        self.round_index = 0
        self.group = "round"

    def on_press(self):
        self.state = "down"

    def on_release(self):
        self.state = "down"


class ResultPanel(BoxLayout):
    team_name = StringProperty("-")
    score = NumericProperty(0)

    def __init__(self, **kwargs):
        super(ResultPanel, self).__init__(**kwargs)


class RoundTeamStat(BoxLayout):
    money = NumericProperty(0)
    eqvalue = NumericProperty(0)
    ars = ListProperty([0, 0, 0])
    ratio_money = NumericProperty(0)
    ratio_eqvalue = NumericProperty(0)
    align_right = BooleanProperty(False)

    def __init__(self, **kwargs):
        super(RoundTeamStat, self).__init__(**kwargs)


class RoundPanel(ToggleButtonBehavior, BoxLayout):
    index = NumericProperty(0)
    traj_image_path = StringProperty("")
    traj_overlay_alpha = NumericProperty(1)
    round_number = NumericProperty(0)
    winteam_color = ListProperty([0.3, 0.3, 0.3, 0.3])
    team0_score = NumericProperty(0)
    team1_score = NumericProperty(0)
    planted_site = StringProperty("")

    team0_color = ListProperty([0.3, 0.3, 0.3, 0.3])
    team0_money = NumericProperty(0)
    team0_eqvalue = NumericProperty(0)
    team0_ars = ListProperty([0, 0, 0])
    team0_win_r = StringProperty("")

    team1_color = ListProperty([0.3, 0.3, 0.3, 0.3])
    team1_money = NumericProperty(0)
    team1_eqvalue = NumericProperty(0)
    team1_ars = ListProperty([0, 0, 0])
    team1_win_r = StringProperty("")

    def __init__(self, ri=None, **kwargs):
        super().__init__(**kwargs)
        self.selected = False
        if ri is not None:
            self.load_ri(ri)

    def reset_ri(self):
        self.traj_image_path = ""
        self.round_number = 0
        self.winteam_color = [0.3, 0.3, 0.3, 0.3]
        self.team0_score = 0
        self.team1_score = 0
        self.planted_site = ""

        self.team0_color = [0.3, 0.3, 0.3, 0.3]
        self.team0_money = 0
        self.team0_eqvalue = 0
        self.team0_ars = [0, 0, 0]
        self.team0_win_r = ""

        self.team1_color = [0.3, 0.3, 0.3, 0.3]
        self.team1_money = 0
        self.team1_eqvalue = 0
        self.team1_ars = [0, 0, 0]
        self.team1_win_r = ""

    def load_ri(self, ri):
        self.team0_win_r = ""
        self.team1_win_r = ""
        self.round_number = ri["RoundNumber"]

        if ri["Team0Side"] == 2:
            self.team0_color = (*T_COLOR, 0.3)
            self.team1_color = (*CT_COLOR, 0.3)
            if ri["WinTeam"] == 2:  # if t wins
                self.team0_win_r = WIN_R_MAP[ri["WinReason"]]
            elif ri["WinTeam"] == 3:
                self.team1_win_r = WIN_R_MAP[ri["WinReason"]]
        else:
            self.team0_color = (*CT_COLOR, 0.3)
            self.team1_color = (*T_COLOR, 0.3)
            if ri["WinTeam"] == 2:  # if t wins
                self.team1_win_r = WIN_R_MAP[ri["WinReason"]]
            elif ri["WinTeam"] == 3:
                self.team0_win_r = WIN_R_MAP[ri["WinReason"]]

        self.team0_money = ri["Money"][0]
        self.team0_eqvalue = ri["EquipmentValues"][0]
        self.team0_ars = (
            ri["EquipmentCounts"][0]["AwpNumber"],
            ri["EquipmentCounts"][0]["RifleNumber"],
            ri["EquipmentCounts"][0]["SmgNumber"],
        )
        self.team1_money = ri["Money"][1]
        self.team1_eqvalue = ri["EquipmentValues"][1]
        self.team1_ars = (
            ri["EquipmentCounts"][1]["AwpNumber"],
            ri["EquipmentCounts"][1]["RifleNumber"],
            ri["EquipmentCounts"][1]["SmgNumber"],
        )
        if ri["WinTeam"] == 2:  # if t wins
            self.winteam_color = (*T_COLOR, 0.9)
        elif ri["WinTeam"] == 3:
            self.winteam_color = (*CT_COLOR, 0.9)
        else:
            self.winteam_color = (0.5, 0.5, 0.5, 0.9)
        self.team0_score = ri["CorrectScore"][0]
        self.team1_score = ri["CorrectScore"][1]
        self.planted_site = chr(ri["BombPlantedSite"])


class RoundPanelRVItem(RecycleDataViewBehavior, RoundPanel):
    ri = ObjectProperty(None, allownone=True)
    selected = BooleanProperty(False)

    def refresh_view_attrs(self, rv, index, data):
        ret = super().refresh_view_attrs(rv, index, data)
        self.traj_image_path = data.get("traj_image_path", "")

        if self.ri is not None:
            self.load_ri(self.ri)
        else:
            self.reset_ri()

        desired_state = "down" if self.selected else "normal"
        if self.state != desired_state:
            self.state = desired_state

        return ret

    def calc_value_ratio(self, eqvalue):
        if eqvalue <= 0:
            return 0
        elif eqvalue >= 30000:
            return 1
        else:
            return eqvalue / 30000

    def on_popup_parent(self, popup, parent):
        if parent:
            popup.content.focus = True


class NadeLabel(Label):
    pass


class PlayerPanel(BoxLayout):
    slot = NumericProperty(0)
    name = StringProperty("-")
    color = ListProperty([0, 0, 0, 0])

    hp = NumericProperty(0)
    armor = StringProperty("n/a")

    helmet = StringProperty("")
    c4 = StringProperty("")
    defkit = StringProperty("")

    main_wep = ObjectProperty(None)
    sub_wep = ObjectProperty(None)

    he_label = ObjectProperty(None)
    fb_label = ObjectProperty(None)
    sm_label = ObjectProperty(None)
    fire_label = ObjectProperty(None)
    dc_label = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(PlayerPanel, self).__init__(**kwargs)

    def update(self, pdi):
        self.hp = pdi["Hp"]
        self.armor = "A" if pdi["Armor"] > 0 else ""
        self.helmet = "/H" if pdi["HasHelmet"] else ""
        self.c4 = "C4" if pdi["HasBomb"] else ""
        self.defkit = "Dk" if pdi["HasDefuseKit"] else ""

        self.main_wep.opacity = 0.6
        self.sub_wep.opacity = 0.6

        self.he_label.opacity = 0.6
        self.fb_label.opacity = 0.6
        self.sm_label.opacity = 0.6
        self.fire_label.opacity = 0.6
        self.dc_label.opacity = 0.6

        self.main_wep.text = kdm.EQMAP[pdi["PrimaryEq"]]
        self.sub_wep.text = kdm.EQMAP[pdi["SecondaryEq"]]

        acw = pdi["ActiveEquipment"]
        if acw == 405:
            self.main_wep.opacity = 0.6
        elif acw == 0:
            pass
        elif acw < 100:
            self.sub_wep.opacity = 1
        elif 101 <= acw and acw < 400:
            self.main_wep.opacity = 1
        elif acw == 501:
            self.dc_label.opacity = 1
        elif acw == 502 or acw == 503:
            self.fire_label.opacity = 1
        elif acw == 504:
            self.fb_label.opacity = 1
        elif acw == 505:
            self.sm_label.opacity = 1
        elif acw == 506:
            self.he_label.opacity = 1

        if pdi["He"] > 0:
            self.he_label.text = "HE"
        else:
            self.he_label.text = ""

        if pdi["Fb"] == 2:
            self.fb_label.text = "FB FB"
        elif pdi["Fb"] == 1:
            self.fb_label.text = "FB"
        else:
            self.fb_label.text = ""

        if pdi["Smk"] > 0:
            self.sm_label.text = "SG"
        else:
            self.sm_label.text = ""

        if pdi["Mol"] > 0:
            self.fire_label.text = "ML"
        elif pdi["Inc"] > 0:
            self.fire_label.text = "IC"
        else:
            self.fire_label.text = ""

        if pdi["Dec"] > 0:
            self.dc_label.text = "DC"
        else:
            self.dc_label.text = ""


class TeamPanel(BoxLayout):
    team_name = StringProperty("")
    team_color = ListProperty([0.1, 0.1, 0.1, 0.3])
    is_winner = BooleanProperty(False)

    score = NumericProperty(0)
    rsmoney = NumericProperty(0)
    rseqvalue = NumericProperty(0)
    ars = ListProperty([0, 0, 0])
    players_box = ObjectProperty(None)
    player_panels = ListProperty([])

    def __init__(self, **kwargs):
        super(TeamPanel, self).__init__(**kwargs)
        self.bind(team_color=self._sync_player_colors)

    def _sync_player_colors(self, *args):
        for panel in self.player_panels:
            panel.color = self.team_color

    def ensure_player_panels(self, count):
        if self.players_box is None:
            return

        current = len(self.player_panels)
        if current > count:
            for panel in self.player_panels[count:]:
                self.players_box.remove_widget(panel)
            self.player_panels = self.player_panels[:count]
        elif current < count:
            for _ in range(count - current):
                panel = PlayerPanel()
                panel.color = self.team_color
                self.players_box.add_widget(panel)
                self.player_panels.append(panel)

        self._sync_player_colors()


class TeamsPanel(StackLayout):
    round_number = NumericProperty(0)
    win_team = StringProperty("-")
    win_reason = StringProperty("-")
    planted_site = StringProperty("-")

    player_list = ListProperty([])

    def __init__(self, **kwargs):
        super(TeamsPanel, self).__init__(**kwargs)
        self.ms = None
        self.rss = None
        self.team = []

    def load_teamnames(self, matchstats):
        self.ms = matchstats
        self.team = []
        self.team.append(self.ids["team0"])
        self.team.append(self.ids["team1"])

        self.team[0].team_name = self.ms["TeamName"][0]
        self.team[1].team_name = self.ms["TeamName"][1]

        if self.team[0].team_name == "" or self.team[1].team_name == "":
            self.team[0].team_name = "Team0"
            self.team[1].team_name = "Team1"

    def load_round(self, rss, index):
        self.rss = rss
        self.player_list = []

        self.round_number = self.rss["RoundNumber"]

        ri = self.ms["RoundInfoList"][index]

        self.team[0].is_winner = False
        self.team[1].is_winner = False

        if self.rss["Team0Side"] == 2:
            self.team[0].team_color = (*T_COLOR, 0.3)
            self.team[1].team_color = (*CT_COLOR, 0.3)
            if ri["WinTeam"] == 2:  # If T won the round
                self.team[0].is_winner = True
            elif ri["WinTeam"] == 3:
                self.team[1].is_winner = True
        else:
            self.team[0].team_color = (*CT_COLOR, 0.3)
            self.team[1].team_color = (*T_COLOR, 0.3)
            if ri["WinTeam"] == 2:  # If T won the round
                self.team[1].is_winner = True
            elif ri["WinTeam"] == 3:
                self.team[0].is_winner = True

        self.win_team = TEAM_MAP[ri["WinTeam"]]
        self.win_reason = WIN_R_MAP[ri["WinReason"]]
        self.planted_site = chr(ri["BombPlantedSite"])

        for i, t in enumerate(self.team):
            t.score = 0
            t.score = ri["CorrectScore"][i]
            t.rsmoney = ri["Money"][i]
            t.rseqvalue = ri["EquipmentValues"][i]
            t.ars = [
                ri["EquipmentCounts"][i]["AwpNumber"],
                ri["EquipmentCounts"][i]["RifleNumber"],
                ri["EquipmentCounts"][i]["SmgNumber"],
            ]

        total_players = len(self.rss.get("PlayerNames", []))
        per_team = total_players // 2 if total_players else 5
        for team_panel in self.team:
            team_panel.ensure_player_panels(per_team)

        self.player_list.extend(self.team[0].player_panels)
        self.player_list.extend(self.team[1].player_panels)

        for i, p in enumerate(self.player_list):
            if i >= total_players:
                break
            p.slot = (i + 1) % 10
            p.name = self.rss["PlayerNames"][i]

    def update(self, ssindex):
        if self.rss is None:
            return
        for i, p in enumerate(self.rss["PlayerDrawingSnapShots"][ssindex]["PlayerDrawingInfo"]):
            if i >= len(self.player_list):
                break
            self.player_list[i].update(p)


class NadeInfoPanel(BoxLayout, Button):
    ssindex = NumericProperty(0)
    time = StringProperty("")
    tick = StringProperty("")
    thrower = StringProperty("")
    n_type = StringProperty("")
    getpos = StringProperty("")

    def load_ndm(self, ndm, time):
        self.time = "Time:{}".format(time)
        self.tick = "Tick:{}".format(ndm["StartTick"])
        self.ssindex = ndm["StartSnapShotIndex"]
        self.thrower = ndm["ThrowerName"]
        self.n_type = UTIL_FULL_MAP[ndm["NadeType"]]
        if ndm["IsDucking"] is True:
            self.n_type = self.n_type + "(Ducking)"
        angx = self.calc_ang(ndm["ThrowAngX"])
        angy = ndm["ThrowAngY"]
        self.getpos = "setpos {0} {1} {2};setang {3} {4} 0.0000".format(
            ndm["ThrowPos"]["X"], ndm["ThrowPos"]["Y"], ndm["ThrowPos"]["Z"], angy, angx
        )

        if ndm["ThrowerSide"] == 2:
            self.background_color = (*T_COLOR, 0.9)
        else:
            self.background_color = (*CT_COLOR, 0.9)

    def reset_ndm(self):
        self.ssindex = 0
        self.time = ""
        self.tick = ""
        self.thrower = ""
        self.n_type = ""
        self.getpos = ""
        self.background_color = (0.3, 0.3, 0.3, 0.3)

    def calc_ang(self, ang):
        if ang <= 180:
            return ang
        else:
            return (ang - 180) + -180

    def on_press(self):
        app = App.get_running_app()
        app.root.current_ss_index = self.ssindex
        app.root.update_ss(self.ssindex)
        Clipboard.copy(self.getpos)


class EventLog(Label):
    pass


class NadeInfoRVItem(RecycleDataViewBehavior, NadeInfoPanel):
    ndm = ObjectProperty(None, allownone=True)

    def refresh_view_attrs(self, rv, index, data):
        ret = super().refresh_view_attrs(rv, index, data)
        if self.ndm is not None:
            self.load_ndm(self.ndm, data.get("time", ""))
        else:
            self.reset_ndm()
        return ret


Factory.register("RoundTeamStat", cls=RoundTeamStat)
Factory.register("RoundPanelRVItem", cls=RoundPanelRVItem)
Factory.register("NadeInfoRVItem", cls=NadeInfoRVItem)


class EventLogger(GridLayout):
    log_list = ListProperty([])

    def __init__(self, **kwargs):
        super(EventLogger, self).__init__(**kwargs)
        self.log_list = []

    def load_logs(self, event_list):
        self.log_list = []
        if event_list:
            for ev in event_list:
                self.log_list.append((ev["SsIndex"], self.label_constructor(ev)))

    def label_constructor(self, event_log):
        ret = EventLog()
        ret.width = self.width

        tmcolor = ""
        if event_log["Side"] == "T":
            tmcolor = T_COLOR_H[1:]
        elif event_log["Side"] == "CT":
            tmcolor = CT_COLOR_H[1:]
        ret.text = "[color=" + tmcolor + "]" + event_log["Log"] + "[/color]"

        if event_log["Type"] == "Kill":
            ret.text = "[color=FF0000]<Kill>[/color]  " + ret.text
        elif event_log["Type"] == "GrenadeThrown":
            ret.text = "[color=BFFF00]<Utility>[/color]  " + ret.text
        elif (
            event_log["Type"] == "PlantingA"
            or event_log["Type"] == "PlantingB"
            or event_log["Type"] == "PlantedA"
            or event_log["Type"] == "PlantedB"
        ):
            ret.text = "[color=DF7401]<{}>[/color]  ".format(event_log["Type"]) + ret.text
        elif event_log["Type"] == "Defusing":
            ret.text = "[color=0080FF]<Defusing>[/color]  " + ret.text

        return ret

    def update(self, ssindex):
        min_index = ssindex - 32 * 3
        max_index = ssindex
        self.clear_widgets()
        for log in self.log_list:
            if log[0] in range(min_index, max_index):
                self.add_widget(log[1])


class PlayButton(Button):
    def __init__(self, **kwargs):
        super(PlayButton, self).__init__(**kwargs)


class HintBox(Widget):
    rpos = NumericProperty(0)
    color = ListProperty([1, 1, 1, 1])
    hint_text = StringProperty("")


class Seekbar(Slider):
    root = ObjectProperty(None)

    hint_layer = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(Seekbar, self).__init__(**kwargs)
        self.layer = None
        self.hint_w = []

    def draw_hints(self, time_list, tk_list, ctk_list, plant):
        if self.layer:
            self.canvas.remove(self.layer)
        self.canvas.after.clear()
        self.canvas.after.add(Color(rgba=(1, 1, 1, 1)))
        self.canvas.after.add(
            Line(
                points=(
                    (
                        self.x + self.width * (1 / 2),
                        self.y + self.height * (1 / 4),
                        self.x + self.width * (1 / 2),
                        self.top - self.height * (1 / 4),
                    )
                ),
                width=1.2,
            )
        )

    def draw_hints_w(self, time_list, tk_list, ctk_list, plant, plant_site, n_list):
        self.hint_layer.clear_widgets()
        self.hint_w = []
        self.nade_w = []

        for i, t in enumerate(time_list):
            new_hint = HintBox()
            new_hint.opacity = 1
            new_hint.height = self.height / 2
            new_hint.rpos = t
            new_hint.center_x = self.width * t
            new_hint.y = self.height / 4
            new_hint.color = (1, 1, 1, 1)
            if i == 0:
                new_hint.hint_text = "1:30"
            elif i == 1:
                new_hint.hint_text = "1:00"
            elif i == 2:
                new_hint.hint_text = "0:30"

            self.hint_w.append(new_hint)
            self.hint_layer.add_widget(new_hint)
        for tk in tk_list:
            new_hint = HintBox()
            new_hint.opacity = 1
            new_hint.height = self.height
            new_hint.rpos = tk
            new_hint.center_x = self.width * tk
            new_hint.color = (*T_COLOR, 1)
            self.hint_w.append(new_hint)
            self.hint_layer.add_widget(new_hint)
        for ctk in ctk_list:
            new_hint = HintBox()
            new_hint.opacity = 1
            new_hint.height = self.height
            new_hint.rpos = ctk
            new_hint.center_x = self.width * ctk
            new_hint.color = (*CT_COLOR, 1)
            self.hint_w.append(new_hint)
            self.hint_layer.add_widget(new_hint)

        if plant != 0:
            new_hint = HintBox()
            new_hint.opacity = 1
            new_hint.height = self.height
            new_hint.rpos = plant
            new_hint.center_x = +self.width * plant
            new_hint.color = (0.961, 0.020, 0.000, 1)
            new_hint.hint_text = " " + plant_site
            self.hint_w.append(new_hint)
            self.hint_layer.add_widget(new_hint)

        for n in n_list:
            new_hint = HintBox()
            new_hint.height = self.height / 3
            new_hint.rpos = n[0]
            new_hint.center_x = self.width * n[0]
            new_hint.opacity = 0.9
            if len(self.nade_w) != 0:
                if self.nade_w[-1].x > new_hint.x - 10:
                    new_hint.y = self.nade_w[-1].y + 10
                else:
                    new_hint.y = self.height / 12
            else:
                new_hint.y = self.height / 12
            new_hint.color = (1, 1, 1, 0)
            new_hint.hint_text = " " + n[1]

            if n[2] == 2:
                new_hint.hint_text = "[color=" + "FACC2E" + "] " + n[1] + "[/color]"
            elif n[2] == 3:
                new_hint.hint_text = "[color=" + "58D3F7" + "] " + n[1] + "[/color]"

            self.hint_w.append(new_hint)
            self.nade_w.append(new_hint)
            self.hint_layer.add_widget(new_hint)

    def on_width(self, *args):
        for w in self.hint_w:
            w.center_x = self.width * w.rpos

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if touch.button == "right":
                if self.root:
                    ratio = (touch.pos[0] - self.x) / self.width
                    self.root.bookmark_index = int(self.root.ss_index_max * ratio)
                    if self.root.bookmark_index >= self.root.ss_index_max:
                        self.root.bookmark_index = self.root.ss_index_max
                    elif self.root.bookmark_index <= 0:
                        self.root.bookmark_index = 0

        return super(Seekbar, self).on_touch_down(touch)

