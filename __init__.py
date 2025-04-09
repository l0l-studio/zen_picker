from krita import DockWidgetFactory, DockWidgetFactoryBase, Krita
from .zen_picker import ZenDocker


DOCKER_ID = "zen_picker"
instance = Krita.instance()
dock_widget_factory = DockWidgetFactory(
    DOCKER_ID, DockWidgetFactoryBase.DockRight, ZenDocker
)

instance.addDockWidgetFactory(dock_widget_factory)
