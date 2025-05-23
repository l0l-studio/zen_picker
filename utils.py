try:
    from PyQt6.QtGui import QColor
    from PyQt5.QtWidgets import QLayout
except:
    from PyQt5.QtGui import QColor
    from PyQt5.QtWidgets import QLayout

from typing import Union
import time
from krita import ManagedColor, Canvas

from .lib_zen import mix, relative_color_shift

class UnimplementedError(Exception):
    pass

class Light():
    def __init__(self, color: ManagedColor, intensity: float = 0.1):
        self.__color = color
        self.__intensity = intensity

    @property
    def color(self) -> ManagedColor:
        return self.__color

    @color.setter
    def color(self, color: ManagedColor):
        self.__color = color

    @property
    def intensity(self) -> float:
        return self.__intensity

    @intensity.setter
    def set_intensity(self, intensity: float):
        self.__intensity = intensity

# https://gist.github.com/kylebebak/ee67befc156831b3bbaa88fb197487b0
# TODO: debounce severs link to class instance
def debounce(s):
    """Decorator ensures function that can only be called once every `s` seconds.
    """
    def decorate(f):
        t = None

        def wrapped(*args, **kwargs):
            nonlocal t
            t_ = time.time()
            if t is None or t_ - t >= s:
                result = f(*args, **kwargs)
                t = time.time()
                return result
        return wrapped
    return decorate

def parse_color(array):
    color = ManagedColor(array[0], array[1], array[2])
    color.setComponents([float(x) for x in array[3:]])
    return color

def q_to_managed_color(canvas: Canvas, qcolor: QColor):
    return ManagedColor.fromQColor(qcolor, canvas)

def managed_to_q_color(canvas: Canvas, managedcolor: ManagedColor):
    return managedcolor.colorForCanvas(canvas)

def copy_managed_color(color: ManagedColor) -> ManagedColor:
    color_model = color.colorModel()
    color_depth = color.colorDepth()
    color_profile = color.colorProfile()

    new = ManagedColor(color_model, color_depth, color_profile)
    comps = get_managed_color_comps(color)

    new = set_managed_color_comps(new, comps)
    return new

def get_managed_color_comps(color: ManagedColor) -> list[float]:
    r, g, b, a = color.componentsOrdered()
    return [r, g, b, a]

def set_managed_color_comps(color: ManagedColor, comps: list[float]) -> ManagedColor:
    r, g, b, a = comps
    color.setComponents([b, g, r, a])
    return color

def delete_layout(layout: QLayout):
    while layout.count():
        child = layout.takeAt(0)
        widget = child.widget()
        if widget:
            widget.deleteLater()


def get_color_idx(color: ManagedColor, colors: list[ManagedColor]) -> int:
    for i, stored_color in enumerate(colors):
        r, g, b, a = stored_color.componentsOrdered()
        _r, _g, _b, _a = color.componentsOrdered()

        if (r == _r and g == _g and b == _b and a == _a):
            return i

    return -1


def get_mixed_colors(
    color: ManagedColor, 
    lights: (Light, Light),
    components: bool = False,
    bgr: bool = True
) -> (Union[QColor, list[float]], Union[QColor, list[float]]):
    r, g, b, a = color.componentsOrdered()

    main_light, ambient_light = lights

    l_r, l_g, l_b, l_a = main_light.color.componentsOrdered()
    a_r, a_g, a_b, a_a = ambient_light.color.componentsOrdered()

    #TODO: could assume new_color already influenced by ambient color?

    #TODO: only mix hue
    l_r, l_g, l_b = mix((r, g, b),(l_r, l_g, l_b), main_light.intensity)
    r, g, b = mix((r, g, b),(a_r, a_g, a_b), ambient_light.intensity)
    s_r, s_g, s_b = relative_color_shift((r, g, b), 0.0, 0.2)

    if components:
        return ([l_b, l_g, l_r, a], [s_b, s_g, s_r, a]) if bgr else ([l_r, l_g, l_b, a], [s_r, s_g, s_b, a])

    illuminated_color = copy_managed_color(color)
    illuminated_color.setComponents([l_b, l_g, l_r, a])

    shadow_color = copy_managed_color(color) 
    shadow_color.setComponents([s_b, s_g, s_r, a])

    return (illuminated_color, shadow_color)
