# Unlock project runtime script
from core import Screen
from apps.stimuli.ssvep import SSVEP, SSVEPStimulus

def get_apps(window):
    ssvep_screen = Screen(0, 0, window.width, window.height)
    stimuli = [
        SSVEPStimulus(ssvep_screen, 15.0, 'center', width=200, height=200,
            x_freq=4, y_freq=4, filename_reverse=True, y_offset=100, x_offset=100,
            sequence=(1,1,1,0,1,0,1,0,0,0,0,1,0,0,1,0,1,1,0,0,1,1,1,1,1,0,0,0,1,1,0)),
        SSVEPStimulus(ssvep_screen, 15.0, 'center', width=200, height=200,
            x_freq=4, y_freq=4, filename_reverse=True, y_offset=100, x_offset=-100,
            sequence=(0,1,1,1,0,1,0,1,0,0,1,0,0,0,0,0,1,1,1,1,1,1,1,0,1,0,1,1,0,1,1)),
        SSVEPStimulus(ssvep_screen, 15.0, 'center', width=200, height=200,
            x_freq=4, y_freq=4, filename_reverse=True, y_offset=-100, x_offset=100,
            sequence=(0,1,0,0,0,1,0,1,0,0,1,0,1,1,0,0,1,0,1,0,0,1,0,0,0,1,0,0,1,1,0)),
        SSVEPStimulus(ssvep_screen, 15.0, 'center', width=200, height=200,
            x_freq=4, y_freq=4, filename_reverse=True, y_offset=-100, x_offset=-100,
            sequence=(0,0,1,1,0,0,0,1,1,0,1,0,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,0,0,0,0))
    ]
    ssvep = SSVEP(ssvep_screen, stimuli, rest_length=0)
    # Uncomment the following line to turn off the flickering stimuli.
    #ssvep.stop()

    return [ssvep]

if __name__ == '__main__':
    from core import viewport
    # Uncomment the following line to see the rate of frames per second.
    # viewport.show_fps = True
    viewport.controller.set_apps(get_apps(viewport.window))
    viewport.start()