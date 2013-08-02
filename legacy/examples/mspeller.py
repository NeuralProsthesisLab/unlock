from core import Screen
from apps.mspeller import MSpeller


def get_apps(window):
    """
    An m-sequence speller app based on Spuler et al. (2012).
    """
    fullscreen = Screen(0, 0, window.width, window.height)
    labels = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ_12345'
    sequence = (1, 0, 0, 1, 0, 1, 1, 0, 1, 1,
                1, 0, 1, 1, 0, 0, 1, 1, 0, 1,
                0, 1, 0, 1, 1, 1, 1, 1, 1, 0,
                0, 0, 0, 0, 1, 0, 0, 0, 0, 1,
                1, 0, 0, 0, 1, 0, 1, 0, 0, 1,
                1, 1, 1, 0, 1, 0, 0, 0, 1, 1,
                1, 0, 0)
    mseq = MSpeller(fullscreen, 4, 8, labels, sequence)
    return [mseq]

if __name__ == '__main__':
    from core import viewport
    viewport.controller.set_apps(get_apps(viewport.window))
    viewport.window.set_vsync(True)
    viewport.start()