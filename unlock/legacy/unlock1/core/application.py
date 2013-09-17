import os
import inspect

class UnlockApplication(object):
    """Unlock Application base class

    :param screen: Screen to be passed to the app
    """

    name = "Unlock Application"
    gets_samples = False

    def __init__(self, screen):
        """__init__"""
        self.screen = screen
        self.controller = None
        self.parent = None
        self.apps = {}
        self.resource_path = os.path.dirname(
            inspect.getfile(self.__class__)) + '/resource/'

#    def draw(self):
#        """Draw"""
#        raise NotImplementedError(
#            "Unlock Applications must define the draw method")

    def update(self, dt, decision, selection):
        """Update: Unlock Applications must define the update method"""
        raise NotImplementedError(
            "Unlock Applications must define the update method")

    def sample(self, data):
        """Sample"""
        pass

    def attach(self, app):
        self.apps[app] = app
        app.parent = self
        self.on_attach(app)

    def open(self, app, **kwargs):
        #if self.controller and app in self.apps:
        if app is not None:
            self.controller.replace_app(self, app)
            app.on_open(kwargs)

    def close(self, **kwargs):
        #if self.controller and self.parent:
        if self.parent is not None:
            self.controller.replace_app(self, self.parent)
            self.parent.on_return(kwargs)

    def root(self):
        """
        Returns the root app associated with this app
        """
        app = self
        while app.parent is not None:
            app = app.parent
        return app


    def on_open(self, kwargs):
        """
        Called when the application is opened.
        """
        pass

    def on_return(self, kwargs):
        """
        Called when a parent receives control from a child app.
        """
        pass

    def on_attach(self, app):
        """
        Called when a child app is attached to this app.
        """
        pass

    def quit(self):
        """
        Called when the display is shutting down to enable graceful cleanup.
        """
        pass