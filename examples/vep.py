# Unlock project runtime script
from core import Screen
from apps.dashboard import Dashboard
from apps.stimuli.ssvep import SSVEP, SSVEPStimulus
import numpy as np

def get_apps(window):
    """
    Examples of the various visual evoked potential paradigms
    """
    fullscreen = Screen(0, 0, window.width, window.height)
    dashboard = Dashboard(fullscreen)

    size = 200
    offset = size + 100
    sfreq = 4

    ## frequency VEP
    ## distinct, fixed frequency stimuli
    fscreen = fullscreen.copy()
    fstims = [
        SSVEPStimulus(fscreen, 8.0, 'center', width=size, height=size,
            x_freq=sfreq, y_freq=sfreq, y_offset=offset),
        SSVEPStimulus(fscreen, 9.0, 'center', width=size, height=size,
            x_freq=sfreq, y_freq=sfreq, y_offset=-offset),
        SSVEPStimulus(fscreen, 10.0, 'center', width=size, height=size,
            x_freq=sfreq, y_freq=sfreq, x_offset=-offset),
        SSVEPStimulus(fscreen, 11.0, 'center', width=size, height=size,
            x_freq=sfreq, y_freq=sfreq, x_offset=offset),
    ]
    fVEP = SSVEP(fscreen, fstims, rest_length=0)
    fVEP.name = 'f-VEP'

    ## phase VEP
    ## common frequency, distinct phase offset stimuli
    pscreen = fullscreen.copy()
    pstims = [
        SSVEPStimulus(pscreen, 30.0, 'center', width=size, height=size,
            x_freq=sfreq, y_freq=sfreq, y_offset=offset,
            sequence=(1,1,1,1,1,1,0,0,0,0,0,0)),
        SSVEPStimulus(pscreen, 30.0, 'center', width=size, height=size,
            x_freq=sfreq, y_freq=sfreq, y_offset=-offset,
            sequence=(0,0,1,1,1,1,1,1,0,0,0,0)),
        SSVEPStimulus(pscreen, 30.0, 'center', width=size, height=size,
            x_freq=sfreq, y_freq=sfreq, x_offset=-offset,
            sequence=(0,0,0,0,1,1,1,1,1,1,0,0)),
        SSVEPStimulus(pscreen, 30.0, 'center', width=size, height=size,
            x_freq=sfreq, y_freq=sfreq, x_offset=offset,
            sequence=(0,0,0,0,0,0,1,1,1,1,1,1)),
    ]
    pVEP = SSVEP(pscreen, pstims, rest_length=0)
    pVEP.name = 'p-VEP'

    ## time VEP
    ## common frequency, distinct appearance stimuli
    tscreen = fullscreen.copy()
    tstims = [
        SSVEPStimulus(tscreen, 4.0, 'center', width=size, height=size,
            x_freq=sfreq, y_freq=sfreq, y_offset=offset,
            sequence=(1,0,0,0,0,1,0,0,0,0,1,0)),
        SSVEPStimulus(tscreen, 4.0, 'center', width=size, height=size,
            x_freq=sfreq, y_freq=sfreq, y_offset=-offset,
            sequence=(0,0,1,0,0,0,1,0,0,0,0,1)),
        SSVEPStimulus(tscreen, 4.0, 'center', width=size, height=size,
            x_freq=sfreq, y_freq=sfreq, x_offset=-offset,
            sequence=(0,1,0,0,1,0,0,0,1,0,0,0)),
        SSVEPStimulus(tscreen, 4.0, 'center', width=size, height=size,
            x_freq=sfreq, y_freq=sfreq, x_offset=offset,
            sequence=(0,0,0,1,0,0,0,1,0,1,0,0)),
    ]
    tVEP = SSVEP(tscreen, tstims, rest_length=0)
    tVEP.name = 't-VEP'

    ## code VEP (phase)
    ## common m-sequence, distinct phase offset stimuli
    cscreen = fullscreen.copy()
    msequence = np.array((1, 0, 0, 1, 0, 1, 1, 0, 1, 1,
                1, 0, 1, 1, 0, 0, 1, 1, 0, 1,
                0, 1, 0, 1, 1, 1, 1, 1, 1, 0,
                0, 0, 0, 0, 1, 0, 0, 0, 0, 1,
                1, 0, 0, 0, 1, 0, 1, 0, 0, 1,
                1, 1, 1, 0, 1, 0, 0, 0, 1, 1,
                1, 0, 0))
    cstims = [
        SSVEPStimulus(cscreen, 30.0, 'center', width=size, height=size,
            x_freq=sfreq, y_freq=sfreq, y_offset=offset,
            filename_reverse=True, sequence=msequence),
        SSVEPStimulus(cscreen, 30.0, 'center', width=size, height=size,
            x_freq=sfreq, y_freq=sfreq, y_offset=-offset,
            filename_reverse=True, sequence=np.roll(msequence, 15)),
        SSVEPStimulus(cscreen, 30.0, 'center', width=size, height=size,
            x_freq=sfreq, y_freq=sfreq, x_offset=-offset,
            filename_reverse=True, sequence=np.roll(msequence, 30)),
        SSVEPStimulus(cscreen, 30.0, 'center', width=size, height=size,
            x_freq=sfreq, y_freq=sfreq, x_offset=offset,
            filename_reverse=True, sequence=np.roll(msequence, 45)),
    ]
    cVEP = SSVEP(cscreen, cstims, rest_length=0)
    cVEP.name = 'cp-VEP'

    ## code VEP (entropy)
    ## distinct m-sequence stimuli
    cescreen = fullscreen.copy()
    cestims = [
        SSVEPStimulus(cescreen, 30.0, 'center', width=size, height=size,
            x_freq=sfreq, y_freq=sfreq, y_offset=offset, filename_reverse=True,
            sequence=(1,0,1,0,1,0,0,0,0,0,1,0,1,1,0,1,0,0,1,0,1,1,1,1,1,1,0,0,0,1,1)),
        SSVEPStimulus(cescreen, 30.0, 'center', width=size, height=size,
            x_freq=sfreq, y_freq=sfreq, y_offset=-offset, filename_reverse=True,
            sequence=(0,0,1,1,1,0,0,1,0,1,0,1,0,0,0,0,1,0,1,1,0,0,1,1,1,1,1,1,0,0,1)),
        SSVEPStimulus(cescreen, 30.0, 'center', width=size, height=size,
            x_freq=sfreq, y_freq=sfreq, x_offset=-offset, filename_reverse=True,
            sequence=(0,0,0,1,1,0,1,1,1,0,1,0,1,0,1,1,1,0,0,0,1,0,1,1,1,0,0,1,1,0,0)),
        SSVEPStimulus(cescreen, 30.0, 'center', width=size, height=size,
            x_freq=sfreq, y_freq=sfreq, x_offset=offset, filename_reverse=True,
            sequence=(0,1,0,1,1,1,1,0,0,1,0,1,1,1,0,1,1,1,1,1,1,0,1,1,0,1,0,0,1,1,0)),
    ]
    ceVEP = SSVEP(cescreen, cestims, rest_length=0)
    ceVEP.name = 'ce-VEP'

    dashboard.attach(ceVEP)
    dashboard.attach(pVEP)
    dashboard.attach(fVEP)
    dashboard.attach(tVEP)
    dashboard.attach(cVEP)

    return [dashboard]

if __name__ == '__main__':
    from core import viewport
    # Uncomment the following line to see the rate of frames per second.
    viewport.show_fps = True
    viewport.controller.set_apps(get_apps(viewport.window))
    viewport.start()
