from core import Screen
from apps.tutorials import HelloWorld
from apps.stimuli.ssvep import DefaultSSVEP

def get_apps(window):
    """
    Defines a single hello world sample application with the default SSVEP
    stimuli.
    """
    fullscreen = Screen(0, 0, window.width, window.height)
    ssvep = DefaultSSVEP(fullscreen)

    app_screen = Screen(100, 100, window.width - 200, window.height - 200)
    hw = HelloWorld(app_screen)

    return [ssvep, hw]

if __name__ == '__main__':
    from core import viewport
    viewport.controller.set_apps(get_apps(viewport.window))
    viewport.start()