try:
    from PyQt6.QtGui import QColor
    from PyQt5.QtWidgets import QLayout
except:
    from PyQt5.QtGui import QColor
    from PyQt5.QtWidgets import QLayout

from krita import ManagedColor, Canvas
import time

class UnimplementedError(Exception):
    pass

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

    return ManagedColor(color_model, color_depth, color_profile)

def delete_layout(layout: QLayout):
    while layout.count():
        child = layout.takeAt(0)
        widget = child.widget()
        if widget:
            widget.deleteLater()
