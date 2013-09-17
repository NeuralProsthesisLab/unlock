from core import Screen
from apps import HelloWorld

def get_apps(window):
    full_screen = Screen(0, 0, window.width,window.height)
#    stimuli = [
#        SSVEPStimulus(full_screen, 12.0, 'north'),
#        SSVEPStimulus(full_screen, 13.0, 'south'),
#        SSVEPStimulus(full_screen, 14.0, 'west', rotation=90),
#        SSVEPStimulus(full_screen, 15.0, 'east', rotation=90),
#        ]
#    ssvep = SSVEP(full_screen, stimuli)

#    app_screen = Screen(100, 100, window.width - 200, window.height - 200)

    #robot = RobotDriver(app_screen, 'demo')
    #grid = GridHierarchyExperimentNoText(app_screen,'','')
    #scope = TimeScope(full_screen, numchan=3, labels=['O1','Oz','O2'])

    app = HelloWorld(full_screen)
    return [app]#[ssvep, grid]


if __name__ == '__main__':
    from core import viewport
    viewport.controller.apps = get_apps(viewport.window)
    viewport.start()