import os
import inspect
from unlock.core.util import observer

    
class UnlockApplication(object):
    """Unlock Application base class

    :param screen: Screen to be passed to the app
    """

    name = "Unlock Application"
    gets_samples = False

    def __init__(self, screen, resource=Resource()):
        """__init__"""
        self.screen = screen
        self.resource = resource
        self.observer = observer.Observer(self.__notify__)
        self.children = []
        self.resource = resource
        self.parent = None
    def __notify__(self, **kwargs):
        assert kwargs.has_key('cmd')
        if kwargs['cmd'] == 'on_attach':
            assert kwargs.has_key('parent')
            onattach = getattr(self, kwargs['cmd'])
            onattach(kwargs['parent'])
        elif kwargs['cmd'] == 'on_return':
            onattach = getattr(self, kwargs['cmd'])
            onattach(kwargs)
        
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
        c = Connection(app, 'cmd', 'parent')
        self.children.append(c)
        c.send_message(cmd='on_attach', parent=self)
        
    #def attach(self, app):
    #    self.apps[app] = app
    #    app.parent = self
    #    self.on_attach(app)

    # WTF?
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

    def on_attach(self, parent):
        self.parent = parent
        self.parent_conn = Connection(parent)

    def quit(self):
        """
        Called when the display is shutting down to enable graceful cleanup.
        """
        pass