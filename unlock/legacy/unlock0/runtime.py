from core import Screen
from apps import Dashboard, HelloWorld
from stimuli import SSVEP, SSVEPStimulus

"""
Import settings and files from folders and initiate viewport.py


"""

def get_apps(window):
    """
    Partition screen into different sections. Add apps and stimuli to each section

    Viewport.py provides the total window size to this method. For this script, it is
    split into quadrants. Stimulus parameters are set. Then instance of app classes
    are called. Apps need to be chosen in import settings.
    """

    w2 = window.width / 2
    h2 = window.height / 2
#
    bottom_left = Screen(0, 0, w2, h2)
    bottom_right = Screen(w2, 0, w2, h2)
    top_left = Screen(0, h2, w2, h2)
    top_right = Screen(w2, h2, w2, h2)
    full = Screen(0,0,window.width,window.height)

#    freqs = [11.5,12.0,12.5,13.0,13.5,
#             14.0,14.5,15.0,15.5,16.0]

#    stim_freq = 10
#    stim_size = 300
#    stimuli = [
#        SSVEPStimulus(full, 12.0, 'center', width=stim_size,
#                      height=stim_size, x_freq=stim_freq, y_freq=stim_freq),
#        ]
    app1 = HelloWorld(bottom_left)
#    #app1 = SSVEP(bottom_left, stimuli, rest_length=0)
#
    app2 = HelloWorld(bottom_right)
#    #app2 = SpectrumScope(bottom_right, freqs, numchan=1, debug=False)
#    #app2 = TimeScope(bottom_right, numchan=1)
#
    app3 = HelloWorld(top_right)
#    #app3 = TimeScope(top_right, numchan=3, debug=True)
#    #app3 = BCIRemote(top_right)
#
    app4 = HelloWorld(top_left)
#    #app4 = FreqButton(top_left, freqs, app1 ,app2)
#
#    #return [SSVEP(full, stimuli, rest_length=0)]
#    return [app1, app2, app3, app4]
    app = Dashboard(full)
    app.attach(app1)
    app.attach(app2)
    app.attach(app3)
    app.attach(app4)
    return [app]

if __name__ == '__main__':
    from core import viewport
    viewport.controller.set_apps(get_apps(viewport.window))
    viewport.start()