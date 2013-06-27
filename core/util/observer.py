import dispatcher

class Observable(object):
    def __init__(self, *notification_keywords):
        self.dispatcher = dispatcher.Signal(providing_args=notification_keywords)
    def register_observers(self, *observers):
        for observer in observers:
            issubclass(observer,Observer)
            self.dispatcher.connect(observer.notify)
    def send_notification(self, **kwargs):
        self.dispatcher.send(sender=self, **kwargs)
        
        
class Observer(object):
    def __init__(self, callout_fn):
        self.callout_fn = callout_fn
    def notify(self, **kwargs):
        self.callout_fn(**kwargs)
        
        
class Connection(object):
    def __init__(self, endpoint, *callback_fns):
        assert issubclass(endpoint, Observer)
        self.observable = Observable(callback_fns)
        self.endpoint = endpoint
        self.observable.register_observers(self.endpoint)
    def send_message(self, **kwargs):
        self.observable.send_notification(kwargs)