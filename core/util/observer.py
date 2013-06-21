import dispatcher

class Observable(object):
    def __init__(self, notification_keywords):
        self.dispatcher = dispatcher.Signal(providing_args=notification_keywords)
    def register_observers(self, *observers):
        print observers
        for observer in observers:
            self.dispatcher.connect(observer.notify)
    def send_notification(self, **kwargs):
        self.dispatcher.send(sender=self, **kwargs)

class AbstractObserver(object):
    def __init__(self):
        pass
    def notify(self, **view_specific_kwargs):
        raise TypeError('Abstract method '+self._class.__name__+'.notify() cannot be called')
    
