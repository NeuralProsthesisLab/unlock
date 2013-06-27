import unlock_core.CommandReceiverInterface
import util.switch

class Controller(object):
    pass

class ControlManager(object):
    """
    Handles the import of data and sends the decisions and selections to the update methods of each app
    """
    def __init__(self, command_receiver, controllers):
        self.override_key = None
        self.override_value = None
        self.set_apps(controllers)
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
            app.root().quit()
    def command_override(self, key, value):
        self.override_key = key
        self.override_value = value
    def poll_for_next_command(self, delta_since_last_poll_mills):
        check_for_override()
        decision, selection, data = self.command_receiver.get_next_command()
        if self.override_key != None:
            for case in switch(self.override_key):
                if case('decision'):
                    decision = self.override_value
                    self.override_key = None
                    break
                if case('selection'):
                    selection = self.override_value
                    self.override_key = None                    
                    break
                if case():
                    logger.debug("Unsupported override key = ", self.override_key, " value = ", override_value)
                    data = self.override_value
                    
        for app in self.apps:
            app.update(delta_since_last_poll_mills, decision, selection)
            if app.gets_samples:
                app.sample(data)

   # def draw(self):
   #     for app in self.apps:
   #         app.draw()
            
            