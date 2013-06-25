from core import Screen
from core import PygletWindow
from time_scope import TimeScope
from frequency import SpectrumScope
from selector import FreqButton
from ssvep import SSVEP, SSVEPStimulus

def get_apps(window):
    """Retrieves apps for viewport

    Partitions window into sections. Apps and stimuli are added to each section

    :param window: window to use to display apps
    """
    w2 = window.width / 2       #Half the width
    h2 = window.height / 2      #Half the height

    # split the screen into quadrants
    bottom_left = Screen(0, 0, w2, h2)
    bottom_right = Screen(w2, 0, w2, h2)
    top_left = Screen(0, h2, w2, h2)
    top_right = Screen(w2, h2, w2, h2)

    freqs = [11.5,12.0,12.5,13.0,13.5,  #Stimulating frequencies
             14.0,14.5,15.0,15.5,16.0]

    #the decoder to be used on the frequency scope
    debug   = True
    fs      = 256       #sampling frequency
    dur     = 2         #length of sampling time
    numchan = 3         #number of recording channels
    #decoder = fft_Decoder(fs ,dur, freqs, ffWin=0.1, h1Win=0.1, lpass=8.0, hpass=34.0)

    stim_freq = 10      #Number of checks on one edge
    stim_size = 300     #Size of stimulus in pixels
    stimuli = [
        SSVEPStimulus(bottom_left, 12.0, 'center', width=stim_size,
            height=stim_size, x_freq=stim_freq, y_freq=stim_freq),
        ]
    ssvep = SSVEP(bottom_left, stimuli, rest_length=0)
    frequency_scope = SpectrumScope(bottom_right, numchan=numchan, dur=dur,
        debug=debug)
    time_scope = TimeScope(top_right, numchan=numchan, debug=debug)
    selector = FreqButton(top_left, freqs, ssvep, frequency_scope)

    return [selector, ssvep, time_scope, frequency_scope]

if __name__ == '__main__':
    window = PygletWindow()
    window.controller.apps = get_apps(window)
    window.start()