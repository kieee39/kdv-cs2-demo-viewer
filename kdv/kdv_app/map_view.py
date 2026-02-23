# -*- coding: utf-8 -*-
from kivy.app import App
from kivy.graphics.context_instructions import Color, PopMatrix, PushMatrix, Rotate
from kivy.graphics.instructions import InstructionGroup
from kivy.graphics.vertex_instructions import Ellipse, Line, Rectangle, Triangle
from kivy.properties import (
    BooleanProperty,
    ListProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.scatter import Scatter
from kivy.uix.widget import Widget

from . import constants, kdm
from .constants import (
    BOMB_SIZE,
    C4DF_IMG_PATH,
    C4DT_IMG_PATH,
    C4P_IMG_PATH,
    C4_IMG_PATH,
    CT_COLOR,
    CT_LA_IMG_PATH,
    GRD_SIZE,
    MOLOTOV_SECOND,
    PLY_SIZE,
    SIDE_COLOR,
    SMOKE_SECOND,
    T_COLOR,
    T_LA_IMG_PATH,
    TIMER_SIZE,
    is_on_targetlayer,
)


class Player(Widget):
    root = ObjectProperty(None)
    angle = NumericProperty(0)

    he_color = (0.333, 0.42, 0.184, 0.8)
    fb_color = (0, 1, 1, 0.8)
    smoke_color = (1, 1, 1, 0.8)
    molo_color = (1, 0, 0, 0.8)

    def __init__(self, **kwargs):
        super(Player, self).__init__(**kwargs)
        self.player_group_before = None
        self.player_group = None

        self.namelabel = self.ids["namelabel"]
        self.numlabel = self.ids["numlabel"]
        self.acwlabel = self.ids["acwlabel"]

        self.map_name = ""

    def init_player(self, number, name, side, player_ss):
        map_scale = max(constants.MAP_SCALE, 1)
        self.width = PLY_SIZE / map_scale
        self.height = PLY_SIZE / map_scale
        self.bomb_icon_size = BOMB_SIZE / map_scale
        self.la_icon_size = 80 / map_scale

        self.blind_circle_size = self.width * 1.4
        self.awp_rec_width = self.width * 0.6
        self.awp_rec_height = self.height * 0.2
        self.awp_ind_space = self.width * 0.1
        self.nade_circle_size = self.width * 0.3
        self.tri_ind_space = self.width * 0.1
        self.tri_height = self.height * 0.4
        self.tri_width_half = self.height * 0.6 / 2
        self.bullet_space = self.width * 0.6
        self.bullet_length = self.width * 15
        self.vl_length = self.width * 50

        self.namelabel.text = name
        self.namelabel.font_size = 12 * (4.9 / map_scale)
        self.numlabel.text = str(number)
        self.numlabel.font_size = 12 * (4.9 / map_scale)
        self.acwlabel.font_size = 10 * (4.9 / map_scale)

        self.chk_wico = self.root.chk_wico
        self.chk_name = self.root.chk_name
        self.chk_num = self.root.chk_num
        self.chk_hp = self.root.chk_hp
        self.chk_sl = self.root.chk_sl
        self.chk_pu = self.root.chk_pu

        self.side = side
        if self.side == "T":
            self.color = (*T_COLOR, 0.9)  # CT
        else:
            self.color = (*CT_COLOR, 0.9)  # CT

        self.update(player_ss)

    def update(self, player_ss):
        player_x = player_ss["Positions"]["X"]
        player_y = player_ss["Positions"]["Y"]
        player_z = player_ss["Positions"]["Z"]

        if self.map_name in ["de_nuke", "de_vertigo"]:
            if is_on_targetlayer(player_z, self.root.map_layer, self.map_name):
                self.opacity = 1
            else:
                self.opacity = 0.4
        else:
            self.opacity = 1

        if player_ss["Hp"] <= 0 and not player_ss["Alive"]:
            if self.player_group_before is not None:
                self.canvas.before.remove(self.player_group_before)
            if self.player_group is not None:
                self.canvas.remove(self.player_group)

            last_alive_x = player_ss["LastAlivePosition"]["X"]
            last_alive_y = player_ss["LastAlivePosition"]["Y"]
            last_alive_z = player_ss["LastAlivePosition"]["Z"]
            la_opacity = 0.7

            if self.map_name in ["de_nuke", "de_vertigo"]:
                if is_on_targetlayer(last_alive_z, self.root.map_layer, self.map_name):
                    la_opacity = 0.7
                else:
                    la_opacity = 0.3

            self.namelabel.opacity = 0
            self.numlabel.opacity = 0
            self.acwlabel.opacity = 0

            # Draw LastAlive Pos
            self.player_group_before = InstructionGroup()
            size = (self.la_icon_size, self.la_icon_size)
            pos = (last_alive_x - self.la_icon_size / 2, last_alive_y - self.la_icon_size / 2)
            self.player_group_before.add(Color(1, 1, 1, la_opacity))
            if self.side == "T":
                self.player_group_before.add(Rectangle(size=size, pos=pos, source=T_LA_IMG_PATH))
            else:
                self.player_group_before.add(Rectangle(size=size, pos=pos, source=CT_LA_IMG_PATH))
            self.player_group_before.add(Color(1, 1, 1, 0))
            self.canvas.before.add(self.player_group_before)
            return

        else:
            if self.chk_name.active is True:
                self.namelabel.opacity = 1
            else:
                self.namelabel.opacity = 0

            if self.chk_num.active is True:
                self.numlabel.opacity = 1
            else:
                self.numlabel.opacity = 0

            if self.chk_wico.active is True:
                self.acwlabel.opacity = 1
            else:
                self.acwlabel.opacity = 0

        self.acwlabel.text = kdm.EQMAP[player_ss["ActiveEquipment"]]

        self.center_x = player_ss["Positions"]["X"]
        self.center_y = player_ss["Positions"]["Y"]
        self.angle = player_ss["ViewDirectionX"]
        try:
            self.bomb = player_ss["HasBomb"]
        except KeyError:
            self.bomb = False

        if self.player_group_before is not None:
            self.canvas.before.remove(self.player_group_before)
        self.player_group_before = InstructionGroup()
        self.player_group_before.add(Color(*self.color))
        self.player_group_before.add(Ellipse(size=self.size, pos=self.pos))
        if self.bomb is True:
            size = (self.bomb_icon_size, self.bomb_icon_size)
            pos = (self.right, self.y - self.bomb_icon_size)
            self.player_group_before.add(Color(1, 1, 1, 1))
            self.player_group_before.add(Rectangle(size=size, pos=pos, source=C4_IMG_PATH))
        self.canvas.before.add(self.player_group_before)

        if self.player_group is not None:
            self.canvas.remove(self.player_group)
        self.player_group = InstructionGroup()

        if self.chk_hp.active is True:
            if player_ss["Hp"] > 50:
                hp_color = (0, 1, 0.25, 1)
            elif player_ss["Hp"] < 65 and player_ss["Hp"] > 30:
                hp_color = (1, 1, 0, 1)
            else:
                hp_color = (1, 0, 0, 1)
            self.player_group.add(Color(*hp_color))
            self.player_group.add(
                Line(
                    width=1.05,
                    points=(
                        self.x - self.bullet_space / 2,
                        self.y,
                        self.x - self.bullet_space / 2,
                        self.y + self.height * (player_ss["Hp"] / 100),
                    ),
                )
            )

        if self.chk_pu.active is True:
            icon_size = self.height / 2.5
            pos_x = self.right + self.tri_height
            if player_ss["He"] > 0:
                self.player_group.add(Color(*self.he_color))
                self.player_group.add(Ellipse(pos=(pos_x, self.y + (3 / 4) * self.height), size=(icon_size, icon_size)))
            if player_ss["Fb"] > 0:
                self.player_group.add(Color(*self.fb_color))
                self.player_group.add(Ellipse(pos=(pos_x, self.y + (2 / 4) * self.height), size=(icon_size, icon_size)))
            if player_ss["Smk"] > 0:
                self.player_group.add(Color(*self.smoke_color))
                self.player_group.add(Ellipse(pos=(pos_x, self.y + (1 / 4) * self.height), size=(icon_size, icon_size)))
            if player_ss["Mol"] > 0 or player_ss["Inc"] > 0:
                self.player_group.add(Color(*self.molo_color))
                self.player_group.add(Ellipse(pos=(pos_x, self.y), size=(icon_size, icon_size)))

        if player_ss["FlashDuration"] > 0:
            self.player_group.add(Color(1, 1, 1, 0.3))
            start, end = self.fd_calc(player_ss["FlashDuration"])
            self.player_group.add(
                Ellipse(
                    size=(self.blind_circle_size, self.blind_circle_size),
                    pos=(self.x - (self.blind_circle_size - self.width) / 2, self.y - (self.blind_circle_size - self.height) / 2),
                    angle_start=start,
                    angle_end=end,
                )
            )
        self.player_group.add(Color(*self.color))

        self.player_group.add(PushMatrix())
        self.player_group.add(Rotate(angle=self.angle, origin=self.center))
        if player_ss["ActiveEquipment"] == 309 or player_ss["ActiveEquipment"] == 306:  # AWP
            self.player_group.add(
                Rectangle(
                    pos=(self.right + self.awp_ind_space, self.center_y - self.awp_rec_height / 2),
                    size=(self.awp_rec_width, self.awp_rec_height),
                )
            )
        elif self.get_weapon_class(player_ss["ActiveEquipment"]) == 1:  # Nades
            self.player_group.add(
                Ellipse(
                    pos=(self.right + self.awp_ind_space, self.center_y - self.nade_circle_size / 2),
                    size=(self.nade_circle_size, self.nade_circle_size),
                )
            )
        else:
            self.player_group.add(
                Triangle(
                    points=(
                        self.right + self.tri_height,
                        self.center_y,
                        self.right + self.tri_ind_space,
                        self.center_y + self.tri_width_half,
                        self.right + self.tri_ind_space,
                        self.center_y - self.tri_width_half,
                    )
                )
            )
        if player_ss["Firing"] is True and self.get_weapon_class(player_ss["ActiveEquipment"]) == 0:
            self.player_group.add(Line(points=(self.right + self.bullet_space, self.center_y, self.right + self.bullet_length, self.center_y)))

        if self.chk_sl.active is True:
            if self.map_name in ["de_nuke", "de_vertigo"]:
                if is_on_targetlayer(player_z, self.root.map_layer, self.map_name):
                    self.player_group.add(Color(*self.color[:-1], 0.3))
                else:
                    self.player_group.add(Color(*self.color[:-1], 0.1))
            else:
                self.player_group.add(Color(*self.color[:-1], 0.3))
            self.player_group.add(Line(points=(self.right, self.center_y, self.right + self.vl_length, self.center_y)))
        self.player_group.add(PopMatrix())

        self.canvas.add(self.player_group)

    def fd_calc(self, f_duration):
        if f_duration > 3:
            return 0, 360
        else:
            return 180 - 180 * (f_duration / 3), 180 + 180 * (f_duration / 3)

    def get_weapon_class(self, eq_element):
        if eq_element < 400:
            return 0
        elif eq_element // 500 == 1:
            return 1
        elif eq_element // 400 == 1:
            return 2
        else:
            return -1


class GrenadeLayer(Widget):
    map_board_obj = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(GrenadeLayer, self).__init__(**kwargs)
        self.map_name = ""
        self.nades_ss = None
        self.nades_map = None
        self.nades_effect_ss = None
        self.nades_effect_map = None

        self.bomb_ss = None

        self.ent_group = None
        self.efct_group = None

        map_scale = max(constants.MAP_SCALE, 1)
        self.nade_drawing_size = GRD_SIZE / map_scale
        self.bomb_drawing_size = BOMB_SIZE / map_scale

        self.bomb_img_path = C4_IMG_PATH

        self.he_color = (0.294, 0.541, 0.031, 0.9)
        self.fb_color = (0.180, 0.604, 0.996, 0.9)
        self.smoke_color = (0.8, 0.8, 0.8, 0.9)
        self.molo_color = (1, 0.251, 0.090, 0.8)
        self.decoy_color = (0.694, 0.537, 0.016, 0.9)

        self.he_color_e = (0.294, 0.541, 0.031, 0.4)
        self.fb_color_e = (0.180, 0.604, 0.996, 0.4)
        self.smoke_color_e = (0.8, 0.8, 0.8, 0.5)
        self.molo_color_e = (1, 0.251, 0.090, 0.4)
        self.decoy_color_e = (0.694, 0.537, 0.016, 0.4)

        self.nadecolor_map = {
            501: self.decoy_color,
            502: self.molo_color,
            503: self.molo_color,
            504: self.fb_color,
            505: self.smoke_color,
            506: self.he_color,
        }
        self.nadecolor_e_map = {
            501: self.decoy_color_e,
            502: self.molo_color_e,
            503: self.molo_color_e,
            504: self.fb_color_e,
            505: self.smoke_color_e,
            506: self.he_color_e,
        }
        self.nadesize_map = {
            501: 60 / map_scale,
            502: 288 / map_scale,
            503: 288 / map_scale,
            504: 144 / map_scale,
            505: 288 / map_scale,
            506: 384 / map_scale,
        }
        self.foot_radius = 2048 / map_scale

    def init_gl(self, nades_ss, nades_map, nades_effect_ss, nades_effect_map, bomb_ss):
        self.nades_ss = nades_ss
        self.nades_map = nades_map
        self.nades_effect_ss = nades_effect_ss
        self.nades_effect_map = nades_effect_map

        self.bomb_ss = bomb_ss

        app = App.get_running_app()
        self.kdv = app.root

    def set_bomb_indices(self, plant, deto, defuse):
        self.plant_index = plant
        self.deto_index = deto
        self.defuse_index = defuse

    def update(self, ssindex):
        if self.nades_ss is None or self.nades_map is None or self.bomb_ss is None:
            return

        self.canvas.clear()

        if self.nades_ss[ssindex] is not None:
            for nss in self.nades_ss[ssindex]:
                target_nademap = self.nades_map[nss]

                throw_x = target_nademap["ThrowPos"]["X"]
                throw_y = target_nademap["ThrowPos"]["Y"]
                throw_z = target_nademap["ThrowPos"]["Z"]

                r_index = ssindex - target_nademap["StartSnapShotIndex"]
                if r_index <= 0:
                    r_index = 0
                elif r_index >= len(target_nademap["NadePointsList"]):
                    r_index = len(target_nademap["NadePointsList"]) - 1
                points_list = self.get_points(target_nademap["NadePointsList"][r_index])
                points_z_list = self.get_points_z(target_nademap["NadePointsList"][r_index])

                if is_on_targetlayer(points_z_list[-1], self.kdv.map_layer, self.map_name):
                    self.canvas.add(Color(*self.nadecolor_map[target_nademap["NadeType"]][:3], 0.9))
                else:
                    self.canvas.add(Color(*self.nadecolor_map[target_nademap["NadeType"]][:3], 0.4))

                try:
                    dt = target_nademap["NadePointsList"][r_index]["IsDetonated"]
                except KeyError:
                    dt = False
                if dt is False:
                    self.canvas.add(Line(points=points_list, width=1))
                self.canvas.add(
                    Ellipse(
                        pos=(points_list[-2] - self.nade_drawing_size / 2, points_list[-1] - self.nade_drawing_size / 2),
                        size=(self.nade_drawing_size, self.nade_drawing_size),
                    )
                )

        if self.nades_effect_ss[ssindex] is not None:
            for ness in self.nades_effect_ss[ssindex]:
                target_effect_map = self.nades_effect_map[ness]
                effect_x = target_effect_map["Point"]["X"]
                effect_y = target_effect_map["Point"]["Y"]
                effect_z = target_effect_map["Point"]["Z"]

                size = self.nadesize_map[target_effect_map["NadeType"]]
                points = (target_effect_map["Point"]["X"] - size / 2, target_effect_map["Point"]["Y"] - size / 2)
                if is_on_targetlayer(effect_z, self.kdv.map_layer, self.map_name):
                    self.canvas.add(Color(*self.nadecolor_e_map[target_effect_map["NadeType"]][:3], 0.5))
                else:
                    if target_effect_map["NadeType"] in [502, 503]:
                        self.canvas.add(Color(*self.nadecolor_e_map[target_effect_map["NadeType"]][:3], 0.2))
                    else:
                        self.canvas.add(Color(*self.nadecolor_e_map[target_effect_map["NadeType"]][:3], 0.15))

                self.canvas.add(Ellipse(pos=points, size=(size, size)))

                if target_effect_map["NadeType"] == 505:
                    timer_size = TIMER_SIZE / max(constants.MAP_SCALE, 1)
                    timer_points = (target_effect_map["Point"]["X"] - timer_size / 2, target_effect_map["Point"]["Y"] - timer_size / 2)

                    max_sec = (target_effect_map["EndTick"] - target_effect_map["StartTick"]) / self.kdv.demo_tick
                    if max_sec <= 0:
                        max_sec = SMOKE_SECOND if target_effect_map["NadeType"] == 505 else MOLOTOV_SECOND

                    end_angle = 360 * (1 - (self.kdv.current_tick - target_effect_map["StartTick"]) / (self.kdv.demo_tick * max_sec))
                    if end_angle <= 0:
                        end_angle = 1
                    elif end_angle >= 360:
                        end_angle = 359
                    if is_on_targetlayer(effect_z, self.kdv.map_layer, self.map_name):
                        self.canvas.add(Color(*SIDE_COLOR[target_effect_map["ThrowerSide"]], 0.65))
                    else:
                        self.canvas.add(Color(*SIDE_COLOR[target_effect_map["ThrowerSide"]], 0.15))
                    self.canvas.add(Ellipse(size=(timer_size, timer_size), pos=timer_points, angle_start=0, angle_end=end_angle))

        if self.bomb_ss[ssindex] is not None:
            bomb = self.bomb_ss[ssindex]
            try:
                isOnGround = bomb["OnGround"]
            except KeyError:
                isOnGround = False

            if isOnGround is True:
                if self.plant_index == 0:
                    self.bomb_img_path = C4_IMG_PATH
                elif ssindex < self.plant_index:
                    self.bomb_img_path = C4_IMG_PATH
                elif ssindex >= self.plant_index:
                    self.bomb_img_path = C4P_IMG_PATH

                if self.deto_index != 0 and self.deto_index <= ssindex:
                    self.bomb_img_path = C4DT_IMG_PATH
                if self.defuse_index != 0 and self.defuse_index <= ssindex:
                    self.bomb_img_path = C4DF_IMG_PATH

                size = (self.bomb_drawing_size, self.bomb_drawing_size)
                pos = (bomb["Pos"]["X"] - self.bomb_drawing_size / 2, bomb["Pos"]["Y"] - self.bomb_drawing_size / 2)
                if is_on_targetlayer(bomb["Pos"]["Z"], self.kdv.map_layer, self.map_name):
                    self.canvas.add(Color(1, 1, 1, 0.9))
                else:
                    self.canvas.add(Color(1, 1, 1, 0.4))

                self.canvas.add(Rectangle(pos=pos, size=size, source=self.bomb_img_path))

        if self.parent:
            if self.parent.draw_ft:
                fpos = self.parent.ft_pos
                self.canvas.add(Color(1, 1, 1, 0.1))
                self.canvas.add(Ellipse(pos=(fpos[0] - self.foot_radius / 2, fpos[1] - self.foot_radius / 2), size=(self.foot_radius, self.foot_radius)))

    def get_points(self, npoints):
        res = []
        for kdp in npoints["Points"]:
            res.append(kdp["X"])
            res.append(kdp["Y"])
        return res

    def get_points_z(self, npoints):
        res = []
        for kdp in npoints["Points"]:
            res.append(kdp["Z"])
        return res


class KdvMap(Scatter):
    player_list = ListProperty([])
    g_layer = ObjectProperty(None)
    map_path = StringProperty("")
    map_path_lower = StringProperty("")
    map_name = StringProperty("")

    xgap = NumericProperty(0)
    ygap = NumericProperty(0)

    draw_ft = BooleanProperty(False)
    ft_pos = ListProperty([0, 0])

    def __init__(self, **kwargs):
        super(KdvMap, self).__init__(**kwargs)
        self.rss = None
        self.pwidget = []
        self.current_ss_index = 0

        self.back_img = None
        self.back_img_lower = None
        self.traj_color = None
        self.traj_img = None

        self.is_drawing_vl = False
        self.scale = 1

    def load_map(self, map_name):
        self.map_name = map_name
        self.map_path = "./maps/" + map_name + ".png"
        self.map_path_lower = "./maps/" + map_name + "_lower.png"

        self.current_ss_index = 0

        if self.back_img:
            self.canvas.before.remove(self.back_img)
        if self.back_img_lower:
            self.canvas.before.remove(self.back_img_lower)
        if self.traj_color:
            self.canvas.before.remove(self.traj_color)
            self.traj_color = None
        if self.traj_img:
            self.canvas.before.remove(self.traj_img)
            self.traj_img = None

        traj_path = ""
        if self.parent and getattr(self.parent, "ko", None):
            round_index = int(getattr(self.parent, "current_round_index", 0))
            traj_path = self.parent.ko.get_round_trajectory_full_path(round_index)

        with self.canvas.before:
            if self.map_name:
                if (self.map_name in ["de_nuke", "de_vertigo"]) and self.parent.map_layer == -1:
                    self.back_img_lower = Rectangle(size=self.size, source=self.map_path_lower)
                else:
                    self.back_img = Rectangle(size=self.size, source=self.map_path)
                if traj_path and getattr(self.parent, "show_map_traj", False):
                    self.traj_color = Color(1, 1, 1, 1)
                    self.traj_img = Rectangle(size=self.size, source=traj_path)

    def load_round(self, rss, root):
        self.player_list = []
        self.rss = rss
        self.load_map(self.map_name)
        self.clear_widgets()
        for i in range(10):
            player = Player()
            player.root = root
            if i < 5:
                if self.rss["Team0Side"] == 2:
                    side = "T"
                else:
                    side = "CT"
            else:
                if self.rss["Team0Side"] == 2:
                    side = "CT"
                else:
                    side = "T"
            player.init_player(
                (i + 1) % 10,
                self.rss["PlayerNames"][i],
                side,
                self.rss["PlayerDrawingSnapShots"][0]["PlayerDrawingInfo"][i],
            )
            player.map_name = self.map_name
            self.player_list.append(player)
            self.add_widget(player)

        grenade_layer = GrenadeLayer()
        grenade_layer.init_gl(
            self.rss["NadesSnapShots"],
            self.rss["NadesDrawingInfoMap"],
            self.rss["NadeEffectSnapShots"],
            self.rss["NadeEffectMap"],
            self.rss["BombSnapShots"],
        )
        grenade_layer.set_bomb_indices(self.rss["BombPlantedSSIndex"], self.rss["BombDetonatedSSIndex"], self.rss["BombDefusedSSIndex"])
        grenade_layer.map_name = self.map_name
        self.g_layer = grenade_layer
        self.add_widget(grenade_layer)

    def update_ss(self, ssindex):
        self.current_ss_index = ssindex
        for i, p in enumerate(self.player_list):
            p.update(self.rss["PlayerDrawingSnapShots"][ssindex]["PlayerDrawingInfo"][i])
        self.g_layer.update(ssindex)

    def refresh(self):
        for i, p in enumerate(self.player_list):
            p.update(self.rss["PlayerDrawingSnapShots"][self.current_ss_index]["PlayerDrawingInfo"][i])
        if self.g_layer:
            self.g_layer.update(self.current_ss_index)

    def scale_up(self):
        self.scale = self.scale * 1.2
        if self.scale > self.scale_max:
            self.scale = self.scale_max

    def scale_down(self):
        self.scale = self.scale * 0.8
        if self.scale < self.scale_min:
            self.scale = self.scale_min

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if touch.button == "middle":
                self.draw_ft = True
                self.ft_pos = self.to_local(*touch.pos)
                self.refresh()
                return False
        return super(KdvMap, self).on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.collide_point(*touch.pos):
            if touch.button == "middle":
                self.draw_ft = False
                self.refresh()
                return False
        return super(KdvMap, self).on_touch_up(touch)


class MapBoard(RelativeLayout):
    root = ObjectProperty(None)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if touch.button == "left":
                self.root.press_play()
            if touch.button == "scrolldown":
                for i, v in enumerate(self.root.color_sp.values):
                    if v == self.root.color_sp.text:
                        current_index = i
                        break
                current_index -= 1
                if current_index < 0:
                    current_index = len(self.root.color_sp.values) - 1
                self.root.color_sp.text = self.root.color_sp.values[current_index]
            if touch.button == "scrollup":
                for i, v in enumerate(self.root.color_sp.values):
                    if v == self.root.color_sp.text:
                        current_index = i
                        break
                current_index += 1
                if current_index >= len(self.root.color_sp.values):
                    current_index = 0
                self.root.color_sp.text = self.root.color_sp.values[current_index]
        return super(MapBoard, self).on_touch_down(touch)


class Paint(Widget):
    color = ListProperty([1, 1, 1, 1])

    def on_touch_down(self, touch):
        if touch.button == "right":
            with self.canvas:
                Color(rgba=self.color)
                try:
                    touch.ud["line"] = Line(points=(touch.x, touch.y), width=1.15)
                except KeyError:
                    pass
        return super(Paint, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.button == "right":
            try:
                touch.ud["line"].points += [touch.x, touch.y]
            except KeyError:
                pass

    def clear(self):
        self.canvas.clear()

