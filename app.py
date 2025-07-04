try:
    from PyQt6.QtGui import QColor
except:
    from PyQt5.QtGui import QColor

from krita import (
    Krita,
    DockWidget,
    ManagedColor,
    Canvas
)
from .lib_zen import mix, relative_color_shift
from .utils import (
    Light, 
    q_to_managed_color, 
    managed_to_q_color,
    get_managed_color_comps,
    set_managed_color_comps,
    get_mixed_colors, 
    get_color_idx
)

class App():
    default_light_color = QColor.fromRgb(230, 205, 167)
    default_ambient_color = QColor.fromRgb(73, 120, 234)

    def __init__(self, dock_widget: DockWidget, current_color: ManagedColor = None, settings=None):
        krita_instance = Krita.instance()
        notifier = krita_instance.notifier()
        notifier.setActive(True)

        self.__dock_widget = dock_widget
        self.__krita_instance = krita_instance

        self.__current_color = current_color if current_color is not None else q_to_managed_color(
            self.canvas,
            QColor.fromRgbF(0.0, 0.0, 0.0, 1)
        )

        self.__main_light = Light(
            q_to_managed_color(self.canvas, self.default_light_color),
            0.3
        )
        self.__ambient_light = Light(
            q_to_managed_color(self.canvas, self.default_ambient_color),
            0.2
        )

        self.__color_to_match: ManagedColor = None
        self.__saved_colors = []
        self.__contrast = 1.0
        self.__value_range = (0.0, 1.0)

    @property
    def krita_instance(self):
        return self.__krita_instance

    def current_color(self, comps: bool = False) -> ManagedColor | list[float]:
        if not comps:
            return self.__current_color

        components = [0.0] * 4
        rgba = get_managed_color_comps(self.__current_color)
        comps_len = len(rgba)

        if comps_len == len(components):
            r, g, b, a = rgba
            components[0] = r
            components[1] = g
            components[2] = b
            components[3] = a

        return components

    def set_current_color(self, color: ManagedColor):
        self.__current_color = color

    @property
    def main_light(self) -> Light:
        return self.__main_light

    @property
    def ambient_light(self) -> Light:
        return self.__ambient_light

    @property
    def saved_colors(self) -> list[QColor]:
        return self.__saved_colors

    @property
    def dock_widget(self) -> DockWidget:
        return self.__dock_widget

    @property
    def canvas(self) -> Canvas:
            return self.__dock_widget.canvas()

    @property
    def contrast(self) -> float:
        return self.__contrast

    @contrast.setter
    def contrast(self, value: float):
        self.__contrast = value

    @property
    def value_range(self) -> tuple[float, float]:
        return self.__value_range

    @value_range.setter
    def value_range(self, value: tuple[float, float]):
        self.__value_range = value

    @property
    def color_to_match(self) -> ManagedColor:
        return self.__color_to_match

    @color_to_match.setter
    def color_to_match(self, color: ManagedColor):
        self.__color_to_match = color

    def foregroundColor(self) -> ManagedColor:
        canvas = self.canvas
        if canvas is not None:
            return canvas.view().foregroundColor()
        else:
            raise ValueError('no active canvas.')

    def sync(self):
        canvas = self.canvas
        if canvas is None or canvas.view() is None:
            return

        active_view = self.krita_instance.activeWindow().activeView()
        color_fg = active_view.foregroundColor()
        color_bg = active_view.backgroundColor()

        self.set_current_color(color_fg)

    @property
    def current_color_mix(self) -> tuple[ManagedColor, ManagedColor, ManagedColor]:
        managed_color = self.current_color()

        illuminated_color = get_mixed_colors(
            managed_color, 
            self.__main_light
        )
        shadow_color = get_mixed_colors(
            managed_color, 
            self.__ambient_light
        )
        r, g, b, a = get_managed_color_comps(shadow_color)
        s_r, s_g, s_b = relative_color_shift((r, g, b), 0.0, 0.2)
        shadow_color = set_managed_color_comps(shadow_color, [s_r, s_g, s_b, a])

        return (managed_color, illuminated_color, shadow_color) 

    def try_remove_local_color(self, to_remove: ManagedColor):
        colors = self.__saved_colors

        idx = get_color_idx(to_remove, colors)
        if idx == -1:
            raise ValueError("id not found in local_color list")

        if len(colors) > 1:
            colors[idx], colors[-1] = colors[-1], colors[idx]
        colors.pop()

    def try_set_foreground_color(self, color: ManagedColor) -> ManagedColor:
        canvas = self.canvas
        if canvas is not None:
            canvas.view().setForeGroundColor(color)
        else:
            raise ValueError('No active canvas')

    #TODO: refactor to be able to add more light colors?
    # do i even need more than 3 light sources?
    def try_update_main_light(self) -> ManagedColor:
        managed_color = self.foregroundColor()
        self.__main_light.color = managed_color

        return managed_color

    def try_update_ambient_light(self) -> ManagedColor:
        managed_color = self.foregroundColor()
        self.__ambient_light.color = managed_color

        return managed_color
