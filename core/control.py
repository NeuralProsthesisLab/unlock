import unlock.core
import logging
from unlock.core.util import switch

class Controller(object):
    pass

class ControlManager(object):
    def __init__(self, logger, command_receiver, controllers):
        self.command_receiver = command_receiver
        self.set_apps(controllers)
        self.logger = logging.getLogger(type(self).__name__)
        self.override_key = None
        self.override_value = None        
    def set_apps(self, apps):
        self.apps = apps
        for app in apps:
            app.controller = self
    def replace_apps(self, old, new):
        self.apps.remove(old)
        self.apps.append(new)
        new.controller = self
    def stop(self):
        self.command_reciever.stop()
        for app in self.apps:
            app.root().stop()
    def command_override(self, key, value):
        self.override_key = key
        self.override_value = value
    def poll_for_next_command(self, delta_since_last_poll_mills):
        command = self.command_receiver.get_next_command()
        if self.override_key != None:
            for case in switch(self.override_key):
                if case('decision'):
                    command.decision = self.override_value
                    self.override_key = None
                    break
                if case('selection'):
                    command.selection = self.override_value
                    self.override_key = None                    
                    break
                if case():
                    logger.debug("Unsupported override key = ", self.override_key, " value = ", override_value)
                    
        for app in self.apps:
            app.update(command)
#            if app.gets_samples:
#                app.sample(data)

   # def draw(self):
   #     for app in self.apps:
   #         app.draw()
            
            