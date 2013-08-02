from core import Screen
from apps.dashboard import Dashboard
from apps.tutorials.lines import Line1
from apps.tutorials.rectangles import Rectangle1, Rectangle2, Rectangle3
from apps.tutorials.text import Text1, Text2

def get_apps(window):
    """
    Defines a single hello world sample application with the default SSVEP
    stimuli.
    """
    fullscreen = Screen(0, 0, window.width, window.height)
    dashboard = Dashboard(fullscreen)

    dashboard.attach(Line1(fullscreen.copy()))
    dashboard.attach(Rectangle1(fullscreen.copy()))
    dashboard.attach(Rectangle2(fullscreen.copy()))
    dashboard.attach(Rectangle3(fullscreen.copy()))
    dashboard.attach(Text1(fullscreen.copy()))
    dashboard.attach(Text2(fullscreen.copy()))

    return [dashboard]

if __name__ == '__main__':
    from core import viewport
    viewport.controller.set_apps(get_apps(viewport.window))
    viewport.start()