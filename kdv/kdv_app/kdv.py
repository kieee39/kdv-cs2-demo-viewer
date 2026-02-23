# -*- coding: utf-8 -*-
import os
import subprocess
import sys

from kivy.config import Config

# Config must be set before importing other Kivy modules to take effect at startup.
Config.set("kivy", "window_icon", "kdv.ico")
Config.set("kivy", "log_enable", 0)
Config.set("input", "mouse", "mouse,disable_multitouch")
Config.set("graphics", "resizable", 1)
Config.set("graphics", "width", "1524")
Config.set("graphics", "height", "1024")
Config.set("graphics", "minimum_width", "800")
Config.set("graphics", "minimum_height", "600")

from kivy.app import App
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import BooleanProperty, ListProperty, NumericProperty, ObjectProperty, StringProperty
from kivy.resources import resource_add_path
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.widget import Widget

from . import constants
from .app_controller import KdvController
from .config_loader import load_config
from .constants import KDV_VER
from .loader import KdvLoader
from .map_ui_service import MapUiService
from .map_view import GrenadeLayer, KdvMap, MapBoard, Paint, Player
from .round_list_presenter import RoundListPresenter
from .seekbar_hints import build_seekbar_hints
from .ui_components import (
    EventLog,
    EventLogger,
    HintBox,
    NadeInfoPanel,
    NadeLabel,
    PlayerPanel,
    PlayButton,
    ResultPanel,
    RoundPanel,
    RoundTeamStat,
    Seekbar,
    TeamPanel,
    TeamsPanel,
)


BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
KV_PATH = os.path.join(BASE_DIR, "kdv.kv")
resource_add_path(BASE_DIR)

constants.apply_config(load_config())


class Kdv(Widget):
    ver = StringProperty("version")
    team0_name = StringProperty("team0")
    team1_name = StringProperty("team1")

    current_ss_index = NumericProperty(0)
    current_round_index = NumericProperty(0)
    current_demo_tick = NumericProperty(0)
    bookmark_index = NumericProperty(0)
    ss_index_max = NumericProperty(0)
    round_index_max = NumericProperty(0)

    is_playing = BooleanProperty(False)
    is_playing_speed = NumericProperty(1)

    current_tick = NumericProperty(0)
    current_time = StringProperty("1:56")

    map_layer = NumericProperty(0)
    mb_init_size = ListProperty([0, 0])
    map_name = StringProperty("")
    show_map_traj = BooleanProperty(False)

    tab = ObjectProperty(None)
    round_list_panel = ObjectProperty(None)
    teams_panel = ObjectProperty(None)
    nade_list_panel = ObjectProperty(None)
    kdvmap = ObjectProperty(None)
    event_logger = ObjectProperty(None)

    seekbar = ObjectProperty(None)
    speed_sp = ObjectProperty(None)
    map_layer_sp = ObjectProperty(None)
    map_traj_toggle = ObjectProperty(None)
    paint = ObjectProperty(None)
    color_sp = ObjectProperty(None)

    simple_round_list = ObjectProperty(None)
    simple_round_btn_list = ListProperty([])

    chk_wico = ObjectProperty(None)
    chk_name = ObjectProperty(None)
    chk_num = ObjectProperty(None)
    chk_hp = ObjectProperty(None)
    chk_sl = ObjectProperty(None)
    chk_pu = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(Kdv, self).__init__(**kwargs)

        self.kdm = None
        self.ko = None

        self.playing_event = None

        self.map_texture = None
        self.mapsub_texture = None

        self.demo_tick = 0
        self.controller = KdvController(self)
        self.loader = KdvLoader(self)
        self.map_ui_service = MapUiService(self)
        self.round_list_presenter = RoundListPresenter(self)

    def _keyboard_start(self):
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        return self.controller.handle_key(keycode)

    def load_kdm_ver(self, file_path):
        self.loader.load_kdm_ver(file_path)

    def load_kdm(self, file_path):
        self.loader.load_kdm(file_path)

    def load_round(self, round_index):
        self.loader.load_round(round_index)

    def load_next_round(self):
        self.controller.load_next_round()

    def load_prev_round(self):
        self.controller.load_prev_round()

    def update_ss(self, ssindex):
        if self.ko is None:
            return
        if self.ss_index_max <= 0:
            self.current_tick = 0
            return
        max_index = max(self.ss_index_max - 1, 0)
        safe_index = int(ssindex)
        if safe_index < 0:
            safe_index = 0
        elif safe_index > max_index:
            safe_index = max_index
        if self.current_ss_index != safe_index:
            self.current_ss_index = safe_index
        if 0 <= safe_index < self.ss_index_max:
            self.kdvmap.update_ss(safe_index)
            self.teams_panel.update(safe_index)
            self.event_logger.update(safe_index)
            self.current_time = self.ko.get_current_time(safe_index)
        try:
            if self.ko.rs_tick_list and safe_index < len(self.ko.rs_tick_list):
                self.current_tick = self.ko.rs_tick_list[safe_index]
            else:
                self.current_tick = 0
        except AttributeError:
            self.current_tick = 0

    def refresh(self, *args):
        self.update_ss(self.current_ss_index)

    def press_play(self):
        self.controller.press_play()

    def play(self):
        self.controller.play()

    def stop(self):
        self.controller.stop()

    def change_speed(self):
        self.controller.change_speed()

    def increment_index(self, *args):
        self.controller.increment_index(*args)

    def increment_index_5sec(self):
        self.controller.increment_index_5sec()

    def decrement_index_5sec(self):
        self.controller.decrement_index_5sec()

    def increment_index_3sec(self):
        self.controller.increment_index_3sec()

    def decrement_index_3sec(self):
        self.controller.decrement_index_3sec()

    def refresh_layer(self):
        self.map_ui_service.refresh_layer()

    def change_layer(self):
        self.map_ui_service.change_layer()

    def resize_map(self, size):
        self.map_ui_service.resize_map(size)

    def change_paint_color(self):
        self.map_ui_service.change_paint_color()

    def copy_tick(self):
        Clipboard.copy("demo_gototick " + str(self.current_tick))

    def get_time_from_index(self, index):
        if self.ko:
            return self.ko.get_current_time(index)
        else:
            return "0:0"

    def load_simple_round_list(self, round_index_max):
        self.round_list_presenter.load_simple_round_list(round_index_max)

    def update_simple_round_list(self):
        self.round_list_presenter.update_simple_round_list()

    def update_round_list(self):
        self.round_list_presenter.update_round_list()

    def load_seekbar(self):
        if self.ko is None or self.ko.rs is None or self.seekbar is None:
            return
        ssrate = self.ko.Header["SnapshotRate"]
        time_list, tk_list, ctk_list, plant, plant_site, n_list = build_seekbar_hints(self.ko.rs, self.ss_index_max, ssrate)
        self.seekbar.draw_hints_w(time_list, tk_list, ctk_list, plant, plant_site, n_list)


class KdvApp(App):
    def build(self):
        if hasattr(sys, "_MEIPASS"):
            resource_add_path(sys._MEIPASS)
        Builder.load_file(KV_PATH)
        Window.bind(on_dropfile=self.on_file_drop)
        self.title = "KumaDemoViewer_" + KDV_VER
        root = Kdv()
        root.kdvmap.scale = 1
        root._keyboard_start()
        return root

    @staticmethod
    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = BASE_DIR
        return os.path.join(base_path, relative_path)

    def on_file_drop(self, widget, file_path):
        file_path_uni = os.fsdecode(file_path)

        filename = os.path.basename(file_path_uni)
        self.title = "KumaDemoViewer_" + KDV_VER + "   " + filename

        kdz, ext = os.path.splitext(file_path_uni)
        kdz = kdz + ".kdz"
        if ext == ".dem":
            if os.path.isfile(kdz):
                self.root.load_kdm_ver(kdz)
                if self.root.ko.MatchStats["KdmVersion"] != KDV_VER:
                    self.title = "KumaDemoViewer_" + KDV_VER + " is Parsing " + file_path_uni
                    res = self.make_kdz(file_path_uni)
                    print("res.returncode =", res.returncode)
                    if res.returncode == 0:
                        filename = os.path.basename(file_path_uni)
                        self.title = "KumaDemoViewer_" + KDV_VER + "   " + filename
                        self.root.load_kdm(kdz)
                        return
                    else:
                        print("error occurred while parsing!")
                        self.title = "KumaDemoViewer_" + KDV_VER
                        return
                else:
                    self.root.load_kdm(kdz)

            else:
                self.title = "KumaDemoViewer_" + KDV_VER + " is Parsing " + file_path_uni
                res = self.make_kdz(file_path_uni)
                print("res.returncode =", res.returncode)
                if res.returncode == 0:
                    filename = os.path.basename(file_path_uni)
                    self.title = "KumaDemoViewer_" + KDV_VER + "   " + filename
                    self.root.load_kdm(kdz)
                    return
                else:
                    print("error occurred while parsing!")
                    return
            return
        elif ext == ".kdz":
            self.root.load_kdm(file_path_uni)
            return

    def make_kdz(self, dem_path):
        return subprocess.run((self.resource_path("./kdv_parser.exe"), "-s", dem_path))


if __name__ == "__main__":
    if hasattr(sys, "_MEIPASS"):
        resource_add_path(os.path.join(sys._MEIPASS))
    KdvApp().run()
