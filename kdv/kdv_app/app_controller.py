# -*- coding: utf-8 -*-
from kivy.clock import Clock
from kivy.core.window import Window


class KdvController:
    def __init__(self, root):
        self.root = root

    def handle_key(self, keycode):
        key = keycode[1]
        if key == "f11":
            if Window.fullscreen is False:
                Window.fullscreen = "auto"
            elif Window.fullscreen == "auto":
                Window.fullscreen = False
        if key == "tab":
            for i, tb in enumerate(self.root.tab.tab_list):
                if self.root.tab.current_tab == tb:
                    self.root.current_tab = i
                    break
            self.root.current_tab -= 1
            if self.root.current_tab < 0:
                self.root.current_tab = len(self.root.tab.tab_list) - 1
            self.root.tab.switch_to(self.root.tab.tab_list[self.root.current_tab])
        if key == "c":
            self.root.paint.clear()
        if key == "t":
            self.root.map_traj_toggle.state = "normal" if self.root.map_traj_toggle.state == "down" else "down"
        if self.root.ko is None:
            return True
        if key == "spacebar":
            self.press_play()
        if key == "left" or key == "a":
            self.decrement_index_3sec()
        if key == "right" or key == "d":
            self.increment_index_3sec()
        if key == "up" or key == "w":
            self.load_prev_round()
        if key == "down" or key == "s":
            self.load_next_round()
        if key == "1":
            self.root.speed_sp.text = "x1"
            self.root.is_playing_speed = 1
            self.change_speed()
        if key == "2":
            self.root.speed_sp.text = "x2"
            self.root.is_playing_speed = 2
            self.change_speed()
        if key == "4":
            self.root.speed_sp.text = "x4"
            self.root.is_playing_speed = 4
            self.change_speed()
        if key in ["h", "3", "5"]:
            self.root.speed_sp.text = "x1/2"
            self.root.is_playing_speed = 0.5
            self.change_speed()
        if key == "v":
            self.root.chk_sl.active = not self.root.chk_sl.active
        if key == "g":
            self.root.chk_pu.active = not self.root.chk_pu.active
        if key == "b":
            self.root.current_ss_index = self.root.bookmark_index
            self.root.update_ss(self.root.current_ss_index)
        if key == "lctrl":
            self.root.change_layer()
            self.root.refresh_layer()

        return True

    def press_play(self):
        if self.root.ko is None:
            print("Load kdz first!")
            return
        if self.root.is_playing is False:
            self.play()
        else:
            self.stop()

    def play(self):
        if self.root.ko is None:
            return
        if self.root.playing_event is not None:
            self.root.playing_event.cancel()
        self.root.is_playing = True
        if self.root.is_playing_speed == 4:
            self.root.playing_event = Clock.schedule_interval(self.increment_index, 0.25 * self.root.second_per_frame)
        elif self.root.is_playing_speed == 2:
            self.root.playing_event = Clock.schedule_interval(self.increment_index, 0.5 * self.root.second_per_frame)
        elif self.root.is_playing_speed == 0.5:
            self.root.playing_event = Clock.schedule_interval(self.increment_index, 2 * self.root.second_per_frame)
        else:
            self.root.playing_event = Clock.schedule_interval(self.increment_index, self.root.second_per_frame)

    def stop(self):
        if self.root.ko is None:
            return
        if self.root.playing_event is not None:
            self.root.playing_event.cancel()
        self.root.is_playing = False

    def change_speed(self):
        if self.root.speed_sp.text == "x1":
            self.root.is_playing_speed = 1
            self.stop()
            self.play()
        elif self.root.speed_sp.text == "x1/2":
            self.root.is_playing_speed = 0.5
            self.stop()
            self.play()
        elif self.root.speed_sp.text == "x2":
            self.root.is_playing_speed = 2
            self.stop()
            self.play()
        elif self.root.speed_sp.text == "x4":
            self.root.is_playing_speed = 4
            self.stop()
            self.play()

    def increment_index(self, *args):
        if self.root.current_ss_index >= self.root.ss_index_max:
            self.stop()
            self.root.playing_event.cancel()
        else:
            self.root.current_ss_index += 1

    def increment_index_5sec(self):
        if self.root.ko:
            new_index = self.root.current_ss_index + (5 * self.root.ko.Header["SnapshotRate"])
            if new_index >= self.root.ss_index_max:
                new_index = self.root.ss_index_max
            self.root.current_ss_index = new_index

    def decrement_index_5sec(self):
        if self.root.ko:
            new_index = self.root.current_ss_index - (5 * self.root.ko.Header["SnapshotRate"])
            if new_index <= 0:
                new_index = 0
            self.root.current_ss_index = new_index

    def increment_index_3sec(self):
        if self.root.ko:
            new_index = self.root.current_ss_index + (3 * self.root.ko.Header["SnapshotRate"])
            if new_index >= self.root.ss_index_max:
                new_index = self.root.ss_index_max
            self.root.current_ss_index = new_index

    def decrement_index_3sec(self):
        if self.root.ko:
            new_index = self.root.current_ss_index - (3 * self.root.ko.Header["SnapshotRate"])
            if new_index <= 0:
                new_index = 0
            self.root.current_ss_index = new_index

    def load_next_round(self):
        self.root.current_round_index += 1
        if self.root.current_round_index >= self.root.round_index_max:
            self.root.current_round_index = self.root.round_index_max - 1
        else:
            self.root.load_round(self.root.current_round_index)

    def load_prev_round(self):
        self.root.current_round_index -= 1
        if self.root.current_round_index < 0:
            self.root.current_round_index = 0
        else:
            self.root.load_round(self.root.current_round_index)
