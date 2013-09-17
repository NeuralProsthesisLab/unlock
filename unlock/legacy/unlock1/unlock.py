# Unlock project runtime script
from core import Screen
from apps.dashboard import Dashboard
from apps.stimuli.ssvep import DefaultSSVEP

def get_apps(window):
    """
    The standard Unlock runtime consists of the default four-choice SSVEP
    stimuli and the dashboard. User apps are attached to the dashboard and then
    selected from the initial view.
    """
    ssvep_screen = Screen(0, 0, window.width, window.height)
    ssvep = DefaultSSVEP(ssvep_screen)
    # Uncomment the following line to turn off the flickering stimuli.
    #ssvep.stop()

    dashboard_screen = Screen(100, 100, window.width-200, window.height-200)
    dashboard = Dashboard(dashboard_screen)
    # for each app you want to add:
    #  1. define the screen space it will need
    #  2. create an instance of the app
    #  3. attach the app to the dashboard
    #
    # app_screen = Screen(left_x, bottom_y, width, height)
    # app = MyApp(app_screen)
    # dashboard.attach(app)

    return [ssvep, dashboard]

if __name__ == '__main__':
    from core import viewport
    # Uncomment the following line to see the rate of frames per second.
    #viewport.show_fps = True
    viewport.controller.set_apps(get_apps(viewport.window))
    viewport.start()