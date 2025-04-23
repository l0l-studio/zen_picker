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
from .utils import q_to_managed_color, managed_to_q_color, copy_managed_color

class Light():
    def __init__(self, color: ManagedColor, intensity: float = 0.1):
        self.__color = color
        self.__intensity = intensity

    @property
    def color(self) -> ManagedColor:
        return self.__color

    @color.setter
    def set_color(self, color: ManagedColor):
        self.__color = color

    @property
    def intensity(self) -> float:
        return self.__intensity

    @intensity.setter
    def set_intensity(self, intensity: float):
        self.__intensity = intensity

class App():
    default_light_color = QColor.fromRgb(230, 205, 167)
    default_ambient_color = QColor.fromRgb(73, 120, 234)

    def __init__(self, dock_widget: DockWidget, current_color: ManagedColor, settings=None):
        krita_instance = Krita.instance()
        notifier = krita_instance.notifier()
        notifier.setActive(True)

        self.__dock_widget = dock_widget
        self.__krita_instance = krita_instance

        self.__current_color = current_color
        self.__main_light = Light(q_to_managed_color(self.canvas, self.default_light_color))
        self.__ambient_light = Light(q_to_managed_color(self.canvas, self.default_ambient_color))

        self.__local_colors = []
        self.__exposure = 1.0

    @property
    def krita_instance(self):
        return self.__krita_instance

    @property
    def current_color(self) -> ManagedColor:
        return self.__current_color

    @current_color.setter
    def set_current_color(self, color: ManagedColor):
        self.__current_color = color

    @property
    def main_light(self) -> Light:
        return self.__main_light

    @main_light.setter
    def set_main_light(self, color: Light):
        self.__main_light = color

    @property
    def ambient_light(self) -> Light:
        return self.__ambient_light

    @ambient_light.setter
    def set_ambient_light(self, color: Light):
        self.__ambient_light = color

    @property
    def local_colors(self) -> list[QColor]:
        return self.__local_colors

    #TODO: temp
    @property
    def dock_widget(self) -> DockWidget:
        return self.__dock_widget

    @property
    def canvas(self) -> Canvas:
            return self.__dock_widget.canvas()

    def sync(self):
        canvas = self.canvas
        if canvas is None or canvas.view() is None:
            return

        active_view = self.krita_instance.activeWindow().activeView()
        color_fg = active_view.foregroundColor()
        color_bg = active_view.backgroundColor()

        self.set_current_color = color_fg

    def __get_color_idx(self, color: ManagedColor) -> int:
        colors = self.__local_colors
        for i, stored_color in enumerate(colors):
            r, g, b, a = stored_color.componentsOrdered()
            _r, _g, _b, _a = color.componentsOrdered()

            if (r == _r and g == _g and b == _b and a == _a):
                return i

        return -1

    def try_add_local_color(self) -> (ManagedColor, ManagedColor, ManagedColor):
        canvas = self.canvas
        if canvas is not None:
            managed_color = canvas.view().foregroundColor()
            if self.__get_color_idx(managed_color) == -1:
                self.__local_colors.append(managed_color)
                illuminated_color, shadow_color = self.get_mixed_colors(managed_color)

                return (managed_color, illuminated_color, shadow_color)
            else:
                raise ValueError('color already exists.')
        else:
            raise ValueError('no active canvas.')

    def try_remove_local_color(self, to_remove: ManagedColor):
        colors = self.__local_colors

        idx = self.__get_color_idx(to_remove)
        if idx == -1:
            raise ValueError("id not find in local_color list")

        if len(colors) > 1:
            colors[idx], colors[-1] = colors[-1], colors[idx]
        colors.pop()

    def try_set_foreground_color(self, color: ManagedColor) -> ManagedColor:
        canvas = self.canvas
        if canvas is not None:
            canvas.view().setForeGroundColor(color)
        else:
            raise ValueError('No active canvas')

    # color: QColor because color conversion between QColor and ManagedColor
    # shifts color drastically
    def get_mixed_colors(self, color: ManagedColor) -> (QColor, QColor):
        r, g, b, a = color.componentsOrdered()

        main_light = self.main_light
        ambient_light = self.ambient_light 

        l_r, l_g, l_b, l_a = main_light.color.componentsOrdered()
        a_r, a_g, a_b, a_a = ambient_light.color.componentsOrdered()

        #TODO: could assume new_color already influenced by ambient color?
        l_r, l_g, l_b = mix((r, g, b),(l_r, l_g, l_b), main_light.intensity)
        r, g, b = mix((r, g, b),(a_r, a_g, a_b), ambient_light.intensity)
        s_r, s_g, s_b = relative_color_shift((r, g, b), 0.0, 0.5)

        # color = QColor.fromRgbF(r, g, b, a)
        illuminated_color = copy_managed_color(color)
        illuminated_color.setComponents([l_b, l_g, l_r, a])

        shadow_color = copy_managed_color(color) 
        shadow_color.setComponents([s_b, s_g, s_r, a])

        return (illuminated_color, shadow_color)
