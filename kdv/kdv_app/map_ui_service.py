# -*- coding: utf-8 -*-

from .constants import KDV_SCALE_MAP

LAYERED_MAPS = {"de_nuke", "de_vertigo"}


class MapUiService:
    def __init__(self, root):
        self.root = root

    def refresh_layer(self):
        root = self.root
        if root.ko is None:
            print("Load kdz first!")
            return

        root.kdvmap.load_map(root.map_name)
        root.refresh()

    def change_layer(self):
        root = self.root
        if root.ko is None:
            print("Load kdz first!")
            return
        if root.map_layer == 0:
            root.map_layer = -1
            root.map_layer_sp.text = "Lower"
        elif root.map_layer == -1:
            root.map_layer = 0
            root.map_layer_sp.text = "Upper"

        if root.map_name not in LAYERED_MAPS:
            root.map_layer_sp.text = "Upper"
            root.map_layer = 0

    def resize_map(self, size):
        root = self.root
        if root.mb_init_size == [0, 0]:
            if size[0] != 0 and size[1] != 0:
                root.mb_init_size = size
        else:
            min_scale = min(size[0] / root.mb_init_size[0], size[1] / root.mb_init_size[1])
            root.kdvmap.scale = KDV_SCALE_MAP[root.map_name] * min_scale
        root.refresh()

    def change_paint_color(self):
        root = self.root
        if root.color_sp.text == "White":
            root.color_sp.color = (1, 1, 1, 1)
            root.paint.color = (1, 1, 1, 1)
        elif root.color_sp.text == "Orange":
            root.color_sp.color = (1, 0.251, 0, 1)
            root.paint.color = (1, 0.251, 0, 1)
        elif root.color_sp.text == "Blue":
            root.color_sp.color = (0.180, 0.996, 0.969, 1)
            root.paint.color = (0.180, 0.996, 0.969, 1)
